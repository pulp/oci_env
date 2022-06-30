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

.PHONY: test/functional/install_requirements
test/functional/install_requirements:
	make generate_client PLUGIN=$(PLUGIN)
	./compose exec pulp bash /src/oci_env/base/tests/install_requirements.sh $(PLUGIN)

.PHONY: test/run-functional
test/run-functional:
	./compose exec pulp bash /src/oci_env/base/tests/run_functional_tests.sh $(PLUGIN) $(FLAGS)
