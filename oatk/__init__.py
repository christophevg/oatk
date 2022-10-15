__version__ = "0.0.2"

import logging
logger = logging.getLogger(__name__)

import json
import uuid

import jwt
from authlib.jose import jwk

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from functools import wraps
from flask import request, Response

from oatk import fake

try:
  from AppKit import NSPasteboard, NSStringPboardType
  pb = NSPasteboard.generalPasteboard()
except ModuleNotFoundError:
  logger.debug("No AppKit installed, so no MacOS clipboard support!")
  pb = None

class OAuthToolkit():
  def __init__(self):
    self._encoded     = None
    self._certs       = {}
    self._private_key = None
    self._public_key  = None
    self._alg         = "RS256"
    self._kid         = str(uuid.uuid4())
    self._claims      = None
    
    self.server       = fake.server
    self.server.oatk  = self

  @property
  def version(self):
    return __version__

  def with_private(self, path):
    with open(path, "rb") as fp:
      self._private_key = serialization.load_pem_private_key(
        fp.read(),
        password=None,
        backend=default_backend()
      )
    return self

  def with_public(self, path):
    with open(path, "rb") as fp:
      self._public_key = serialization.load_pem_public_key(
        fp.read(),
        backend=default_backend()
      )
    self._certs = { self._kid : self._public_key }
    return self

  @property
  def jwks(self):
    return json.dumps({
      "keys" : [
        jwk.dumps(self._public_key, kty="RSA", alg=self._alg, kid=self._kid)
      ]
    }, indent=2)

  def with_jwks(self, path_or_string_or_obj):
    try:
      with open(path_or_string_or_obj) as fp:
        jwks = json.load(fp)
    except:
      try:
        jwks = json.loads(path_or_string_or_obj)
      except:
        jwks = path_or_string_or_obj
    assert isinstance(jwks, dict)
    self._certs = {
      key["kid"] : jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
      for key in jwks["keys"]
    }
    if jwks["keys"]:
      self._kid = jwks["keys"][0]["kid"]
    return self
  
  def from_clipboard(self):
    encoded = pb.stringForType_(NSStringPboardType)
    if encoded[:6] == "Bearer":
      encoded = clip[7:]
    self._encoded = encoded.strip() # strip to remove trailing newline
    return self

  def from_file(self, path):
    with open(path) as fp:
      self._encoded = fp.read().strip() # strip to remove trailing newline
    return self

  def header(self, token=None):
    if not token:
      token = self._encoded
    return jwt.get_unverified_header(token)

  def claims(self, claimsdict=None, **claimset):
    if claimsdict is None: claimsdict = {}
    self._claims = claimset
    self._claims.update(claimsdict)
    return self

  @property
  def token(self):
    return jwt.encode(
      self._claims, self._private_key, algorithm=self._alg,
      headers={ "kid": self._kid, "alg" : self._alg }
    )

  def validate(self, token=None):
    kid = self.header(token)["kid"]
    alg = self.header(token)["alg"]
    if not token:
      token = self._encoded
    jwt.decode( token, self._certs[kid], algorithms=[alg] )

  def decode(self, token=None):
    if not token:
      token = self._encoded
    return jwt.decode( token, options={"verify_signature": False} )

  def authenticated(self, f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      msg = ""
      try:
        token = request.headers["Authorization"][7:]
        self.validate(token)
        return f(*args, **kwargs)
      except KeyError as ex:
        msg = "Missing Authorization"
      except Exception as e:
        msg = repr(e)
      return Response(msg, 401)
    return wrapper

  def authenticated_with_claims(self, **required_claims):
    def decorator(f):
      @wraps(f)
      def wrapper(*args, **kwargs):
        msg = ""
        try:
          token = request.headers["Authorization"][7:]
          self.validate(token)
          claims = self.decode(token)
          for claim, value in required_claims.items():
            if not claim in claims:
              raise ValueError(f"required claim {claim} is missing")
            if not value in claims[claim]:
              raise ValueError(f"claim {claim} is missing required value")
          return f(*args, **kwargs)
        except KeyError as ex:
          msg = "Missing Authorization"
        except Exception as e:
          msg = repr(e)
        return Response(msg, 401)
      return wrapper
    return decorator
