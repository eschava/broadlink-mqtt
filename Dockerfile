FROM debian:stretch

RUN apt-get update && apt-get install -y\
    git build-essential python-pip

RUN git clone https://github.com/TechForze/broadlink-mqtt

WORKDIR /broadlink-mqtt

RUN pip install -r /broadlink-mqtt/requirements.txt

CMD ["python", "/broadlink-mqtt/mqtt.py"]