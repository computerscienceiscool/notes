Based on the project files, here are the files related to the **exec feature**:

## Core Exec Files

| File | Role |
|------|------|
| `internal/executor/exec.go` | Main handler - validates command, calls Docker, captures output |
| `internal/docker/client.go` | Checks Docker availability, pulls images |
| `internal/docker/container.go` | Runs commands in isolated containers with security restrictions |
| `internal/security/exec_validation.go` | Validates commands against the whitelist |

## Tests

| File | Role |
|------|------|
| `internal/docker/client_test.go` | Tests for Docker connectivity and image pulling |
| `internal/docker/container_test.go` | Tests for container execution, timeouts, security |

## Configuration

| File | Role |
|------|------|
| `internal/config/types.go` | Defines exec config fields (`ExecEnabled`, `ExecWhitelist`, `ExecTimeout`, etc.) |
| `internal/config/defaults.go` | Sets default exec values |
| `internal/cli/flags.go` | Parses exec-related CLI flags (`--exec-enabled`, `--exec-timeout`, etc.) |
| `llm-runtime.config.yaml` | YAML config with exec whitelist and settings |

## Supporting

| File | Role |
|------|------|
| `internal/executor/executor.go` | Dispatcher that routes `exec` commands to `exec.go` |
| `internal/command/parser.go` | Parses `<exec command>` from text |
| `internal/session/session.go` | Audit logging for exec operations |

## Documentation

| File | Role |
|------|------|
| `docs/command-execution-guide.md` | User guide for exec |
| `docs/docker-cheatsheet.md` | Docker setup help |
