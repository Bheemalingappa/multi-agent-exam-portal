# Security Controls Specification

## 1. Input Sanitization & Payload Size Caps
- **Source Code Payload**: Maximum 100 KB (`MAX_SOURCE_CODE_BYTES = 100000`). Submissions exceeding this limit are rejected with HTTP 413 Payload Too Large.
- **Output Limit Cap**: Sandbox standard output and standard error are capped at 64 KB (`MAX_OUTPUT_BYTES = 65536`). Programs exceeding this limit receive `OUTPUT_LIMIT_EXCEEDED` and container termination.
- **Telemetry Batch Cap**: Telemetry arrays are capped at 1000 items per request (`max_length=1000`).

## 2. Ephemeral Sandbox Container Hardening
- **User**: Runs under non-root uid:gid `10001:10001`.
- **Filesystem**: `read_only=True` (tmpfs mounted for temporary execution file).
- **Networking**: `network_mode="none"` completely disabling external network interfaces.
- **CPU & Memory**: `mem_limit="128m"`, `nano_cpus=500000000` (0.5 CPU quota).
- **Privileges**: `no-new-privileges:true`, dropping all Linux capabilities (`cap_drop=["ALL"]`).

## 3. Web & API Protection Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- CORS configuration dynamically restricts origins via `CORS_ORIGINS`.
