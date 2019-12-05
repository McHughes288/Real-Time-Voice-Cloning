.DEFAULT_GOAL=all
includes="apis *.py"

all: deps check

deps:
	./scripts/setup.sh
build:
	./scripts/build.sh
check:
	black --check "${includes}"
	# flake8 --max-line-length=100 "${includes}"
	pylint "${includes}"
clean:
	$(RM) -r $(wildcard ut_*.xml) $(cov_dir) .pytest_cache .coverage exp models logs
	find . -name '*.pyc' -delete
	find . -name __pycache__ -delete
format:
	black "${includes}"