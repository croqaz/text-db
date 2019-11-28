
ENV=

clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*.rej' `
	rm -rf *.egg-info
	rm -f .coverage
	rm -rf coverage
	rm -rf build
	rm -rf cover
	python3 setup.py clean

update:
	${ENV}pip install -U -r requirements.txt

lint:
	${ENV}flake8 tdb
	${ENV}mypy --ignore-missing-imports tdb

coverage:
	${ENV}pytest --cov-report term --cov=tdb/ tests/

test:
	${ENV}pytest -ra -sv tests/
