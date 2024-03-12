# Create Custom Profiles

You can create custom profiles for your instance of oci_env by creating adding `_local` to the end of the profile name. These profiles will be ignored by git. Example `oci_env/profiles/my_custom_profile_local/`.

For a complete list of available variables, check the [Profile Configuration](site:oci_env/docs/dev/reference/profile-config/) reference.

## Basic Usage

OCI env has a pluggable profile system. Profiles can be defined in `oci_env/profiles/` or
in any pulp plugin at `<PLUGIN_NAME>/profiles/`.

To generate a new profile template run:

```bash
# Generate a new profile in oci_env
oci-env profile init my_profile

# Generate a new profile in a plugin repo
oci-env profile init -p PLUGIN_NAME my_profile

# List available profiles
oci-env profile ls

# Display the README.md for a profile
oci-env profile docs my_profile
```

Each profile goes in it's own directory and can include:

- `compose.yaml`: This is a docker compose file that can define new services or modify the base `pulp` service.
- `pulp_config.env`: Environment file that defines any settings that the profile needs to run.
- `init.sh`: Script that gets run when the environment loads. Can be used to initialize data and set up tests. Must be a bash script.
- `profile_reqirements.txt`: A list of other profiles that are required to be set in COMPOSE_PROFILE for this profile to function.
- `profile_default_config.env`: A list of default variables to use if not specified by the user.
- `README.md`: Readme file describing what the profile is for and how to use it.


## Intertermediate Example

Profile structure in the galaxy_ng plugin

```
galaxy_ng/profiles/
└── ui
    ├── compose.yaml
    └── pulp_config.env
```

compose.yaml: This defines a UI service that builds the container found at `ANSIBLE_HUB_UI_PATH` and configures the UI to proxy requests to the pulp API server.

```yaml
version: "3.7"

services:
  ui:
    build:
      context: "{ANSIBLE_HUB_UI_PATH}"
    ports:
      - "8002:8002"
    volumes:
      - "{ANSIBLE_HUB_UI_PATH}:/hub/app/"
    tmpfs:
      # Forces npm to ignore the node_modules in the volume and look
      # for it in ../node_modules instead, while still being able to write .cache
      - "/hub/app/node_modules"
    depends_on:
      - pulp
    environment:
      - "API_PROXY_HOST=pulp"
      - "API_PROXY_PORT=80"
      - "DEPLOYMENT_MODE=standalone"
```

pulp_config.env: The UI expects the galaxy apis to be served from `/api/automation-hub/` and for the app to be launched in standalone mode. The environment file provided with the profile ensures that the API is configured correctly to consume the new service.

```
PULP_CONTENT_PATH_PREFIX=/api/automation-hub/v3/artifacts/collections/

PULP_GALAXY_API_PATH_PREFIX=/api/automation-hub/

PULP_GALAXY_COLLECTION_SIGNING_SERVICE=ansible-default
PULP_RH_ENTITLEMENT_REQUIRED=insights

PULP_ANSIBLE_API_HOSTNAME={API_PROTOCOL}://{API_HOST}:{API_PORT}
PULP_ANSIBLE_CONTENT_HOSTNAME={API_PROTOCOL}://{API_HOST}:{API_PORT}/api/automation-hub/v3/artifacts/collections

PULP_TOKEN_AUTH_DISABLED=true

```

To activate this profile set `COMPOSE_PROFILE=galaxy_ng/ui`. Running this will launch the UI container along with pulp.

```bash
dnewswan-mac:oci_env dnewswan$ docker ps
CONTAINER ID   IMAGE                         COMMAND                  CREATED         STATUS         PORTS                    NAMES
2cc06f79bc87   oci_env_ui                    "docker-entrypoint.s…"   3 seconds ago   Up 1 second    0.0.0.0:8002->8002/tcp   oci_env_ui_1
e1c3ae797018   localhost/oci_env/pulp:base   "/init"                  6 seconds ago   Up 2 seconds   0.0.0.0:5001->80/tcp     oci_env_pulp_1
```

Multiple profiles can be selected with `COMPOSE_PROFILE=galaxy_ng/ui:profile2:profile3`. The last profile loaded gets priority on environment variables. Each `compose.yaml` is added additively, and subsquent profles can modify the services from previous profiles.

