private_key.pem:
	openssl genrsa -out $@ 2048

public_key.pem: private_key.pem
	openssl rsa -in $< -outform PEM -pubout -out $@

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
