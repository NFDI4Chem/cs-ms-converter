# Stage 0: import this for later
#FROM lincoln1010/pwiz-skyline-i-agree-to-the-vendor-licenses:v1.0 as chemotion-build-base

# Stage 1: prepare the base image
# hadolint ignore=DL3006
#FROM chambm/pwiz-skyline-i-agree-to-the-vendor-licenses as prebuild
FROM biocontainers/openms:2.2.0_cv6 AS prebuild
RUN apt-get -y update && \
    apt-get -y upgrade || true


#RUN apt-get install -y --no-install-recommends --autoremove --fix-missing python3-flask python3-gevent curl python3-pip build-essential python3-dev
#RUN pip3 install uWSGI

#RUN apt-get clean && \
#    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

FROM scratch AS msconvert
COPY --from=prebuild / /



# Stage 2: finalize the image
FROM msconvert AS app
#RUN apt-get -y update && \
#    apt-get install -y software-properties-common
#RUN apt-get install -y --no-install-recommends --autoremove --fix-missing python3-setuptools python3-flask python3-gevent curl python3-pip build-essential python3-dev
#RUN pip3 install uWSGI python-dotenv requests boto3
#RUN pip3 cache purge || true


# 1. tools needed to compile Python
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
        libsqlite3-dev libffi-dev libncurses5-dev libgdbm-dev liblzma-dev \
        tk-dev wget ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 2. build & install Python 3.9 to /usr/local
ARG PY=3.9.19
RUN wget -q https://www.python.org/ftp/python/${PY}/Python-${PY}.tgz && \
    tar xzf Python-${PY}.tgz && \
    cd Python-${PY} && \
    ./configure --enable-optimizations --with-ensurepip=install && \
    make -j$(nproc) altinstall && \
    cd / && rm -rf Python-${PY}*

# 3. make python3 point to the new binary
RUN ln -sf /usr/local/bin/python3.9 /usr/local/bin/python3 && \
    ln -sf /usr/local/bin/pip3.9 /usr/local/bin/pip3

# 4. install your packages
RUN python3 -m pip install --no-cache-dir \
        uWSGI flask python-dotenv requests boto3

# 6. clean-up
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


WORKDIR "/app"
RUN mkdir -p input_files

COPY main_file.py /app/main_file.py
COPY credentials /app/credentials
ENV CPU=1
ENV THREAD=1
ENV SOCKET="3000"
ENV URL=""
EXPOSE ${SOCKET}


#CMD ["python3", "/app/main_file.py"]
CMD ["sh", "-c", "uwsgi --http-socket ${URL}:${SOCKET} --master --processes ${CPU} --threads ${THREAD} -w main_file:app --logto /app/serverlog.log"]

# Add labels for metadata and maitainability
LABEL maintainer="lincoln.sherpa@tu-dresden.de"
LABEL org.opencontainers.image.source="https://git.rwth-aachen.de/linsherpa/msconverter_v2"
LABEL org.opencontainers.image.title="NFDI4Chem Validation Image"
LABEL org.opencontainers.image.description="Docker image for validation processes using Flask, uWSGI, and OpenMS"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.license_note="This image incorporates components from biocontainers/openms:2.2.0_cv6 (Apache-2.0). All terms and conditions of the original license apply to this image."