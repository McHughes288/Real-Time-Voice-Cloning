FROM nvidia/cuda:10.1-base-ubuntu18.04 AS base

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    root=/work
LABEL maintainer="johnh@speechmatics.com"
WORKDIR /app

RUN apt update \
    && apt install -y software-properties-common \
    && add-apt-repository ppa:jonathonf/python-3.7 \
    && apt update \
    && apt install -y --no-install-recommends \
        build-essential \
        python3.7 \
        python3-setuptools \
        python3.7-dev \
        wget \
        git \
        make \
        netbase \
    && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*

COPY requirements-base.txt .
RUN wget https://bootstrap.pypa.io/get-pip.py \
    && python3.7 get-pip.py \
    && rm -f get-pip.py \
    && pip3.7 install --upgrade setuptools pip \
    && pip3.7 install -r requirements-base.txt --no-cache-dir

COPY inference ./inference
COPY apis ./apis
COPY run_batch ./

## APP Image
FROM base AS app

COPY build/models/encoder.pt /model/encoder.pt
COPY build/models/synthesizer /model/synthesizer
COPY build/models/vocoder.pt /model/vocoder.pt
COPY build/hashes .

ENTRYPOINT [ "python3.7" ]
