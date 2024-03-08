# Profile Configuration

For creating custom profiles, see [Create Custom Profiles](site:oci_env/docs/dev/guides/create-custom-profiles/).

## Available variables
These variables can be used in `pulp_config.env` and `compose.yaml`:

- `API_HOST`: hostname where pulp expects to run (default: localhost).
- `API_PORT`: port that pulp expects to run on. This port will also get exposed on the pulp container (default: 5001).
- `API_PROTOCOL`: can be http or https (default: http).
- `NGINX_SSL_PORT`: the port on which Nginx listens to https traffic (default: 443). `API_PROTOCOL` needs to be `https`.
- `NGINX_PORT`: the port on which Nginx listens to http traffic. Note: the functional tests won't work correctly if this is different from API_PORT. (default: 5001, or the value of `API_PORT`).
- `DEV_SOURCE_PATH`: colon separated list of python dependencies to include from source.
- `COMPOSE_PROFILE`: colon separated list of profiles.
- `DJANGO_SUPERUSER_USERNAME`: username for the super user (default: admin).
- `DJANGO_SUPERUSER_PASSWORD`: password for the super user (default: password).
- `COMPOSE_PROJECT_NAME`: the project name passed to podman-compose. Use this when running multiple environments to keep containers and volumes separate (default: oci_env).
- `SRC_DIR`: path to load source code from. Set this if you want to use a different set of git checkouts with your environment (default: oci_env/../)

## Notes

- Variables are templated using pythons `"{VAR}".template(VAR="my_var")` function, so they must be referenced as `{VARIABLE_NAME}` in environment and compose files.
- Profiles can use variables outside of this list as well. They are just required to be defined in the user's compose.env file or in the profile's (or its parents) `profile_default_config.env` file.

Example:

```bash title="pulp_config.env"
PULP_ANSIBLE_API_HOSTNAME="{API_PROTOCOL}://{API_HOST}:{API_PORT}"
PULP_ANSIBLE_CONTENT_HOSTNAME="{API_PROTOCOL}://{API_HOST}:{API_PORT}/pulp/content"
```
