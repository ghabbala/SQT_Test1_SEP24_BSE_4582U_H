# TicketHub QA package - build/task definitions.
# One command for a marker:  make test
PY ?= python3

.PHONY: install test test-raw ci clean

install:            ## install test dependencies
	$(PY) -m pip install -r requirements.txt

test:               ## run the suite; known defects reported as strict xfail -> green while defects are open
	$(PY) -m pytest -v --junitxml=ci/junit_report.xml

test-raw:           ## ignore the xfail markers and show every raw failure
	$(PY) -m pytest -v --runxfail --junitxml=ci/junit_report_raw.xml

ci: install test-raw-allow-fail test   ## what the CI pipeline runs

test-raw-allow-fail:
	-$(PY) -m pytest -v --runxfail --junitxml=ci/junit_report_raw.xml

clean:
	rm -rf .pytest_cache tests/__pycache__ src/__pycache__
