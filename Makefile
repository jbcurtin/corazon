build-docs:
	pip install sphinx sphinx_rtd_theme sphinx_automodapi pip setuptools -U
	mkdir -p /tmp/docs
	rm -rf /tmp/docs/*
	sphinx-build -b html docs/ /tmp/docs
