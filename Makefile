PYTHON = python

.PHONY: default install rebuild build uninstall reinstall clean test

default:
	make rebuild
	make install
	make clean
	make test

reinstall:
	make uninstall
	make rebuild
	make install
	make clean

install: dist/*.whl
	$(PYTHON) -m pip install dist/*.whl
	$(PYTHON) -m pip show markdown_link_attr_modifier

uninstall:
	$(PYTHON) -m pip uninstall -y markdown_link_attr_modifier

rebuild build dist/*.whl: ./setup.py ./markdown_link_attr_modifier.py
	# make sure clean old versions
	make clean

	$(PYTHON) ./setup.py bdist_wheel

	# 'pip install' is buggy when .egg-info exist
	rm -rf *.egg-info build

clean:
	rm -rf *.egg-info build dist

test: ./markdown_link_attr_modifier.py
	$(PYTHON) ./markdown_link_attr_modifier.py -vv
