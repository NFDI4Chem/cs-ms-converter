FROM ubuntu:22.04
RUN apt-get update && \
    apt-get install -y apt-utils && \
    apt-get -y install systemd && \
    apt-get install -qy curl && \
    apt-get install -y nodejs && \
    apt-get install -y python3-pip &&\
    apt-get install -y git

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV THREAD=1
ENV CPU=1
ENV MSCONVERT_URL="http://nfdi4chem-ms-msconvert:4000"
ENV VALIDATION_URL="http://nfdi4chem-ms-validation:3000"
RUN mkdir /app
WORKDIR /app
RUN git clone https://git.rwth-aachen.de/linsherpa/mzml_metadataextractor.git /app/mzml_metadataextractor


COPY rest_api.py /app/rest_api.py

RUN mkdir -p input_files

RUN chmod 777 -R /tmp
RUN pip install --no-cache-dir uWSGI flask apiflask boto3 python-dotenv flask-cors requests pytz marshmallow "lxml>=4.9.0" "rich>=13.0.0"
EXPOSE 5000


CMD ["sh", "-c", "uwsgi --http-socket :5000 --master --processes ${CPU} --threads ${THREAD} -w rest_api:app --logto /app/serverlog.log"]



# Add labels for metadata and maitainability
LABEL maintainer="lincoln.sherpa@tu-dresden.de"
LABEL org.opencontainers.image.source="https://git.rwth-aachen.de/linsherpa/msconverter_v2"
LABEL org.opencontainers.image.title="NFDI4Chem MS Converter Image"
LABEL org.opencontainers.image.description="Docker image for conversion processes using Flask, uWSGI, and OpenMS"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.licenses="MIT"
