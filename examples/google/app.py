# load the environment variables for this setup from .env file
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
load_dotenv(find_dotenv())
load_dotenv(find_dotenv(".env.local"))

import os

from flask import Flask, render_template, Response
from flask_restful import Resource, Api

import oatk.js
from oatk import OAuthToolkit

server = Flask(__name__)

# route to load web app
@server.route("/", methods=["GET"])
def home():
  return render_template("home.html", **os.environ)

# route service oatk.js from the oatk package
@server.route("/oatk.js", methods=["GET"])
def oatk_script():
  return Response(oatk.js.as_src(), mimetype="application/javascript")

# API set up
api = Api(server)

# setup oatk
auth = OAuthToolkit()
auth.using_provider(os.environ["OAUTH_PROVIDER"]);
auth.with_client_id(os.environ["OAUTH_CLIENT_ID"])

def validate_name(name):
  return name == "Christophe VG"

class HelloWorld(Resource):
  @auth.authenticated_with_claims(name=validate_name)
  def get(self):
    return {"hello": "world"}

api.add_resource(HelloWorld, "/api/hello")
