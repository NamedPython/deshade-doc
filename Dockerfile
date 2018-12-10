FROM jjanzic/docker-python3-opencv

ENV LANG C.UTF-8

RUN pip install --upgrade pip
RUN pip install \
  pillow

WORKDIR /app