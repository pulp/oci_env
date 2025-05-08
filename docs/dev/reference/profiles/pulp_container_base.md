# pulp\_container\_base

A profile for configuring a token server for the Pulp Registry. The profile benefits
from a key pair provided by the container under the `/etc/pulp/certs/` directory. The
token server is exposed at `localhost:{API_PORT}/token/`.

## Usage

Append `pulp_container_base` to the `COMPOSE_PROFILE` variable in your `compose.env` when
working with pulp\_container.
