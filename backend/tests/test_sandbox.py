import unittest

try:
    from app.pipeline.sandbox import DockerSandboxEngine
    HAS_SANDBOX = True
except ImportError:
    HAS_SANDBOX = False

class TestDockerSandboxEngine(unittest.TestCase):

    def setUp(self):
        if HAS_SANDBOX:
            self.engine = DockerSandboxEngine(
                image_name="multi-agent-exam-portal-sandbox:latest",
                blocked_rules_path="sandbox/blocked_builtins.json"
            )

    @unittest.skipUnless(HAS_SANDBOX, "Docker SDK package not installed in local environment")
    def test_01_ast_pre_screen_safe_code(self):
        code = 'print("Hello Sandbox")'
        # AST pre screen should not raise ValueError
        self.engine.ast_pre_screen(code)

    @unittest.skipUnless(HAS_SANDBOX, "Docker SDK package not installed in local environment")
    def test_02_ast_pre_screen_blocked_import(self):
        code = 'import subprocess\nsubprocess.run(["ls"])'
        with self.assertRaises(ValueError):
            self.engine.ast_pre_screen(code)

    @unittest.skipUnless(HAS_SANDBOX, "Docker SDK package not installed in local environment")
    def test_03_ast_pre_screen_dangerous_builtin(self):
        code = 'x = eval("1 + 1")'
        with self.assertRaises(ValueError):
            self.engine.ast_pre_screen(code)

if __name__ == "__main__":
    unittest.main()
