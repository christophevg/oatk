# load the environment variables for this setup from .env file
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
load_dotenv(find_dotenv())
load_dotenv(find_dotenv(".env.local"))

import os

from flask import Flask, render_template
from flask_restful import Resource, Api

from oatk import OAuthToolkit

server = Flask(__name__)

# route to load web app
@server.route("/", methods=["GET"])
def home():
  return render_template("home.html", **os.environ)

# API set up
api = Api(server)

# setup oatk
oatk = OAuthToolkit()
oatk.using_provider(os.environ["OAUTH_PROVIDER"]);
oatk.with_client_id(os.environ["OAUTH_CLIENT_ID"])

def validate_name(name):
  return name == "Christophe VG"

class HelloWorld(Resource):
  @oatk.authenticated_with_claims(name=validate_name)
  def get(self):
    return {"hello": "world"}

api.add_resource(HelloWorld, "/api/hello")
