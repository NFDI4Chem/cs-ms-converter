# Modified OpenMS Image for Converter Service
FROM biocontainers/openms:2.2.0_cv6 AS prebuild
RUN apt-get -y update && \
    apt-get -y upgrade || true


FROM scratch AS msconvert
COPY --from=prebuild / /



# Stage 2: finalize the image
FROM msconvert AS app
RUN apt-get -y update && \
    apt-get install -y software-properties-common

RUN apt-get install -y --no-install-recommends --autoremove --fix-missing python3-setuptools python3-flask python3-gevent curl python3-pip build-essential python3-dev
RUN pip3 install uWSGI
RUN pip3 cache purge || true

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR "/app"
RUN mkdir -p input_files

COPY main_file.py /app/main_file.py
ENV CPU=1
ENV THREAD=1
ENV SOCKET="3000"
ENV URL=""
EXPOSE ${SOCKET}



CMD ["sh", "-c", "uwsgi --http-socket ${URL}:${SOCKET} --master --processes ${CPU} --threads ${THREAD} -w main_file:app --logto /app/serverlog.log"]

# Add labels for metadata and maitainability
LABEL maintainer="lincoln.sherpa@tu-dresden.de"
LABEL org.opencontainers.image.source="https://git.rwth-aachen.de/linsherpa/msconverter_v2"
LABEL org.opencontainers.image.title="NFDI4Chem Validation Image"
LABEL org.opencontainers.image.description="Docker image for validation processes using Flask, uWSGI, and OpenMS"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.license_note="This image incorporates components from biocontainers/openms:2.2.0_cv6 (Apache-2.0). All terms and conditions of the original license apply to this image."