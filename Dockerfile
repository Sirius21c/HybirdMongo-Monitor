FROM python:2.7-slim

COPY . HybirdMongo-Monitor
WORKDIR HybirdMongo-Monitor
RUN apt-get update && apt-get install -y git && \
    pip install -r requirements.txt && python setup.py install

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/hybirdmongo-monitor"]
