# Lean multi-agent environments

Use this guide when several agents (or developers) need isolated Pulp stacks on one host to
run **scoped functional tests against a live API** without sharing mutable state.

## Model

Each agent environment is a full Pulp stack (API, content app, worker, Postgres, Redis) in its
own compose project with its own volumes and API port. Agents do **not** share Postgres or a
writable Python environment, so each can migrate, switch git revisions, and install or remove
dependencies independently.

What is shared safely:

- The immutable base image (`localhost/oci_env/pulp:base`) after a single host build
- Optional shared fixtures (`local_fixtures`) if every agent points at the same fixtures URL

The [`lean`](../reference/profiles/lean.md) profile keeps each stack small: one worker and CPU/memory caps.

Each agent owns a single directory under `.compiled/`:

```text
.compiled/agent_<id>/
  compose.env                      # agent env file
  plugin_volumes_compose.yaml      # bind mounts for plugin checkouts
  pulp-openapi-generator/          # copy of the host generator checkout
  …                                # compose files written here on `up` (parse_profiles)
```

`SRC_DIR` for the agent is that directory. Plugin checkouts are always bind-mounted into
`/src/<plugin>` via the volume overlay (never by sharing the host `SRC_DIR` directly).
If `pulp-openapi-generator` exists under the host source directory, `create` copies it
into the agent `SRC_DIR` so each agent generates clients in isolation. That copy appears
at `/src/pulp-openapi-generator` through the base `{SRC_DIR}:/src` mount.

## Prerequisites

1. Install the `oci-env` client (`pip install -e client` from this repo).
2. Build the base image once on the host:

   ```bash
   oci-env compose build
   ```

3. Agent environments always use **podman**. They do **not** copy settings from the host
   `compose.env`. `PULP_SECRET_KEY` defaults to `dummy`; pass other Pulp/Django/profile
   settings with `--env KEY=VALUE`.

4. Have plugin checkouts under a common host directory (default: parent of `oci_env`), for example:

   ```text
   ~/devel/
   ├── oci_env
   ├── pulpcore   # includes pulp_file
   ├── pulp_rpm
   └── pulp-openapi-generator
   ```

   `pulp_file` ships inside the `pulpcore` checkout — do not list it in `--plugins`.
   `pulp-openapi-generator` is required for `oci-env agent generate-client`.

## Typical agent loop

```bash
# 1. Create a lean env (resolves plugins under the default host SRC_DIR)
oci-env agent create pr-123 --plugins pulpcore

# Or point at an AI-tool / git worktree for plugins under test
oci-env agent create pr-123 \
  --plugins pulpcore=~/.cursor/worktrees/pulpcore/my-wt

# 2. Start and wait for the live API
oci-env agent up pr-123

# 3. Generate/install clients for plugins under test
oci-env agent generate-client pr-123

# 4. Run narrowly scoped functional tests against that agent's API
oci-env agent test pr-123 -p pulpcore -- -k test_crud_repos

# 5. Tear down containers, volumes, and the agent compiled directory
oci-env agent destroy pr-123
```

List allocated agents:

```bash
oci-env agent ls
```

## Create options

| Flag | Purpose |
|------|---------|
| `--plugins pulpcore[=PATH]:…` | Colon-separated `PLUGIN[=PATH]` list (`DEV_SOURCE_PATH`; default `pulpcore`) |
| `--host-src-dir PATH` | Parent used when a plugin has no `=PATH` (default: host `SRC_DIR` or parent of `oci_env`) |
| `--port 5105` | Pin `API_PORT` (default: allocate from 5100–5199) |
| `--env KEY=VALUE` | Set any other agent env var (repeatable), e.g. `COMPOSE_PROFILE`, `LEAN_MEM_LIMIT` |

Defaults baked into the agent env file: `COMPOSE_PROFILE=lean`, `COMPOSE_PROJECT_NAME=agent_<id>`,
`COMPOSE_BINARY=podman`, `API_HOST=localhost`, `API_PROTOCOL=http`, `PULP_SECRET_KEY=dummy`,
`SRC_DIR=.compiled/agent_<id>`. Lean profile defaults still supply `PULP_WORKERS=1` and resource
caps unless you override them with `--env`.

### Plugin paths

`--plugins` accepts an optional path per plugin. Omit the path to resolve
`<host-src-dir>/<plugin>`:

```bash
# Both plugins from the default host SRC_DIR (e.g. ~/devel/pulpcore, ~/devel/pulp_rpm)
oci-env agent create pr-123 --plugins pulpcore:pulp_rpm

# Explicit worktree for pulpcore; pulp_rpm from host SRC_DIR
oci-env agent create pr-123 \
  --plugins pulpcore=~/.cursor/worktrees/pulpcore/my-wt:pulp_rpm
```

`create` always writes a compose volume overlay that bind-mounts each real checkout at
`/src/<plugin>` (nested under the base `{SRC_DIR}:/src` mount). `pulp-openapi-generator`
is copied into the agent `SRC_DIR` when present under `--host-src-dir`; if it is missing,
`create` warns and `generate-client` will fail until you clone it and recreate the agent.

`oci-env agent generate-client` runs the generator against that per-agent copy and
installs the resulting packages from `/src/pulp-openapi-generator` inside the container.

Destroy removes the entire `.compiled/agent_<id>/` directory, including the generator
copy. It never deletes the plugin checkouts that were bind-mounted.

## Parallelism tips

- Build images once; agent `up` should not rebuild unless you pass `--build`.
- Keep `DEV_SOURCE_PATH` limited to plugins under test — that dominates startup cost after workers.
- Prefer scoped pytest paths/markers; full suites multiply host load.
- Destroy agents when finished so ports and volumes are reclaimed.
- Default credentials are `admin` / `password` unless overridden with `--env`.

## How tests hit the live API

`oci-env agent test` loads that agent's env file (`API_PORT`, credentials, `SRC_DIR`, project name)
and runs the existing `oci-env test` path inside **that** container. Functional tests therefore
exercise the agent's live API, not a shared default on port 5001.

The functional test runner prints the API URL and auth user before invoking pytest.

## Manual env files

Agent commands write env files to `.compiled/agent_<id>/compose.env`. You can still use the generic
multi-env flow with `-e` if you prefer hand-written files; see
[Run multiple environments](create-multiple-envs.md).

## When not to use lean agents

Interactive work that needs UI, Kafka, OpenTelemetry, MinIO, or other sidecars should keep using
the normal profiles. Add those profiles with `--env COMPOSE_PROFILE=lean:…` only when required —
they increase resource use and reduce how many agents fit on one machine.
