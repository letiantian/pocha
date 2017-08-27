install:uninstall
	- python setup.py install --user
	@ echo "ok"
	
uninstall:
	- pip uninstall --yes pocha