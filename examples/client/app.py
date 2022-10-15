from flask import Flask, render_template

server = Flask(__name__)

@server.route("/", methods=["GET"])
def home():
  return render_template("home.html")
