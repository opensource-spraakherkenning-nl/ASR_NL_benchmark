#Use Parent image
FROM python:3.7

#Set labels
LABEL maintainer="Rana Klein <rklein@beeldengeluid.nl>"
LABEL Description="ASR-NL-benchmark Toolkit"


# Set working directory
WORKDIR /opt

#Copy requirements into container first to leverage docker cache
COPY ./requirements.txt /opt

#Install requirements
RUN pip install -r requirements.txt

# Build and install all SCTK tools
RUN git clone https://github.com/usnistgov/SCTK \
 && cd SCTK \
 && make config \
 && make all \
 && make install

RUN cp /opt/SCTK/bin/* /usr/local/bin/
COPY . /opt/ASR_NL_benchmark

#install setup.py
WORKDIR /opt/ASR_NL_benchmark
RUN python setup.py install

