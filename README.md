# OCI Env

A developer environment for pulp based off of the [Pulp OCI Images](https://github.com/pulp/pulp-oci-images)

## Getting started

0. Install the `oci-env` python client.

  ```bash
  cd oci_env

  # if pip3 isn't available, try pip. Python 3 is required for oci-env.
  pip3 install -e client
  ```

1. Install podman or docker compose

    - [docker-compose installation docs](https://docs.docker.com/compose/install/). 
    - [podman-compose installation docs](https://github.com/containers/podman-compose#installation).

2. Set up your directory with the following structure:

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

3. Define your `.compose.env` file.

    `cp .compose.env.example .compose.env`

    A minimal `.compose.env` will look something like this:

    ```
    DEV_SOURCE_PATH=pulpcore:pulp_ansible

    # this is set to podman by default.
    COMPOSE_BINARY=docker
    ```

    In this example, `../pulpcore` and `../pulp_ansible` will be installed from source. Other settings
    include:

    - `COMPOSE_PROFILE`: this is used to define environments with extra services running. This could be
      used to launch a UI, set up an authentication provider service or configure an object store.
      Example `COMPOSE_PROFILE=ha:galaxy_ng/ui`. This will use the the `ha` profile from `oci_env/profiles/`
      and the `ui` profile from `galaxy_ng/profiles/`
    - `PULP_<SETTING_NAME>`: set any setting.py value for your environment. Example: `PULP_GALAXY_REQUIRE_CONTENT_APPROVAL=False`

4. Run the environment

    ```bash
    # build the images
    oci-env compose build

    # start the service
    oci-env compose up 
    ```

    The `oci-env compose` command accepts all the same arguments as `podman-compose` or `docker-compose`

    By default the API will be served from http://localhost:5001/pulp/api/v3/. You can login with `admin`/`password` by default.
    The api will reload anytime changes are made to any of the `DEV_SOURCE_PATH` projects.

5. Teardown

    To shut down the containers run `oci-env compose down`. Data in your system will be preserved when you restart the containers.

    To reset the database run `oci-env compose down --volumes`. This will shut down the containers and delete all the data in your system.

## The oci-env CLI

This CLI has all the functionality required to run the OCI Env developer environment. See `oci-env --help` for a list of supported commands.

`oci-env` can either be run in the `oci_env/` root dir, or it can be executed from anywhere by setting the `OCI_ENV_PATH` environment variable.
The path supplied to `OCI_ENV_PATH` is expected to be the `oci_env/` project root dir (where your .compose.env file is defined.)

## Running Tests

### Lint

```bash
# install the lint requirements

oci-env test -i lint

# run the linter
oci-env test -p PLUGIN_NAME lint
```

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
# Generate the pulp client. This will build clients for all plugins in DEV_SOURCE_PATH. -i will also install the client in the container.
oci-env generate-client -i

# Install the functional test requirements
oci-env test -i functional

# Run the tests
oci-env test -p PLUGIN_NAME functional
```

Bindings for specific plugins can be regenerated with `oci-env generate-client PLUGIN_NAME`.

#### Debugging functional tests

1. Add "epdb" to the functest_requirements.txt file in your pulp_ansible checkout path.
2. Inside any functional test, add `import epdb; epdb.st()`.
3. Re-run `oci-env test -i functional` and `oci-env test -p pulp_ansible functional --capture=no` commands again.

#### Using PyCharm remote debug server

1. Start the debugger server in PyCharm. When using `podman`, the hostname should be set to
   `host.containers.internal` hostname. `Docker` users should use `host.docker.internal` hostname. 
2. Add a break point to your Pythong code:
```
import pydevd_pycharm
pydevd_pycharm.settrace('host.containers.internal', port=3013, stdoutToServer=True, stderrToServer=True)`
```
3. Restart all services you need to pick up the code change by running `s6-svc -r /var/run/s6/services/<service_name>`
4. Perform the action that should trigger the code to run.

Please note that `host.containers.internal` points to the wrong interface in `podman` < 4.1. When
using `podman` < 4.1, you need modify `/etc/hosts` inside the container running Pulp with the IP
address for the publicly facing network interface on the host.

### Unit

Coming soon!

## Writing New Profiles

OCI env has a pluggable profile system. Profiles can be defined in `oci_env/profiles/` or
in any pulp plugin at `<PLUGIN_NAME>/profiles/`.

Each profile goes in it's own directory and can include:

- `compose.yaml`: This is a docker compse file that can define new services or modify the base `pulp` service.
- `pulp_config.env`: Environment file that defines any settings that the profile needs to run.
- `init.sh`: Script that gets run when the environment loads. Can be used to initialize data and set up tests. Must be a bash script.

### Variables

These variables can be used in `pulp_config.env` and `compose.yaml`:

- `API_HOST`: hostname where pulp expects to run.
- `API_PORT`: port that pulp expects to run on. This port will also get exposed on the pulp container.
- `API_PROTOCOL`: can be http or https.
- `DEV_SOURCE_PATH`: colon separated list of python dependencies to include from source.
- `COMPOSE_PROFILE`: colon separated list of profiles
- `DJANGO_SUPERUSER_USERNAME`: username for the super user (default: admin)
- `DJANGO_SUPERUSER_PASSWORD`: password for the super user (default: password)
- `NGINX_PORT`: the port on which Nginx listens to http traffic (default: 80)
- `NGINX_SSL_PORT`: the port on which Nginx listens to https traffic (default: 443). `API_PROTOCOL` needs to be `https`.
- `COMPOSE_CONTEXT`: the context directory for podman-compose (default: current working directory)
- `DEV_IMAGE_SUFFIX`: the suffix for the image name
- `DEV_VOLUME_SUFFIX`: the suffic for the volume
- `COMPOSE_PROJECT_NAME`: the project name passed to podman-compose (default: -oci_env)


Variables are templated using pythons `"{VAR}".template(VAR="my_var")` function, so they must be referenced as `{VARIABLE_NAME}` in environment and compose files.

Example pulp_config.env:

```
PULP_ANSIBLE_API_HOSTNAME="{API_PROTOCOL}://{API_HOST}:{API_PORT}"
PULP_ANSIBLE_CONTENT_HOSTNAME="{API_PROTOCOL}://{API_HOST}:{API_PORT}/pulp/content"
```

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
