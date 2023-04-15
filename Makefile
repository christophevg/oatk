public_key.pem: private_key.pem
	openssl rsa -in $< -outform PEM -pubout -out $@

private_key.pem:
	openssl genrsa -out $@ 2048

certs.json: public_key.pem
	python -m oatk with_public public_key.pem jwks > $@

server: certs.json
	python -m oatk with_private private_key.pem with_jwks certs.json server run

app:
	gunicorn -b 0.0.0.0:5001 -k eventlet -w 1 examples.client.app:server

api:
	gunicorn -b 0.0.0.0:5002 -k eventlet -w 1 examples.web:app

google:
	gunicorn -k eventlet -w 1 examples.google.app:server	

# project management targets below this point...

tag:
	git tag ${TAG} -m "${MSG}"
	git push --tags

.python-version:
	@pyenv virtualenv $$(basename ${CURDIR}) > /dev/null 2>&1 || true
	@pyenv local $$(basename ${CURDIR})
	@pyenv version

requirements: .python-version requirements.txt
	@pip install --upgrade -r requirements.txt > /dev/null

upgrade: requirements
	@pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

test: requirements
	tox

dist: requirements
	rm -rf $@
	python setup.py sdist bdist_wheel

publish-test: dist
	twine upload --repository testpypi dist/*

publish: dist
	twine upload dist/*

coverage: test
	coverage report

docs: requirements
	cd docs; make html
	open docs/_build/html/index.html

PROJECT:=`find . -name '__init__.py' -maxdepth 2 | xargs dirname | grep -v docs`

lint:
	@PYTHONPATH=. pylint ${PROJECT} | tee lint.txt

clean:
	find . -type f -name "*.backup" | xargs rm

.PHONY: dist docs
