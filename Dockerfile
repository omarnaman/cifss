FROM ubuntu:20.04

WORKDIR /workspace/storage

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    git \
    python3-pip \
    python3-flask \
    libmagic1
RUN rm -rf /var/lib/apt/lists/*

COPY cifss.py cifss.py
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "./cifss.py"]