# Modified Proteowizard for NFDI4Chem Converter Service
FROM proteowizard/pwiz-skyline-i-agree-to-the-vendor-licenses:latest AS prebuild
RUN apt-get -y update && \
    apt-get -y upgrade || true


RUN apt-get install -y --no-install-recommends --autoremove --fix-missing python3-flask python3-gevent curl python3-pip build-essential python3-dev
RUN pip3 install uWSGI requests python-dotenv pytz 

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

FROM scratch AS msconvert
COPY --from=prebuild / /


ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    CONTAINER_GITHUB=https://github.com/ProteoWizard/container \
    WINEDISTRO=devel \
    WINEVERSION=7.8~focal-1 \
    WINEDEBUG=-all \
    WINEPREFIX=/wineprefix64 \
    WINEPATH=C:\\pwiz;C:\\pwiz\\skyline

# Stage 2: finalize the image
FROM msconvert AS app

WORKDIR "/app"
RUN mkdir -p input_files

COPY main_file.py /app/main_file.py
ENV CPU=1
ENV THREAD=1
ENV SOCKET="4000"
ENV URL=""
EXPOSE ${SOCKET}


CMD ["sh", "-c", "uwsgi --http-socket ${URL}:${SOCKET} --master --processes ${CPU} --threads ${THREAD} -w main_file:app --logto /app/serverlog.log"]


# Add labels for metadata and maitainability
LABEL maintainer="lincoln.sherpa@tu-dresden.de"
LABEL org.opencontainers.image.source="https://git.rwth-aachen.de/linsherpa/msconverter_v2"
LABEL org.opencontainers.image.title="NFDI4Chem MS Converter Image"
LABEL org.opencontainers.image.description="Docker image for conversion processes using Flask, uWSGI, and OpenMS"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL org.opencontainers.image.license_note="This image incorporates components from  proteowizard/pwiz-skyline-i-agree-to-the-vendor-licenses (Apache-2.0). All terms and conditions of the original license apply to this image."
