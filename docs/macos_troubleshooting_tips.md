# macOS troubleshooting tips

## Setup on arm64 macOS machines 

Unfortunately, pulp-oci-images [aren't built](https://github.com/pulp/pulp-oci-images/pull/369) for other platforms
than amd64, so you're likely to see the output below when trying to follow the setup instructions on these machines.

This is what you're likely to see in your console when trying the setup on a `arm64` machine:

First, you will see a warning: `WARNING: image platform (linux/amd64) does not match the expected platform (linux/arm64)`

<img width="805" alt="oci-env compose build process displaying the warning above" src="https://github.com/pulp/pulp-oci-images/assets/411301/c42ba41a-833f-4a52-83a2-c6a60d6ad4cd">

But even so, the command `oci-env compose build` will end with `exit code: 0`

<img width="1187" alt="oci-env compose build process returning exit code: 0" src="https://github.com/pulp/pulp-oci-images/assets/411301/325eee6f-f0c4-4079-8ce3-3d351b03ffce">

Finally, when you try to run `oci-env compose up` this is what you will see:

<img width="1594" alt="oci-env compose up errors" src="https://github.com/pulp/pulp-oci-images/assets/411301/10578d68-d179-4d35-958b-38b95e24ca07">

In order to fix it, the simplest and fastest way is just to download [Docker Desktop](https://www.docker.com/products/docker-desktop/)
and enable Rosetta 2 support, like this:

<img width="1150" alt="Docker Desktop Rosetta 2 setup" src="https://github.com/pulp/pulp-oci-images/assets/411301/2ee2904a-f6e4-4f70-a77b-2aa32f588165">

After setting it up, you need to click in `Apply and Restart` so Docker Desktop will restart and apply the configuration.

Finally, you need to change the `COMPOSE_BINARY` variable in your `compose.env` file to `COMPOSE_BINARY=docker`, like so:

```dotenv
# Program to use for compose. This defaults to podman. Uncomment this to use docker-compose.
COMPOSE_BINARY=docker
```

Run these commands:

```shell
oci-env compose build
oci-env compose up
```

And it should run properly 🎉

<img width="1447" alt="oci-env compose up (with Docker) running properly" src="https://github.com/pulp/pulp-oci-images/assets/411301/7bb3da07-d2ba-490d-8c86-43cc9d72598a">

## Other problems

If you see the message `=> ERROR [_base internal] load metadata for ghcr.io/pulp/pulp-ci-centos:latest` when running `oci-env compose build`:

<img width="732" alt="oci-env compose build problems" src="https://github.com/pulp/pulp-oci-images/assets/411301/2d08eeb2-ae97-435e-9596-0a5c96ec5f62">

It means your `~/.docker/config.json` probably is configured to access a private Docker registry, so verify which
configurations are there and adjust it accordingly.

If you want to start fresh and have a new `~/.docker/config.json`, you can just run `rm  ~/.docker/config.json`, restart
Docker Desktop so it is recreated and rerun `oci-env compose build`, which should work properly.








