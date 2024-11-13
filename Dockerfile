# This file is only needed for testing Python 3.14 whose image contains no cffi.
# (As a comparison, the official python:3.13-slim works out of the box.)

# TODO: Can this Dockerfile use multi-stage build?
# https://testdriven.io/tips/6da2d9c9-8849-4386-b7f9-13b28514ded8/
FROM python:3.14.0a2-slim

RUN apt-get update && apt-get install -y \
  gcc \
  libffi-dev

