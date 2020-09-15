# Installation instructions

This installation instructions were tested on Ubuntu 18.04.

Python 3.7 and R 3.6.0 should be preinstalled.

R requires the following libraries:
```
lattice
ggplot2
caret
Peptides
doParallel
gbm
```

Set the environment variable pointing to `Rscript`.
```
export NEOFOX_RSCRIPT=`which Rscript`
``` 

## Install third-party dependencies

### Install BLASTP

The version of BLASTP that was tested is 2.8.1, other versions may work but that is untested.
```
wget https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.8.1/ncbi-blast-2.8.1+-x64-linux.tar.gz
tar -xvf ncbi-blast-2.8.1+-x64-linux.tar.gz
export NEOFOX_BLASTP=`pwd`/ncbi-blast-2.8.1+/bin/blastp
```

### Install NetMHCpan 4.0

NetMHCpan 4.0 can be downloaded by academic users from https://services.healthtech.dtu.dk/service.php?NetMHCpan-4.0

```
tar -xvf netMHCpan-4.0a.Linux.tar.gz
cd netMHCpan-4.0
wget http://www.cbs.dtu.dk/services/NetMHCpan-4.0/data.Linux.tar.gz
tar -xvf data.Linux.tar.gz
cd ..
export NEOFOX_NETMHCPAN=`pwd`/netMHCpan-4.0/netMHCpan
```

Configure NetMHCpan as explained in the file `netMHCpan-4.0/netMHCpan-4.0.readme`


### Install NetMHC2pan 3.2

NetMHC2pan can be downloaded by academic users from https://services.healthtech.dtu.dk/software.php

```
tar -xvf netMHCIIpan-3.2.Linux.tar.gz
cd netMHCIIpan-3.2
# download the data
wget http://www.cbs.dtu.dk/services/NetMHCIIpan-3.2/data.Linux.tar.gz
tar -xvf data.Linux.tar.gz
cd ..
export NEOFOX_NETMHC2PAN=`pwd`/netMHCIIpan-3.2/netMHCIIpan
# install tcsh shell interpreter if not available yet
sudo apt-get install tcsh
```

Configure NetMHCpan as explained in the file `netMHCIIpan-3.2/netMHCIIpan-3.2.readme`
         

### Install MixMHCpred 2.0.1

```
wget https://github.com/GfellerLab/MixMHCpred/archive/v2.0.1.tar.gz
tar -xvf v2.0.1.tar.gz
export NEOFOX_MIXMHCPRED=`pwd`/MixMHCpred-2.0.1/MixMHCpred
```

Configure MixMHCpred as explained in the file `MixMHCpred-2.0.1/README`

### Install MixMHC2pred 1.1.3

```
wget https://github.com/GfellerLab/MixMHC2pred/archive/v1.1.tar.gz
tar -xvf v1.1.tar.gz
export NEOFOX_MIXMHC2PRED=`pwd`/MixMHC2pred-1.1/MixMHC2pred_unix
```

## Install references

For building the reference data we will need `makeblastdb`, set the environment variable required for building the reference:

```
export NEOFOX_MAKEBLASTDB=`pwd`/ncbi-blast-2.8.1+/bin/makeblastdb
```

Run the script in the neofox repository `neofox/references/build_references.sh` from your reference folder.