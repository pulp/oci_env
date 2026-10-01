# lean

A density-focused profile for short-lived or parallel Pulp environments (for example multiple
coding agents running scoped functional tests).

## What it does

- Sets `PULP_WORKERS=1` so each environment runs a single task worker
- Caps the `pulp` container with `mem_limit` and `cpus` so parallel stacks do not starve the host

This profile does **not** add sidecars (UI, Kafka, OpenTelemetry, RustFS, etc.). Combine it with
other profiles only when those services are required.

## Usage

```bash
COMPOSE_PROFILE=lean
DEV_SOURCE_PATH=pulpcore
PULP_WORKERS=1
API_PORT=5101
COMPOSE_PROJECT_NAME=agent_example
```

Prefer the `oci-env agent` commands to allocate ports/project names and manage lifecycle:

```bash
oci-env agent create example --plugins pulpcore
oci-env agent up example
oci-env agent test example -p pulpcore functional -k test_crud_repos
oci-env agent destroy example
```

When the code already lives in an AI tool worktree (Cursor `/worktree`, etc.), point at it:

```bash
oci-env agent create example \
  --plugins pulpcore=/path/to/external/worktree
```

## Extra variables

- `PULP_WORKERS`
  - Description: Number of pulpcore workers to start
  - Default: `1`
- `LEAN_MEM_LIMIT`
  - Description: Memory limit for the `pulp` container (`mem_limit`)
  - Default: `2g`
- `LEAN_CPUS`
  - Description: CPU limit for the `pulp` container (`cpus`)
  - Default: `1.0`

## Notes

- Build the base image once per host (`oci-env compose build`); agent environments reuse it
- Keep `DEV_SOURCE_PATH` minimal (only plugins under test) for faster startup
- Full interactive profiles (galaxy UI, otel, …) remain available for human workflows; use `lean` for parallel agent density
