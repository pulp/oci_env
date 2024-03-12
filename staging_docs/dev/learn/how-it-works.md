# How it Works

At it's core, the oci-env command launches a predictable set of containers with a CLI interface to communicate with them. Thes containers are launched by taking advantage of a feature in docker and podman compose that allow multiple compose.yaml files to be selected via the `-f` flag. The command that `oci-env` runs can be viewed with the `-v` flag:

```bash
oci-env -v compose up
Running command in container: docker-compose -p oci_env -f /Users/dnewswan/code/hub/oci_env/.compiled/oci_env/base_compose.yaml -f /Users/dnewswan/code/hub/oci_env/.compiled/oci_env/galaxy_ui_compose.yaml up
```

Since not all compose runtimes support variable interpolation, oci-env handles that by itself. The compose.yaml files provided by all of the plugins are gathered up and the variables defined in your `compose.env` file are substituted using python's `str.format()` command and placed in the `.compiled/<COMPOSE_PROJECT_NAME>/` directory. This directory contains all the information for the running instance of your dev enviornment:

```bash
(venv) dnewswan-mac:oci_env dnewswan$ tree .compiled/
.compiled/
├── ci
│  ├── base_compose.yaml
│  ├── combined.env
│  └── init.sh
└── oci_env
    ├── base_compose.yaml
    ├── combined.env
    ├── galaxy_ui_compose.yaml
    └── init.sh
```

`.compiled/` contains all your compose files (with the correct variable substitutions) as well as an `init.sh` script that launches each profile's init.sh script and a combined.env file which combines all the pulp_config.env files into one and performs variable substitution. The `combined.env` file is then loaded into the pulp container as an environment variable, and `init.sh` is run once the container has initialized.

Once all of the information here is compiled, `oci-env` launches the container runtime and mounts the following directories:

- oci_env is mounted into `/opt/oci_env/`. This creates a predictable location to launch scripts provided by oci_env (such as `/opt/oci_env/base/container_scripts/run_functional_tests.sh`)
- your source code directory is mountent into `/opt/src/`. This provies a predictable location to find plugin source code (such as `/src/pulpcore/`).
