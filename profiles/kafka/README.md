# kafka

## Usage

* Runs a kafka service at port 9092

You can connect external tools (e.g. PyCharm kafka plugin) to this kafka instance without authentication.

There are scripts included with kafka you can invoke via `exec` for testing, e.g.

```shell
oci-env exec -s kafka \
  /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server=localhost:9092 \
  --offset earliest \
  --partition 0 \
  --topic pulpcore.tasking.status \
  --max-messages=1
```

## Extra Variables

None.
