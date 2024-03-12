# Getting started

Before we start, make sure you have at least one of the two installed:

- [docker-compose installation docs](https://docs.docker.com/compose/install/). 
- [podman-compose installation docs](https://github.com/containers/podman-compose#installation).

Also, here are some useful things about the CLI:
- It has all the functionality required to run the OCI Env developer environment.
See `oci-env --help` for a list of supported commands.
_ It can be run in the `oci_env/` root dir.
- It can be executed from anywhere by setting the `OCI_ENV_PATH` environment variable to the `oci_env/` project root dir.
So let's get started.

## 1. Install the `oci-env` python client.

```bash
cd oci_env

# if pip3 isn't available, try pip. Python 3 is required for oci-env.
pip3 install -e client
```

## 2. Set up your directory with the following structure:

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

Note, the `/src/` folder in the container is the parent folder containing the `oci_env` and all
plugin checkouts on the container host.

## 3. Define your `compose.env` file.

`cp compose.env.example compose.env`

A minimal `compose.env` will look something like this:

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

## 4. Run the environment

```bash
# build the images
oci-env compose build

# start the service
oci-env compose up 
```

The `oci-env compose` command accepts all the same arguments as `podman-compose` or `docker-compose`

By default the API will be served from `http://localhost:5001/pulp/api/v3/`.
You can login with `admin`/`password` by default. E.g.:

```bash
http --auth admin:password get http://localhost:5001/pulp/api/v3/status/
```

The api will reload anytime changes are made to any of the `DEV_SOURCE_PATH` projects.

`oci-env compose` accepts all of the arguments that docker and podman compose take.
You can also launch the environment in the background with `oci-env compose up -d` and access the logs with `oci-env compose logs -f` if you don't want to run it in the foreground.  

In case you have problems with setup in macOS, check these [troubleshooting tips](site:oci_env/docs/dev/guides/macos_troubleshooting_tips.md). 

## 5. Teardown

When you are done, you can tear down your container.
Data in your system will be preserved when you restart it, or you can choose to tear down the volumes as aswell:

```bash
# Preserve data
oci-env compose up

# Tear down data
oci-env compose down --volumes  # Shut down the containers and delete all the container data on your system
oci-env db reset # alias
```
