FROM andrejreznik/python-gdal:stable

RUN apt-get update && \
    apt-get install -y vim

RUN pip install --no-cache-dir pandas xlrd
