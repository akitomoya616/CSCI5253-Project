FROM python:3.6-alpine
LABEL MAINTAINER="493904592@qq.com"

RUN  pip3 install --upgrade redis minio flask jsonpickle requests

WORKDIR /srv

COPY    rest-server.py /srv

EXPOSE 5000
CMD [ "python", "rest-server.py"]
