ENVDIR := env
HEROKU_APP_NAME := tu2bo-appserver


# -- Run scripts
.PHONY: setup
setup:
	( test -d $(ENVDIR) || ( \
		echo ">>>>>> Crear directorio para venv <<<<<<" && \
		python3 -m venv $(ENVDIR) ) \
	)

.PHONY: install
install: setup
	echo ">>>>>> Install requirements <<<<<<"
	. $(ENVDIR)/bin/activate && \
		pip3 install -r app/requirements.txt

.PHONY: test
test: setup
	. $(ENVDIR)/bin/activate && \
		pip3 install -r app/requirements.txt && \
		coverage run -m pytest -v app/tests/ --disable-pytest-warnings && \
		coverage report -m


# -- Heroku related commands
# You need to be logged in Heroku CLI before doing this
#   heroku login
#   heroku container:login
.PHONY: heroku-push
heroku-push:
	heroku container:push web --recursive --app=$(HEROKU_APP_NAME) --verbose

.PHONY: heroku-release
heroku-release:
	heroku container:release web --app $(HEROKU_APP_NAME) --verbose


# -- Utils
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
