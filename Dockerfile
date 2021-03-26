FROM python:3.7-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# copy over Neofox package
COPY neofox neofox
COPY setup.py setup.py
COPY MANIFEST.in MANIFEST.in
COPY setup.cfg setup.cfg
COPY requirements.txt requirements.txt
COPY LICENSE LICENSE
COPY README.md README.md
# these two files will need to be downloaded from the owner's site after agreeing their license
COPY netMHCIIpan-3.2.Linux.tar.gz netMHCIIpan-3.2.Linux.tar.gz
COPY netMHCpan-4.0a.Linux.tar.gz netMHCpan-4.0a.Linux.tar.gz

# build and install neofox package
RUN python3 setup.py bdist_wheel
RUN pip3 install dist/*.whl

# install R
RUN apt-get update && apt-get install -y --no-install-recommends r-base
ENV NEOFOX_RSCRIPT /usr/bin/Rscript

# install BLASTP
RUN apt-get install -y --no-install-recommends wget
RUN wget https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.10.1/ncbi-blast-2.10.1+-x64-linux.tar.gz
RUN tar -xvf ncbi-blast-2.10.1+-x64-linux.tar.gz
ENV NEOFOX_BLASTP /app/ncbi-blast-2.10.1+/bin/blastp
RUN echo $NEOFOX_BLASTP
ENV NEOFOX_MAKEBLASTDB /app/ncbi-blast-2.10.1+/bin/makeblastdb
RUN echo $NEOFOX_MAKEBLASTDB

# install netmhcpan
RUN tar -xvf netMHCpan-4.0a.Linux.tar.gz
RUN echo $NEOFOX_MAKEBLASTDB
RUN sed -i 's/\/usr\/cbs\/packages\/netMHCpan\/4.0\/netMHCpan-4.0/\/app\/netMHCpan-4.0/g' /app/netMHCpan-4.0/netMHCpan
RUN sed -i 's/\/scratch/\/app\/netMHCpan-4.0\/tmp/g' /app/netMHCpan-4.0/netMHCpan
RUN mkdir /app/netMHCpan-4.0/tmp
RUN wget http://www.cbs.dtu.dk/services/NetMHCpan-4.0/data.Linux.tar.gz  -O /app/netMHCpan-4.0/data.Linux.tar.gz
RUN tar -xvf /app/netMHCpan-4.0/data.Linux.tar.gz -C /app/netMHCpan-4.0
ENV NEOFOX_NETMHCPAN /app/netMHCpan-4.0/netMHCpan

# install netmhc2pan
RUN tar -xvf netMHCIIpan-3.2.Linux.tar.gz
RUN sed -i 's/\/usr\/cbs\/bio\/src\/netMHCIIpan-3.2/\/app\/netMHCIIpan-3.2/g' /app/netMHCIIpan-3.2/netMHCIIpan
RUN sed -i 's/\/scratch/\/app\/netMHCIIpan-3.2\/tmp/g' /app/netMHCIIpan-3.2/netMHCIIpan
RUN mkdir /app/netMHCIIpan-3.2/tmp
RUN wget http://www.cbs.dtu.dk/services/NetMHCIIpan-3.2/data.Linux.tar.gz -O /app/netMHCIIpan-3.2/data.Linux.tar.gz
RUN tar -xvf /app/netMHCIIpan-3.2/data.Linux.tar.gz -C /app/netMHCIIpan-3.2
ENV NEOFOX_NETMHC2PAN /app/netMHCIIpan-3.2/netMHCIIpan
RUN apt-get install tcsh

# install mixmhcpred
RUN wget https://github.com/GfellerLab/MixMHCpred/archive/v2.1.tar.gz
RUN tar -xvf v2.1.tar.gz
RUN sed -i 's/"YOUR PATH TO MixMHCpred\/lib FOLDER"/\/app\/MixMHCpred-2.1\/lib/g' /app/MixMHCpred-2.1/MixMHCpred
RUN apt-get install -y --no-install-recommends g++
RUN g++ -O3 /app/MixMHCpred-2.1/lib/MixMHCpred.cc -o /app/MixMHCpred-2.1/lib/MixMHCpred.x
ENV NEOFOX_MIXMHCPRED /app/MixMHCpred-2.1/MixMHCpred

# install mixmhc2pred
RUN wget https://github.com/GfellerLab/MixMHC2pred/archive/v1.2.tar.gz
RUN tar -xvf v1.2.tar.gz
ENV NEOFOX_MIXMHC2PRED /app/MixMHC2pred-1.2/MixMHC2pred_unix

# configure references
RUN apt-get install -y --no-install-recommends build-essential
RUN neofox-configure --reference-folder /app/neofox-reference --install-r-dependencies
ENV NEOFOX_REFERENCE_FOLDER /app/neofox-reference