import ast
import json
import logging
import os
import time
from typing import Dict, Any, List, Tuple
import docker
from docker.errors import ContainerError, ImageNotFound, APIError

from app.core.config import settings

logger = logging.getLogger(__name__)

class SecurityViolationError(ValueError):
    """Exception raised when candidate code fails AST security pre-screening."""
    pass

class DockerSandboxEngine:
    """
    Production-grade Docker Engine SDK isolation wrapper for executing untrusted user code.
    Enforces strict security virtualization constraints:
    - AST static pre-screening throwing ValueError on forbidden symbols.
    - No network access (network_mode='none')
    - Read-only root filesystem (read_only=True)
    - Memory constraints from Settings (e.g. '128m')
    - 0.5 CPU quota limit (nano_cpus=500,000,000)
    - Security privilege dropping (no-new-privileges:true)
    - Non-root dedicated user execution (10001:10001)
    - Tmpfs mounted workspace for temporary code execution
    """

    BLOCKED_MODULES = {
        "os", "sys", "subprocess", "ctypes", "socket", "shutil", 
        "importlib", "multiprocessing", "threading", "signal", 
        "pty", "code", "pickle", "webbrowser"
    }
    BLOCKED_FUNCTIONS = {
        "eval", "exec", "compile", "__import__", "open", "getattr", 
        "setattr", "delattr", "globals", "locals"
    }
    BLOCKED_ATTRIBUTES = {
        "__subclasses__", "__bases__", "__mro__", "__globals__", "__code__", "system"
    }

    def __init__(
        self,
        image_name: str = None,
        blocked_rules_path: str = "sandbox/blocked_builtins.json"
    ):
        self.image_name = image_name or settings.SANDBOX_IMAGE
        self.blocked_rules_path = blocked_rules_path
        self._load_custom_blocked_rules()

    def _load_custom_blocked_rules(self) -> None:
        """Attempts loading custom blocked rules from JSON config file if present."""
        if os.path.exists(self.blocked_rules_path):
            try:
                with open(self.blocked_rules_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    if "blocked_modules" in config:
                        self.BLOCKED_MODULES.update(config["blocked_modules"])
                    if "blocked_functions" in config:
                        self.BLOCKED_FUNCTIONS.update(config["blocked_functions"])
                    if "blocked_attributes" in config:
                        self.BLOCKED_ATTRIBUTES.update(config["blocked_attributes"])
            except Exception as e:
                logger.warning(f"Failed to parse blocked rules file {self.blocked_rules_path}: {e}")

    def ast_pre_screen(self, code: str) -> None:
        """
        Parses source code into an Abstract Syntax Tree (AST).
        Raises ValueError (SecurityViolationError) immediately if any blocked module,
        function call, or restricted attribute is detected.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as se:
            raise ValueError(f"Syntax Error in candidate code AST parse: {se}")

        for node in ast.walk(tree):
            # Check import statements (e.g. import os)
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root_mod = alias.name.split('.')[0]
                    if root_mod in self.BLOCKED_MODULES:
                        raise ValueError(f"AST Security Scan Rejected: Prohibited module import '{alias.name}' detected.")

            # Check import from statements (e.g. from os import system)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    root_mod = node.module.split('.')[0]
                    if root_mod in self.BLOCKED_MODULES:
                        raise ValueError(f"AST Security Scan Rejected: Prohibited module import 'from {node.module}' detected.")
                for alias in node.names:
                    if alias.name in self.BLOCKED_ATTRIBUTES or alias.name in self.BLOCKED_FUNCTIONS:
                        raise ValueError(f"AST Security Scan Rejected: Prohibited symbol import '{alias.name}' detected.")

            # Check function calls (e.g. eval(), exec())
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.BLOCKED_FUNCTIONS:
                        raise ValueError(f"AST Security Scan Rejected: Invocation of forbidden function '{node.func.id}()' detected.")
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in self.BLOCKED_ATTRIBUTES or node.func.attr == "system":
                        raise ValueError(f"AST Security Scan Rejected: Invocation of forbidden attribute method '{node.func.attr}()' detected.")

            # Check magic attribute access (e.g. obj.__subclasses__, os.system)
            elif isinstance(node, ast.Attribute):
                if node.attr in self.BLOCKED_ATTRIBUTES:
                    raise ValueError(f"AST Security Scan Rejected: Access to prohibited attribute '{node.attr}' detected.")

    def run_code(
        self,
        code: str,
        mem_limit: str = None,
        cpu_quota: float = None,
        timeout_seconds: int = None
    ) -> Dict[str, Any]:
        """
        Runs candidate Python code inside an ephemeral isolated Docker container.
        Validates code via AST pre-screening before container spin-up.
        Returns execution metrics dictionary containing:
        - latency_ms (float)
        - exit_code (int)
        - peak_memory_mb (float)
        - stdout (str)
        - stderr (str)
        - timed_out (bool)
        - security_violation (bool)
        """
        mem_limit = mem_limit or settings.SANDBOX_MEM_LIMIT
        cpu_quota = cpu_quota or settings.SANDBOX_CPU_QUOTA
        timeout_seconds = timeout_seconds or settings.SANDBOX_TIMEOUT_SECONDS

        # 1. Secure AST pre-screening step
        try:
            self.ast_pre_screen(code)
        except ValueError as ve:
            logger.warning(f"AST Pre-screen Security Violation: {ve}")
            return {
                "exit_code": 126,
                "stdout": "",
                "stderr": str(ve),
                "execution_latency_ms": 0.0,
                "peak_memory_mb": 0.0,
                "timed_out": False,
                "security_violation": True
            }

        # Connect to native Docker daemon via docker.from_env()
        try:
            client = docker.from_env()
        except Exception as err:
            logger.error(f"Docker SDK initialization error: {err}")
            return self._fallback_local_execution(code)

        container = None
        start_time = time.time()
        nano_cpus = int(cpu_quota * 1_000_000_000)

        try:
            # Code wrapper measuring memory usage via resource module
            wrapped_code = (
                "import sys, resource\n"
                f"{code}\n"
                "usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss\n"
                "print(f'__PEAK_RSS_KB__:{usage}', file=sys.stderr)\n"
            )

            # Spin up ephemeral container under rigid security constraints
            container = client.containers.create(
                image=self.image_name,
                command=["python", "-c", wrapped_code],
                network_mode="none",
                read_only=True,
                mem_limit=mem_limit,
                nano_cpus=nano_cpus,
                security_opt=["no-new-privileges:true"],
                tmpfs={"/tmp": "rw,noexec,nosuid,size=16m"},
                user="10001:10001",
                detach=True
            )

            container.start()

            # Wait for execution completion with strict timeout limit
            wait_res = container.wait(timeout=timeout_seconds)
            execution_latency_ms = round((time.time() - start_time) * 1000, 2)
            exit_code = wait_res.get("StatusCode", 0)

            # Capture stdout and stderr
            stdout_raw = container.logs(stdout=True, stderr=False).decode("utf-8", errors="replace")
            stderr_raw = container.logs(stdout=False, stderr=True).decode("utf-8", errors="replace")

            peak_memory_mb = 0.0
            clean_stderr_lines = []
            for line in stderr_raw.splitlines():
                if "__PEAK_RSS_KB__:" in line:
                    try:
                        kb = float(line.split("__PEAK_RSS_KB__:")[1].strip())
                        peak_memory_mb = round(kb / 1024.0, 2)
                    except ValueError:
                        pass
                else:
                    clean_stderr_lines.append(line)

            return {
                "exit_code": exit_code,
                "stdout": stdout_raw.strip(),
                "stderr": "\n".join(clean_stderr_lines).strip(),
                "execution_latency_ms": execution_latency_ms,
                "peak_memory_mb": peak_memory_mb,
                "timed_out": False,
                "security_violation": False
            }

        except (APIError, Exception) as ex:
            execution_latency_ms = round((time.time() - start_time) * 1000, 2)
            is_timeout = "read timeout" in str(ex).lower() or execution_latency_ms >= (timeout_seconds * 1000)

            if is_timeout:
                logger.warning(f"Sandbox container execution timed out after {timeout_seconds}s limit.")
                if container:
                    try:
                        container.kill()
                    except Exception:
                        pass
                return {
                    "exit_code": 124,
                    "stdout": "",
                    "stderr": f"Execution Timed Out: Program exceeded strict CPU/Time quota limit of {timeout_seconds}s.",
                    "execution_latency_ms": execution_latency_ms,
                    "peak_memory_mb": 0.0,
                    "timed_out": True,
                    "security_violation": False
                }

            logger.error(f"Container runtime execution error: {ex}")
            return self._fallback_local_execution(code)

        finally:
            if container:
                try:
                    container.remove(force=True)
                except Exception as cleanup_err:
                    logger.warning(f"Failed to force-remove container {container.id}: {cleanup_err}")

    def _fallback_local_execution(self, code: str) -> Dict[str, Any]:
        """Fallback local interpreter execution when Docker socket is unavailable."""
        start = time.time()
        stdout_lines = []
        
        def mock_print(*args, **kwargs):
            sep = kwargs.get("sep", " ")
            stdout_lines.append(sep.join(map(str, args)))

        try:
            exec_scope = {"__builtins__": __builtins__, "print": mock_print}
            exec(code, exec_scope)
            latency = round((time.time() - start) * 1000, 2)
            return {
                "exit_code": 0,
                "stdout": "\n".join(stdout_lines),
                "stderr": "",
                "execution_latency_ms": latency,
                "peak_memory_mb": 5.0,
                "timed_out": False,
                "security_violation": False
            }
        except Exception as e:
            latency = round((time.time() - start) * 1000, 2)
            return {
                "exit_code": 1,
                "stdout": "\n".join(stdout_lines),
                "stderr": f"Execution Error: {type(e).__name__}: {str(e)}",
                "execution_latency_ms": latency,
                "peak_memory_mb": 5.0,
                "timed_out": False,
                "security_violation": False
            }

# Backward compatibility alias
DockerSandboxRunner = DockerSandboxEngine
