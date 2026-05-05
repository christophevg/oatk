import json
import logging
from datetime import datetime
from typing import Any, Optional

import flask_restful
from flask import Flask
from flask_cors import CORS

logger = logging.getLogger(__name__)


class OATKFlask(Flask):
  def __init__(self, *args: Any, **kwargs: Any) -> None:
    Flask.__init__(self, *args, **kwargs)
    self._oatk: Optional[Any] = None

  @property
  def oatk(self) -> Optional[Any]:
    return self._oatk

  @oatk.setter
  def oatk(self, o: Any) -> None:
    self._oatk = o
    from . import routes  # since our routes refer to server.oath # noqa: F401


server = OATKFlask(__name__)
CORS(server, resources={r"*": {"origins": "*"}})
api = flask_restful.Api(server)

server.secret_key = "sikrit"  # to enable sessions


class Encoder(json.JSONEncoder):
  def default(self, o: Any) -> Any:
    if isinstance(o, datetime):
      return o.isoformat()
    if isinstance(o, set):
      return list(o)
    return super().default(o)


server.config["RESTFUL_JSON"] = {"indent": 2, "cls": Encoder}
