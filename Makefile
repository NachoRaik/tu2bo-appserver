ENVDIR := env

.PHONY: setup
setup:
	( test -d $(ENVDIR) || ( \
		echo ">>>>>> Crear directorio para venv <<<<<<" && \
		python3 -m venv $(ENVDIR) ) \
	)

.PHONY: install
install: setup
	echo ">>>>>> Install requirements <<<<<<"
	. env/bin/activate && pip3 install -r requirements.txt

.PHONY: test
test:
	pytest -v

.PHONY: ping
ping:
	curl -vvv "localhost:5000/ping"


.PHONY: help
help:
	@echo 'Usage: make <target>'
	@echo ''
	@echo 'Available targets are:'
	@echo ''
	@grep -E '^\.PHONY: *' $(MAKEFILE_LIST) | cut -d' ' -f2- | sort