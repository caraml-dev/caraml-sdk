.PHONY: setup
setup:
	pip install -r requirements.txt -r requirements.dev.txt

.PHONY: version
version:
	$(eval VERSION=$(if $(OVERWRITE_VERSION),$(OVERWRITE_VERSION),$(shell ../../scripts/vertagen/vertagen.sh -p packages/caraml-auth-google/ -y)))
	@echo 'VERSION = "$(VERSION)"' > version.py
	@echo "caraml-auth-google version:" $(VERSION)

.PHONY: lint
lint:
	@$(eval black_version=$(shell pip show black | grep Version | grep -oE '[0-9].*'))
	@[ "${black_version}" == "22.6.0" ] || sh -c "pip install black==22.6.0"
	@black .

.PHONY: build
build: version
	@rm -rf build dist
	@python setup.py sdist bdist_wheel

.PHONY: test
test:
	@python -m pytest --cov=caraml_auth tests/
