# Installation

This guide contains two alternatives to install NeoFox:
- Building a docker image that automates the installation into a container
- A set of detailed step by step installation instructions without docker

The first approach has the lowest entry barrier to use NeoFox as a command line tool.
While the second provides access to the command line tool and allows the integration of the NeoFox API.

## Build and run the docker image

Clone the repository: `git clone git@github.com:TRON-Bioinformatics/neofox.git`

Move into the neofox folder: `cd neofox`

To download NetMHCpan and NetMHCIIpan, each user must explicitly accept the software license. Thus, we cannot
distribute the software or provide a direct URL to download it. Please make sure to download the right version from 
the sites indicated below.

- NetMHCpan-4.1: https://services.healthtech.dtu.dk/service.php?NetMHCpan-4.1 (`netMHCpan-4.1b.Linux.tar.gz`)
- NetMHCIIpan-4.0: https://services.healthtech.dtu.dk/software.php (`netMHCIIpan-4.0.Linux.tar.gz`)

Store these in the root folder of the repository, next to the `Dockerfile`. Do not rename the installer files.

Build the docker image: `docker build --tag neofox-docker .`

Run NeoFox: `docker run neofox-docker neofox --help`

See the usage guide [here](03_03_usage.md) for further details.


## Step by step guide without docker

These installation instructions were tested on Ubuntu 18.04.

Python >=3.7, <=3.8 and R 3.6.0 should be preinstalled.

Set the environment variable pointing to `Rscript`.
```
export NEOFOX_RSCRIPT=`which Rscript`
```

### Install NeoFox

```
pip install neofox
```

### Install third-party dependencies

#### Install BLASTP

The version of BLASTP that was tested is 2.10.1, other versions may work but that is untested.
```
wget https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.10.1/ncbi-blast-2.10.1+-x64-linux.tar.gz
tar -xvf ncbi-blast-2.10.1+-x64-linux.tar.gz
export NEOFOX_BLASTP=`pwd`/ncbi-blast-2.10.1+/bin/blastp
```

#### Install NetMHCpan-4.1

NetMHCpan-4.1 can be downloaded by academic users from https://services.healthtech.dtu.dk/service.php?NetMHCpan-4.1

```
tar -xvf netMHCpan-4.1b.Linux.tar.gz
cd netMHCpan-4.1
wget https://services.healthtech.dtu.dk/services/NetMHCpan-4.1/data.tar.gz
tar -xvf data.tar.gz
cd ..
export NEOFOX_NETMHCPAN=`pwd`/netMHCpan-4.1/netMHCpan
```

Configure NetMHCpan as explained in the file `netMHCpan-4.1/netMHCpan-4.1.readme`


#### Install NetMHCIIpan-4.0

NetMHCIIpan-4.0 can be downloaded by academic users from https://services.healthtech.dtu.dk/software.php

```
tar -xvf netMHCIIpan-4.0.Linux.tar.gz
cd netMHCIIpan-4.0
# download the data
wget http://www.cbs.dtu.dk/services/NetMHCIIpan-4.0/data.Linux.tar.gz
tar -xvf data.Linux.tar.gz
cd ..
export NEOFOX_NETMHC2PAN=`pwd`/netMHCIIpan-4.0/netMHCIIpan
# install tcsh shell interpreter if not available yet
sudo apt-get install tcsh
```

Configure NetMHCIIpan-4.0 as explained in the file `netMHCIIpan-4.0/netMHCIIpan-4.0.readme`
         

#### Install MixMHCpred-2.1 (recommended but optional)

```
wget https://github.com/GfellerLab/MixMHCpred/archive/v2.1.tar.gz
tar -xvf v2.1.tar.gz
export NEOFOX_MIXMHCPRED=`pwd`/MixMHCpred-2.1/MixMHCpred
```

Configure MixMHCpred-2.1 as explained in the file `MixMHCpred-2.1/README`

#### Install MixMHC2pred-1.2 (recommended but optional)

```
wget https://github.com/GfellerLab/MixMHC2pred/archive/v1.2.tar.gz
tar -xvf v1.2.tar.gz
export NEOFOX_MIXMHC2PRED=`pwd`/MixMHC2pred-1.2/MixMHC2pred_unix
```

#### PRIME-1.0 (recommended but optional)

```
wget https://github.com/GfellerLab/PRIME/archive/master.tar.gz
tar -xvf master.tar.gz
export NEOFOX_PRIME==`pwd`/PRIME-master/PRIME
```

Configure PRIME as explained in the file `PRIME-master/README`

### Configuration of the reference folder 

To configure the reference folder, set the environment variable for `makeblastdb`, NetMHCpan, NetMHCIIpan and Rscript:

```
export NEOFOX_MAKEBLASTDB=`pwd`/ncbi-blast-2.10.1+/bin/makeblastdb
export NEOFOX_RSCRIPT=`which Rscript`
export NEOFOX_NETMHCPAN=`pwd`/netMHCpan-4.1/netMHCpan
export NEOFOX_NETMHC2PAN=`pwd`/netMHCIIpan-4.0/netMHCIIpan
```

Furthermore, a list of available MHC alleles is required. Optionally, you can provide the URL to the IPD-IMGT/HLA database CSV table, see releases here https://www.ebi.ac.uk/ipd/imgt/hla/docs/release.html. 
If not provided the default value is the latest version at the time of this writing https://raw.githubusercontent.com/ANHIG/IMGTHLA/Latest/Allelelist.3430.txt

```
export NEOFOX_HLA_DATABASE=https://raw.githubusercontent.com/ANHIG/IMGTHLA/Latest/Allelelist.3430.txt
```

Run the following to configure the NeoFox reference folder:
```
neofox-configure --reference-folder /your/neofox/folder [--install-r-dependencies]
```

The above command will install several resources and store in the annotations metadata their version, MD5 checksum and 
download timestamp.

Unless indicated to the installer by flag `--install-r-dependencies` you will need to install manually some R packages. These packages are the following:
```
lattice
ggplot2
caret
Peptides
doParallel
gbm
Biostrings
```

Add the reference folder to the Path
```
export NEOFOX_REFERENCE_FOLDER=path/to/reference/folder
```

## Test installation   

The user can test if all the installations have been successful by testing NeoFox with some test data. 
The test data can be downloaded here:

* [test_data.tsv](_static/test_data.tsv)
* [test_patients.tsv](_static/test_patients.tsv)

````commandline
neofox --candidate-file /path/to/test_data.txt --patient-data /path/to/test_patients.txt --output-folder  /path/to/outputfolder --with-table --with-json --output-prefix test
````

The resulting output files can be compared to the following test output files:

* [test_neoantigen_candidates_annotated.tsv](_static/test_neoantigen_candidates_annotated.tsv)
* [test_neoantigen_candidates_annotated.json](_static/test_neoantigen_candidates_annotated.json)

