# pminio

## Usage

Adding this profile sets up a Minio instance that is configured as Pulp's S3 backend. The Minio
instance is launched as a separate service and can be accessed inside the main container at
`http://pminio:9000`. The Minio Client CLI,`mc`, is also installed and configured inside the main 
container to talk to the Minio service.

If you want to interact with Pulp distributions from your host,
add a new entry to `/etc/hosts` on the host machine for the `pminio` alias, like so:

```
127.0.0.1   localhost localhost4 pminio
::1         localhost localhost6 pminio
```

The same entry should not exist in the container's `/etc/hosts` file because the `pminio` service
is already addressable from the internal network.

Note that it is suggested to create a `pulp` bucket beforehand.

## Extra Variables

Below are the default variables used in configuring the Minio instance. If you are using
multiple OCI environments you must change the `MINIO_PORT` and `MINIO_CONSOLE_PORT` in your
`compose.env` profiles to allow the multiple services to bind correctly.

- `S3_ENDPOINT_URL`
    - Description: The internal url the Minio instance will be available at.
    - Default: http://pminio:9000
- `S3_ACCESS_KEY`
    - Description: The S3 access key used to access the Minio instance.
    - Default: pulpminioaccesskey
- `S3_SECRET_KEY`
    - Description: The S3 secret key used to access the Minio instance.
    - Default: pulpminioinsecuresecretkey
- `MINIO_PORT`
    - DESCRIPTION: The outside port that the Minio instance will be exposed at.
    - DEFAULT: 9000
- `MINIO_CONSOLE_PORT`
    - DESCRIPTION: The outside port that the Minio Console will be exposed at.
    - DEFAULT: 9090
