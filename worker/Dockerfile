FROM python:3.7-slim
LABEL MAINTAINER="493984502@qq.com"

# Install required packages
RUN pip install --upgrade pip

# for mysql
RUN apt-get update \
    && apt-get -y install default-libmysqlclient-dev

# for other libraries and mysql-connector
RUN  pip3 install numpy redis matplotlib pandas pillow mysql-connector-python-rf 

WORKDIR /worker

COPY worker.py /worker

# RUN docker run -e MYSQL_ROOT_PASSWORD=test1234 -d -p 3306:3306 mysql:5.6

ENTRYPOINT ["python3", "./worker.py"]


