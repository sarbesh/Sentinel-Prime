FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    jq \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip3 install opencanary

RUN mkdir -p /var/log/opencanary /home/opencanary

COPY config/opencanary.conf /home/opencanary/opencanary.conf
COPY event-forwarder.py /usr/local/bin/event-forwarder.py

RUN chmod +x /usr/local/bin/event-forwarder.py

RUN opencanaryd --createuser --username admin --password admin --allow-run-as-root

EXPOSE 21 22 23 80 443 445 3306 5432 8080 8888

CMD sh -c "opencanaryd --start & \
    sleep 3 && \
    python3 /usr/local/bin/event-forwarder.py"
