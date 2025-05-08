# local\_fixtures

A profile for running test fixtures locally. It pulls down the pulp/pulp-fixtures image which
can be used for running functional tests without relying on the internet connection. The fixtures
are exposed on the very same port on the host machine.

## Usage

Append `local_fixtures` to the `COMPOSE_PROFILE` variable in your `compose.env`.

## Extra Variables

- `PULP_FIXTURES_URL`
    - Description: The URL/origin for the test fixtures endpoint.
    - Default: "http://local\_fixtures:8080"
