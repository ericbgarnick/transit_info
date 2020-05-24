# base image
FROM python:3.7-buster

# set the working directory
WORKDIR /usr/src/mbta_info

# copy app directory
COPY mbta_info ./

# install Python modules needed by the Python app
RUN pip3 install --no-cache-dir -r requirements.txt
