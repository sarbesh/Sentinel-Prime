FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    suricata \
    python3 \
    python3-pip \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/log/suricata /var/lib/suricata/rules /etc/suricata

COPY config/suricata.yaml /etc/suricata/suricata.yaml
COPY config/*.config /etc/suricata/
COPY rules/*.rules /var/lib/suricata/rules/
COPY alert-forwarder.py /usr/local/bin/alert-forwarder.py

RUN chmod +x /usr/local/bin/alert-forwarder.py

RUN pip3 install requests

EXPOSE 9000

CMD sh -c "suricata -c /etc/suricata/suricata.yaml --pidfile /var/run/suricata.pid --pcap & \
    sleep 5 && \
    python3 /usr/local/bin/alert-forwarder.py"
