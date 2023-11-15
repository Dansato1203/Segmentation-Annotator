FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -yqq \
	&& apt-get upgrade -y \
	&& apt-get install -y --no-install-recommends \
	ca-certificates \
	python3 \
	python3-pip \
	python3-pyqt5 \
	libglib2.0-0 \
	mesa-common-dev  \
	libglu1-mesa-dev \
	mesa-utils \
	x11-apps \
	&& rm -rf /var/lib/apt/lists/*


WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install -r requirements.txt

COPY scripts /app/scripts

CMD ["python3", "scripts/main.py"]
