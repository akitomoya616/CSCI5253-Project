FROM xserrat/facebook-demucs:latest
LABEL MAINTAINER="493984502@qq.com"

RUN  pip3 install redis minio soundfile

WORKDIR /worker

COPY worker.py /worker

ENTRYPOINT ["python3", "./worker.py"]


