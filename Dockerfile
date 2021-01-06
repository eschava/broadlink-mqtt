FROM python:3.7.9

# based on https://github.com/pfichtner/docker-mqttwarn

# install python libraries (TODO: any others?)
#RUN pip install paho-mqtt broadlink

# build /opt/mqttwarn
RUN mkdir -p /opt/broadlink-mqtt
WORKDIR /opt/broadlink-mqtt
RUN mkdir -p /var/log/broadlink

COPY ./requirements.txt /opt/broadlink-mqtt
RUN pip install -r /opt/broadlink-mqtt/requirements.txt


# add user mqttwarn to image
RUN groupadd -r broadlink && useradd -r -g broadlink broadlink
RUN chown -R broadlink:broadlink /opt/broadlink-mqtt
RUN chown -R broadlink:broadlink /var/log/broadlink
#RUN chown -R broadlink /home/broadlink

# process run as mqttwarn user
USER broadlink

# conf file from host
VOLUME ["/opt/broadlink-mqtt/conf"]

# commands dir
VOLUME ["/opt/broadlink-mqtt/commands/"]

# set conf path
ENV BROADLINKMQTTCONFIG="/opt/broadlink-mqtt/conf/mqtt.conf"
ENV BROADLINKMQTTCONFIGCUSTOM="/opt/broadlink-mqtt/conf/custom.conf"

# finally, copy the current code (ideally we'd copy only what we need, but it
#  is not clear what that is, yet)
COPY . /opt/broadlink-mqtt

# run process
CMD python mqtt.py
