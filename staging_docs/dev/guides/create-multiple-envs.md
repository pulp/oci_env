# Run multiple environments

You can running multiple environments simultaneously.

## Create an `.env` file

You may place it in the root of `oci_env` dir:

```bash title="custom.env"

COMPOSE_PROFILE=my_profiles
DEV_SOURCE_PATH=pulpcore

# These three values must be different from the api port, docs port and project name for any other
# instances of the environment that are running to avoid conflicts.
API_PORT=4002
DOCS_PORT=12346
COMPOSE_PROJECT_NAME=test

# If you want to use a different directory for your git checkouts you can set this
# SRC_DIR=/path/to/my/git/checkouts
```

## Launch the Environment

If you are in the same dir as the file, you can run:

```bash
oci-env -e custom.env compose up
```

## Run from anywhere

If you have `OCI_ENV_PATH` defined you can create a directory for your custom definitions and run oci-env from there without having to specify an absolute path. Example:

```bash
$ tree
~
├── oci_env
└── oci_env_configs
    ├── custom.env
    └── test.env
$ export OCI_ENV_PATH="~/oci_env"
$ cd oci_env_configs
$ oci-env -e custom.env compose up
```
