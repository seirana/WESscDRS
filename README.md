!! UNDER CONSTRUCTION!
# WESscDRS
WESscDRS is designed to link scRNA-seq with polygenic disease risk at the single-cell resolution, independent of annotated cell types, and suggest drugs for the disease.  

It provides comprehensive functionalities for:  
 - WESscDRS Identifying cells exhibiting excess expression across disease-associated genes implicated by Whole Exome Sequencing (WES).  

In the [Quick Start](#quick-start) section, you can follow the instructions to install the requirements and run simple samples.
To learn more about the functions, refer to the [Documentations](#documentations). Additionally, there, you can find detailed instructions on the data type and formats required as input for the WESscDRS function.
 
# Table of contents
- [Pipeline structure](#pipeline-structure)
- [Key features](#key-features)

- [Quick Start](#quick-start)
	- [Prerequisites and Configuration](#prerequisites-and-configuration)
    	- [Pre-configuration](#pre-configuration)
    	- [Custom configuration](#custom-configuration)
	- [Installing dependencies](#installing-dependencies)
		- [Step 1: Install pipeline](#step-1-Install-pipeline)
		- [Step 2: Install Singularity ](#step-2-Install-singularity)
    	- [step 3: Install dependent software for WESscDRS](#step-3-install-dependent-software-for-WESscDRS)
     - [Downloads](#downloads)
       - [Downloading WESscDRS](#downloading-WESscDRS)
       - [Downloading input data_for WESscDRS](#downloading-input-data-for-WESscDRS)
     - [Example workflows](#example-workflows)
		- [Running WESscDRS](#running-WESscDRS)
- [Documentation](#documentation)
- [Funding](#funding)
  
# Pipeline Structure
![Image Alt Text](https://github.com/seirana/WESscDRS/blob/main/Images/Pipeline%20Structure.png)

# Quick Start
## Prerequisites and Configuration
WESscDRS requires significant computational resources. Ensure your system meets the following minimum requirements:

CPU: At least 16 cores.    
RAM: At least 32 GB (e.g., WESscDRS may require up to 360 GB).

Note: For large datasets, it is recommended to run the pipeline on a high-performance computing (HPC) system.

### Custom configuration
To fully utilize WESscDRS on an HPC or other systems, you must create a custom configuration file specifying:

Available CPU cores and memory.
Scheduler settings (e.g., local or SLURM).
Paths for reference databases.
Please refer to the installation and configuration documentation for more details.

## Downloads
### Clone WESscDRS  and install 
All the codes and needed files for the sample file will be downloaded in this step.

1. Make a folder where you want to keep data and files for the WESscDRS project.
For example, make a folder named WESscDRS in the home directory.
```bash
cd /home
mkdir -p WESscDRS
```
2. Clone the GitHub repo into that folder
```bash
cd /home/WESscDRS
git clone https://github.com/seirana/WESscDRS.git
```
3. If you get an error like “destination path 'WESscDRS' already exists”.
```bash
cd /home/WESscDRS
git pull --rebase origin main
```
## Installing dependencies
WESscDRS needs some extra software to run:
### step 1: Install scDRS
Pipeline will install it. If there is a problem, check [their page](https://pypi.org/project/scdrs/).
### step 2: Install the bcftools
Pipeline will install it. If there is a problem, check [here](https://samtools.github.io/bcftools/howtos/install.html).
### step 3: Install MAGMA
This installation must be done manually.

Select and install the correct version for your operating system and desired genome reference from [here](https://cncr.nl/research/magma/).

**This command installs Python libraries, scDRS, and bcftools
```bash
cd /home/WESscDRS
bash setup_dependencies.sh
```

### Running WESscDRS	
```bash
pipeline run ikmb/WESscDRS \
    -profile custom \
    -c WESscDRS.config \
    --reads '*_R{1,2}.fastq.gz' \
    --metaphlan \
    --updatemetaphlan \
    --metaphlan_db '/path/to/store/metaphlan/db' \
    --outdir results
```
	
# Documentations 
All further documentation about the pipeline can be found in the [docs/](https://github.com/seirana/WESscDRS/blob/main/docs) directory under the links below:
* [WESscDRS](https://github.com/seirana/WESscDRS/blob/main/docs/WESscDRS)

# Funding
The project was funded by the German Research Foundation (DFG) as part of the Research Unit ????.
