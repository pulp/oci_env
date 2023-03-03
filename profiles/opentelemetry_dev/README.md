# OpenTelemetry Developer Environment Profile

## Usage

This profile is intended to be used as a developer environment to integrate OpenTelemetry framework with Pulp.

So, the stack is composed by:
* Prometheus (exposed at port 8889)
    * Responsible for scraping and storing time-series metrics from the application
* Grafana (exposed at port 3000)
    * Used to create visualizations using Prometheus exposed data
* Jaeger (exposed at port 16686)
    * To visualize traces from the application
* OpenTelemetry Collector
    * Needed to receive, process and export telemetry information between the application and any of its consumers

## Instrumenting code

### Django
You need to modify [pulpcore/app/wsgi.py](https://github.com/pulp/pulpcore/blob/main/pulpcore/app/wsgi.py) to be the following:
```
import os

from django.core.wsgi import get_wsgi_application
from opentelemetry.instrumentation.wsgi import OpenTelemetryMiddleware


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pulpcore.app.settings")


application = get_wsgi_application()
application = OpenTelemetryMiddleware(application)
```
just like pulp/pulpcore#3632.


## Extra Variables
- `PULP_OTEL_ENABLE`
    - Description: Enable telemetry on Pulp.
    - Options:
        - true: Enable OpenTelemetry
        - false: Disable OpenTelemetry
    - Default: false
- `OTEL_EXPORTER_OTLP_ENDPOINT`
    - Description: the address used by the instrumentator to send telemetry
    - Default: http://otel-collector:4318
- `OTEL_EXPORTER_OTLP_PROTOCOL`
    - Description: the protocol used to comunicate with the collector
    - Default: http/protobuf

## Examples / Tips
1. After calling `oci-env compose up` and waiting a moment for it to start up, you can access Grafana on 
`http://localhost:3000`. If it is the first time you're accessing it, it will ask you to change the admin password.
After it, you can check on `Explore` section to find all the metrics collected by OpenTelemetry and sent to Prometheus.
2. We already added the Prometheus Datasource into Grafana. ;)
3. There is some dashboards with visualizations of some metrics, like Latency P55 and Active Connections. Try them out!
4. You can call Jaeger on `http://localhost:16686` to visualize the traces produced by OpenTelemetry. Try to select any 
app on the `Service` field and see some traces.
