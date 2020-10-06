PYTHON = python3

.PHONY: default reinstall install upload uninstall rebuild build clean test

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

upload: dist/*.whl dist/*.tar.gz
	$(PYTHON) -m twine check dist/*.whl dist/*.tar.gz
	# username is: __token__
	$(PYTHON) -m twine upload dist/*.whl dist/*.tar.gz

uninstall:
	$(PYTHON) -m pip uninstall -y markdown_link_attr_modifier

rebuild build dist/*.whl dist/*.tar.gz: ./setup.py ./markdown_link_attr_modifier.py
	# make sure clean old versions
	make clean

	$(PYTHON) ./setup.py sdist bdist_wheel --universal

	# 'pip install' is buggy when .egg-info exist
	rm -rf *.egg-info build

clean:
	rm -rf *.egg-info build dist

test: ./markdown_link_attr_modifier.py
	$(PYTHON) ./markdown_link_attr_modifier.py -vv
