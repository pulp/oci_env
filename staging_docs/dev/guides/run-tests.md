# Run Tests

## Lint

```bash
# Install the lint requirements and run the linter for a specific plugin
oci-env test -i -p PLUGIN_NAME lint

# Run the linter without installing lint dependencies.
oci-env test -p PLUGIN_NAME lint
```

## Unit

```bash
# Install the unit test dependencies for a plugin and run it.
oci-env test -i -p PLUGIN_NAME unit

# Run the unit tests for a plugin without installing test dependencies.
oci-env test -p PLUGIN_NAME unit
```

## Functional

Before functional tests can be run, you must clone `github.com/pulp/pulp-openapi-generator` into the parent directory:

```
.
├── (...)
├── oci_env
└── pulp-openapi-generator
```

```bash
# Generate the pulp client. This will build clients for all plugins in DEV_SOURCE_PATH. -i will also install the client in the container.
oci-env generate-client -i

# Install the functional test requirements and run the tests
oci-env test -i -p PLUGIN_NAME functional

# Run the tests without installing dependencies.
oci-env test -p PLUGIN_NAME functional
```

Bindings for specific plugins can be regenerated with `oci-env generate-client PLUGIN_NAME`.

Use `--language` parameter to specify the programming language the bindings should be generated for (default: python),
e.g. `oci-env generate-client -l ruby PLUGIN_NAME`.

## Remote Debugging

### Using `epdb`

1. Add "epdb" to the `functest_requirements.txt` file in your pulp_ansible checkout path.
2. Inside any functional test, add `import epdb; epdb.st()`.
3. Re-run `oci-env test -i functional` and `oci-env test -p pulp_ansible functional --capture=no` commands again.

### Using PyCharm

1. Start the debugger server in PyCharm. When using `podman`, the hostname should be set to
   `host.containers.internal` hostname. `Docker` users should use `host.docker.internal` hostname. 
2. Add a break point to your Pythong code:
```
import pydevd_pycharm
pydevd_pycharm.settrace('host.containers.internal', port=3013, stdoutToServer=True, stderrToServer=True)`
```
3. Restart all services you need to pick up the code change by running `s6-svc -r /var/run/service/<service_name>`
4. Perform the action that should trigger the code to run.

### Caveat

Please note that `host.containers.internal` points to the wrong interface in `podman < 4.1`. When
using `podman < 4.1`, you need modify `/etc/hosts` inside the container running Pulp with the IP
address for the publicly facing network interface on the host.

