From ubuntu:22.04
RUN apt-get update && \
    apt-get -qy full-upgrade && \
    apt-get -y install systemd && \
    apt-get install -qy curl && \
    apt-get install -y nodejs && \
    apt-get install -y docker.io && \
    apt-get install -y python3-pip && \
    pip3 install cwltool

RUN apt-get install python3.9 -y

RUN pip3 install cwltool


# once available add cwltest https://packages.ubuntu.com/search?keywords=cwltest&searchon=names&suite=all&section=all

# ADD . /placeinsidethecontainer
# ENTRYPOINT flask
