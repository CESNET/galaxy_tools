ifndef INSTANCE
$(error INSTANCE is required but not set)
endif

NPROC := $(shell nproc)

help:
	@egrep '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'

lint: ## Lint all yaml files for a given INSTANCE
	find ./$(INSTANCE) -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P $(NPROC) python3 scripts/yaml_check.py
	find ./$(INSTANCE) -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P $(NPROC) -I{} pykwalify -d '{}' -s .schema.yml
	find ./$(INSTANCE) -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P $(NPROC) python3 scripts/identify_unpinned.py

fix: ## For a given INSTANCE fix all lockfiles and add the latest revision to every repo that has no revision
	find ./$(INSTANCE) -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P $(NPROC) python3 scripts/fix_lockfile.py
	find ./$(INSTANCE) -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P $(NPROC) python3 scripts/update_tool.py --without --log debug
	find ./$(INSTANCE) -name '*.yml.lock' | grep '^\./[^/]*/' | grep -v '_test\.yml\.lock$' | xargs -n 1 -P $(NPROC) python3 scripts/fix_outdated.py

update-owner:  ## Run the update script for a subset of repos defined by the OWNER var
	find ./$(INSTANCE) -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P $(NPROC) python scripts/update_tool.py --owner $(OWNER)

update-all: ## Run the update script for all repos
	find ./$(INSTANCE) -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P $(NPROC) python scripts/update_tool.py

install: ## Run the Ephemeris command to install all repos and revisions that are missing from a given INSTANCE
	find ./$(INSTANCE) -name '*.yml' | grep '^\./[^/]*/' | xargs -n 1 -P 1 -I {} shed-tools install --toolsfile {} --galaxy $(INSTANCE) --api_key $(GALAXY_API_KEY) --skip_install_resolver_dependencies

.PHONY: fix lint help update-owner update-all install
