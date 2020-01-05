FROM ubuntu:eoan

ENV DEBIAN_FRONTEND noninteractive

RUN apt update
Run apt dist-upgrade -y
RUN apt install -y \
    curl \
    gifsicle \
    git \
    optipng \
    python3-setuptools \
    python3-venv \
    unrar

RUN python3 /usr/lib/python3/dist-packages/easy_install.py pip
RUN pip3 install poetry
WORKDIR /opt/picopt/
COPY ci ci
RUN ci/mozjpeg.sh
RUN ci/pngout.sh
COPY . .

# Install
RUN poetry install
