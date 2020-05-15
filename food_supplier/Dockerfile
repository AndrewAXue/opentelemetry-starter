# Dockerfile
FROM python:3.7-stretch
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r dock_reqs.txt
ENTRYPOINT ["python"]
CMD ["FoodSupplier.py"]
