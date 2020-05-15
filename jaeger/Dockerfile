# Dockerfile
FROM python:3.7-stretch
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
CMD ["./jaeger-all-in-one --collector.zipkin.http-port=9411 --query.port=$PORT"]
