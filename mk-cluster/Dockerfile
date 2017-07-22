FROM python:3.6.2
MAINTAINER Kevin Zhang <kevz@mit.edu>

RUN pip install bottle trueskill
ADD mk-cluster.py /home/mk-cluster.py
WORKDIR /home

ENTRYPOINT ["python", "mk-cluster.py"]
