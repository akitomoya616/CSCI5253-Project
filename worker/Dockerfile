FROM python:3.7-slim
LABEL MAINTAINER="493984502@qq.com"

# Install required packages
RUN pip install --upgrade pip

# for mysql
RUN apt-get update \
    && apt-get -y install default-libmysqlclient-dev

# for other libraries and mysql-connector
RUN  pip3 install numpy redis pandas pillow mysql-connector-python-rf

WORKDIR /worker

COPY worker.py /worker

ENTRYPOINT ["python3", "./worker.py"]


