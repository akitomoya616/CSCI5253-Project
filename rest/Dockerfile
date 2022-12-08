FROM python:3.6-alpine
LABEL MAINTAINER="493904592@qq.com"

RUN  pip3 install --upgrade pip redis minio flask jsonpickle requests

WORKDIR /srv

COPY    rest-server.py /srv

# For testing on local environment ONLY - don't forget to re-make build and push after un-comment these!
# EXPOSE 5000
# CMD [ "python", "rest-server.py"]

# For testing on GKE
CMD [ "python3", "rest-server.py", "--host", "0.0.0.0"]
