# s3_storage

## Usage

This profile starts a RustFS S3-compatible storage service and configures Pulp to use it. The S3 API
is available inside the environment at `http://rustfs:9000`. Neither the S3 API nor the RustFS
console is published to the host by default.

To access Pulp distributions from the host, add the `rustfs` alias to `/etc/hosts`:

```
127.0.0.1   localhost localhost4 rustfs
::1         localhost localhost6 rustfs
```

The alias is not needed in the container because the `rustfs` service is addressable on the internal
network. The profile creates the configured `pulp` bucket during startup.

To expose the S3 API on the host, add a port mapping under the `rustfs` service in a Compose
override, for example `127.0.0.1:9100:9000`. Add `127.0.0.1:9101:9001` if you also want to expose
the RustFS console. The internal S3 URL used by Pulp remains `http://rustfs:9000`.

## Extra Variables

- `S3_ENDPOINT_URL`
    - Description: The internal URL for the RustFS S3 API.
    - Default: http://rustfs:9000
- `S3_ACCESS_KEY`
    - Description: The S3 access key used by Pulp and RustFS.
    - Default: pulps3storageaccesskey
- `S3_SECRET_KEY`
    - Description: The S3 secret key used by Pulp and RustFS.
    - Default: pulps3storageinsecuresecretkey
