.DEFAULT:
.PHONY: help
help:             ## Show the help.
	@echo "Usage: make <target>"
	@echo ""
	@echo "Targets:"
	@fgrep "##" Makefile | fgrep -v fgrep | sed 's/^/\n/' | sed 's/#/\n/'


.PHONY: generate_client
generate_client:
	./base/tests/generate_client.sh $(PLUGIN)

.PHONY: dev/install_dev_requirements
dev/install_dev_requirements:
	./compose exec pulp bash /src/oci_env/base/dev/install_dev_requirements.sh $(PLUGIN)

.PHONY: test/lint
test/lint:
	make dev/install_dev_requirements PLUGIN=$(PLUGIN)
	./compose exec pulp bash /src/oci_env/base/tests/run_lint.sh $(PLUGIN)

.PHONY: test/functional/install_requirements
test/functional/install_requirements:
	make generate_client PLUGIN=$(PLUGIN)
	./compose exec pulp bash /src/oci_env/base/tests/install_functional_requirements.sh $(PLUGIN)

.PHONY: test/run-functional
test/run-functional:
	./compose exec pulp bash /src/oci_env/base/tests/run_functional_tests.sh $(PLUGIN) $(FLAGS)

.PHONY: database/psql
database/psql:
	./compose exec pulp bash -c 'pulpcore-manager dbshell'

.PHONY: docker/bash
docker/bash:
	./compose exec pulp bash

.PHONY: api/shell
api/shell:
	./compose exec pulp bash -c 'pulpcore-manager shell'
