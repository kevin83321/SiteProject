# FROM ubuntu:latest
FROM python:3-alpine
LABEL author="kevin"
# LABEL description="An example Dockerfile"
LABEL description = 'Dockerfile for Python script which prints Hello, Name'
# RUN apt-get install python
COPY hello-world.py /app/
ENV NAME=Kevin
CMD python /app/hello-world.py