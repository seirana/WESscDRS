# WESscDRS
WESscDRS is a Nexflow pipeline designed to link scRNA-seq with polygenic disease risk at the single-cell resolution, independent of annotated cell types, and suggest drugs for the disease.  

It provides comprehensive functionalities for:  
 - GE-scDRS Identifying cells exhibiting excess expression across disease-associated genes implicated by Whole Exome Sequencing (WES).  

The pipeline is compatible with any Linux system and requires only two dependencies:  
 - Nextflow (workflow manager)  
 - Singularity  (as the container engine)

In [Quick Start](#quick-start), you can follow the instructions to install the requirements and run simple samples.
To know the details of the functions, check the [Documentations](#documentations). Also, there, you can find detailed instructions about the data type and formats that are needed as input for WESscDRS function.
 
# Table of contents
- [Pipeline structure](#pipeline-structure)
- [Key features](#key-features)

- [Quick Start](#quick-start)
	- [Prerequisites and Configuration](#prerequisites-and-configuration)
    	- [Pre-configuration](#pre-configuration)
    	- [Custom configuration](#custom-configuration)
	- [Installing dependencies](#installing-dependencies)
		- [Step 1: Install Nextflow](#step-1-Install-nextflow)
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
After installing Netwflow and Singularity, you no longer need to install additional software.
Nextflow automatically downloads all necessary containers and tools.

![Image Alt Text](https://github.com/seirana/WESscDRS/blob/main/Images/Pipeline%20Structure.png)

# Quick Start
## Prerequisites and Configuration
WESscDRS requires significant computational resources. Ensure your system meets the following minimum requirements:

CPU: At least 16 cores.    
RAM: At least 32 GB (e.g., WESscDRS may require up to 360 GB).

### Pre-configuration
WESscDRS includes a pre-configured quickstart profile for local testing with the least requirements, as mentioned above.

Note: The quickstart profile is not recommended for real metagenome data analysis usage.
For large datasets, it is recommended to run the pipeline on a high-performance computing (HPC) system.

### Custom configuration
To fully utilize WESscDRS on an HPC or other systems, you must create a custom configuration file specifying:

Available CPU cores and memory.
Scheduler settings (e.g., local or SLURM).
Paths for reference databases.
Please take a look at the installation and configuration documentation for details. ???????

## Installing dependencies
### Step 1: Install Nextflow
Nextflow requires Bash 3.2 (or later) and Java 17 (or later, up to 24) to be installed. Follow the instructions from [Nextflow installation guidance](https://www.nextflow.io/docs/latest/install.html#install-page) to check requirements and step-by-step installation.

### Step 2: Install Singularity 
You can install Singularity via the [Singularity Quickstart Guide](https://docs.sylabs.io/guides/3.9/user-guide/quick_start.html) or
[Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html):
```bash
# Create a new conda environment for Singularity
conda create --name sing_env -c conda-forge -c bioconda singularity=3.8 
# Activate environment
conda activate sing_env
# Check whether Singularity has been successfully installed
singularity --version
# Also, make sure you can run an example container
singularity run library://sylabsed/examples/lolcow
```

### step 3: Install dependent software for WESscDRS
GEcsDRS needs some extra software to run:
* scDRS
Nextflow will install it. If there is a problem, check [their page](https://pypi.org/project/scdrs/).
* bcftools
You can install it from [here](https://samtools.github.io/bcftools/howtos/install.html).
* MAGMA
Select and install the proper version based on your operating system from [here](https://cncr.nl/research/magma/).

## Downloads
### Downloading WESscDRS
Use the following command to download or update the pipeline:
```bash
nextflow pull ikmb/WESscDRS
```
You will find the pipeline code stored in ${HOME}/.nextflow/assets/ikmb/WESscDRS.

### Downloading input data for GEsxDRS

## Example workflows
* Running WESscDRS	
  
### Running WESscDRS	
In your first run, to download required databases, you can add the --updatemetaphlan flag; in subsequent runs, you can skip the update flag (remove line 6 from the following code; --updatemetaphlan \).
```bash
nextflow run ikmb/WESscDRS \
    -profile custom \
    -c tofu.config \
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
The project was funded by the German Research Foundation (DFG) Research Unit ????.
