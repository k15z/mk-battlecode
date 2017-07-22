FROM gradle
MAINTAINER Kevin Zhang <kevz@mit.edu>

USER root

RUN apt-get update && \
    apt-get -y install python3-pip && \
    apt-get clean && \
    pip3 install requests

RUN git clone https://github.com/battlecode/battlecode-scaffold-2017 /home/battlecode && \
    cd /home/battlecode && \
    gradle build

ADD mk-worker.py /home/battlecode/mk-worker.py
WORKDIR /home/battlecode

ENTRYPOINT ["python3", "mk-worker.py"]
