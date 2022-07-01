# OCI Env

A developer environment for pulp based off of the [Pulp OCI Images](https://github.com/pulp/pulp-oci-images)

## Getting started

0. Install docker compose

    See the [docker-compose installation docs](https://docs.docker.com/compose/install/). Podman Compose
    might work, but hasn't been tested yet.

1. Set up your directory with the following structure:

    ```
    .
    ├── oci_env
    ├── pulp-openapi-generator
    ├── pulp_ansible
    ├── pulp_container
    ├── pulpcore
    └── any_other_python_sources
    ```

    The OCI env project should be in the same directory as any pulp plugins you wish to run.

2. Define your `.compose.env` file.

    `cp compose.env.example .compose.env`

    A minimal `.compose.env` will look something like this:

    ```
    DEV_SOURCE_PATH='pulpcore:pulp_ansible'
    ```

    In this example, `../pulpcore` and `../pulp_ansible` will be installed from source. Other settings
    include:

    - `COMPOSE_PROFILE`: this is used to define environments with extra services running. This could be
      used to launch a UI, set up an authentication provider service or configure an object store.
      Example `COMPOSE_PROFILE=ha:galaxy_ng/ui`. This will use the the `ha` profile from `oci_env/profiles/`
      and the `ui` profile from `galaxy_ng/profiles/`
    - `PULP_<SETTING_NAME>`: set any setting.py value for your environment. Example: `PULP_GALAXY_REQUIRE_CONTENT_APPROVAL=False`

3. Run the environment

    ```bash
    # build the images
    ./compose build

    # start the service
    ./compose up 
    ```

    The ./compose script accepts all the same arguments as `podman-compose` or `docker-compose`

    By default the API will be served from http://localhost:5001/pulp/api/v3/. You can login with `admin`/`password` by default.
    The api will reload anytime changes are made to any of the `DEV_SOURCE_PATH` projects.

4. Teardown

    To shut down the containerse run `./compose down`. Data in your system will be preserved when you restart the containers.

    To reset the databse run `./compose down --volumes`. This will shut down the containers and delete all the data in your system.

## Running Tests

### Functional

Before functional tests can be run, you must clone github.com/pulp/pulp-openapi-generator into the parent directory.

Ex:

```
.
├── (...)
├── oci_env
└── pulp-openapi-generator
```

```bash
# Install the requirements. This will generate and install the bindings.
make test/functional/install_requirements PLUGIN=pulp_ansible

# Run the tests
make test/run-functional PLUGIN=pulp_ansible FLAGS="-k my_test_name"
```

The bindings can be regenerated with `make generate_client PLUGIN=pulp_ansible`.

#### Debugging functional tests

1. Add "epdb" to the functest_requirements.txt file in your pulp_ansible checkout path.
2. Inside any functional test, add `import epdb; epdb.st()`.
3. Add `--capture=no` to the pytest args in base/tests/run_functional_tests.sh 
4. Re-run the `test/functional/install_requirements` and `test/run-functional PLUGIN=pulp_ansible` makefile targets again.

### Unit

Coming soon!

## Writing New Profiles

OCI env has a pluggable profile system. Profiles can be defined in `oci_env/profiles/` or
in any pulp plugin at `<PLUGIN_NAME>/profiles/`.

Each profile goes in it's own directory and can include:

- `compose.yaml`: This is a docker compse file that can define new services or modify the base `pulp` service.
- `pulp_config.env`: Environment file that defines any settings that the profile needs to run.
- `init.sh`: Script that gets run when the environment loads. Can be used to initialize data and set up tests. Must be a bash script.

### Example

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
      context: "${ANSIBLE_HUB_UI_PATH}"
    ports:
      - "8002:8002"
    volumes:
      - "${ANSIBLE_HUB_UI_PATH}:/hub/app/"
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
PULP_GALAXY_API_PATH_PREFIX=/api/automation-hub/
PULP_GALAXY_DEPLOYMENT_MODE=standalone
```

To activate this profile set `COMPOSE_PROFILE=galaxy_ng/ui`. Running this will launch the UI container along with pulp.

```bash
dnewswan-mac:oci_env dnewswan$ docker ps
CONTAINER ID   IMAGE                         COMMAND                  CREATED         STATUS         PORTS                    NAMES
2cc06f79bc87   oci_env_ui                    "docker-entrypoint.s…"   3 seconds ago   Up 1 second    0.0.0.0:8002->8002/tcp   oci_env_ui_1
e1c3ae797018   localhost/oci_env/pulp:base   "/init"                  6 seconds ago   Up 2 seconds   0.0.0.0:5001->80/tcp     oci_env_pulp_1
```

Multiple profiles can be selected with `COMPOSE_PROFILE=galaxy_ng/ui:profile2:profile3`. The last profile loaded gets priority on environment variables. Each `compose.yaml` is added additively, and subsquent profles can modify the services from previous profiles.
