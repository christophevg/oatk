import os

script: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), "oatk.js")
with open(script) as file:
  src: str = file.read()


def as_src() -> str:
  return src
