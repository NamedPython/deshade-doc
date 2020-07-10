FROM jjanzic/docker-python3-opencv:contrib-opencv-3.4.2

ENV LANG C.UTF-8

RUN pip install --upgrade pip
RUN pip install \
  pillow

WORKDIR /app