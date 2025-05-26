#This script is the master script that runs the personalized dimsum pipeline
"""
It starts by uploading the necessary data as well as the dimsum config file to the server,
then it runs dimsum remotely on the server and downloads the results to the local machine.

"""

#Import the necessary libraries
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import argparse
import time
import getpass

#parse arguments for the dimsum config file#####USELESS
parser = argparse.ArgumentParser()
parser.add_argument("--wk_dir", "-d", type=str, help="Path of the local working directory where the data is located")
parser.add_argument("--wk_dir_remote", "-r", type=str, help="Path working directory on the server")
parser.add_argument("--fastqFileDir", type=str, help="Path of fastq files on server")
parser.add_argument("--projectName","-n", type=str, help="Name of the project")
parser.add_argument("--outputPath", "-o", type=str, help="Path of results on server")
parser.add_argument("--MinInputAny",type=int, help="Minimum number of reads in any sample to be included in the analysis")
parser.add_argument("--MinInputAll",type=int, help="Minimum number of reads in all samples to be included in the analysis")
parser.add_argument("--numCores","-c",type=int, help="Number of cores to use for the analysis")
parser.add_argument("--final_library_30000_path",type=str, help="Path of the final library locally for the R pipeline")
parser.add_argument("--conda_env_R",type=str, help="Name of the conda environment to use for the R pipeline")
parser.add_argument("--conda_env_python",type=str, help="Name of the conda environment to use for the python pipeline")
parser.add_argument("--server_adress",type=str, help="Path of the server")
parser.add_argument("--config_file",type=str, help="Name of the dimsum config file")
parser.add_argument("--scripts_local_path",type=str, help="Path of the scripts on the local machine")
parser.add_argument("--password", "-p", action="store_true", help="Prompt for server password")
args = parser.parse_args()



#Create a class called DimSum pipeline that contain all the parameters to run dimsum and from which the user can call the functions and get the results of the pipeline
class DimSumPipeline:
    def __init__(self, wk_dir, wk_dir_remote, fastqFileDir, projectName, outputPath,  conda_env_R, conda_env_python, server_adress, config_file, scripts_local_path, password, experiment_design_path_remote, experiment_design_path_local, fastq_dir_local, server_required = bool, final_library_30000_path = None, verbose=False):
        self.verbose = verbose
        if self.verbose:
            print("Initializing DimSumPipeline...")
            
        self.server_adress = server_adress
        self.password = password
        self.server_required = server_required
        try:
            if self.verbose:
                print(f"Creating working directory: {wk_dir}")
            self.wk_dir = wk_dir
            if not os.path.exists(self.wk_dir):
                os.makedirs(self.wk_dir)
                
            if self.verbose:
                print(f"Checking remote directory: {wk_dir_remote}")
            self.wk_dir_remote = wk_dir_remote
            if not self.check_remote_dir(self.wk_dir_remote):
                if self.verbose:
                    print("Remote directory not found, creating it...")
                cmd = f"ssh {self.server_adress} 'mkdir -p {self.wk_dir_remote}'"
                if self.password:
                    cmd = f"sshpass -p '{self.password}' " + cmd
                subprocess.run(cmd, shell=True, check=True)
                print(f"Created remote directory: {self.wk_dir_remote}")
        except Exception as e:
            print(f"Error during initialization: {e}")
            raise

        self.fastqFileDir = fastqFileDir
        if self.server_required:
            if not self.check_remote_dir(self.fastqFileDir): #Check if the fastq directory exists on the server
                try:
                    cmd = f"ssh {self.server_adress} 'mkdir -p {self.fastqFileDir}'"
                    if self.password:
                        cmd = f"sshpass -p '{self.password}' " + cmd
                    subprocess.run(cmd, shell=True, check=True)
                    print(f"Created remote directory: {self.fastqFileDir}")
                except subprocess.CalledProcessError as e:
                    print(f"Error creating remote directory: {e}")
                    raise
        
        self.projectName = projectName
        self.outputPath = outputPath    
        if not self.check_remote_dir(self.outputPath) and self.server_required: #Check if the output path exists on the server
            try:
                cmd = f"ssh {self.server_adress} 'mkdir -p {self.outputPath}'"
                if self.password:
                    cmd = f"sshpass -p '{self.password}' " + cmd
                subprocess.run(cmd, shell=True, check=True)
                print(f"Created remote directory: {self.outputPath}")
            except subprocess.CalledProcessError as e:
                print(f"Error creating remote directory: {e}")
                raise
        
        self.final_library_30000_path = final_library_30000_path
        self.conda_env_R = conda_env_R
        self.conda_env_python = conda_env_python
        self.config_file = config_file
        self.scripts_local_path = scripts_local_path
        self.experiment_design_path_remote = experiment_design_path_remote
        self.experiment_design_path_local = experiment_design_path_local
        self.config_file_path = str(scripts_local_path+"/"+config_file)
        self.data_path = wk_dir+"/data" #Path to the data on the local machine
        self.server_path = server_adress+":"+wk_dir_remote #Path to the server
        self.server_path_fastq = self.server_path+"/"+self.fastqFileDir #Path to the server
        self.config_file = config_file #Name of the dimsum config file localy 
        self.scripts_local_path = scripts_local_path #Path to the scripts on the local machine
        self.fastq_dir_local = fastq_dir_local #Path to the fastq files on the local machine
        self.optional_args = {}


    def check_remote_dir(self, path):
        """Check if directory exists on remote server"""
        if self.verbose:
            print(f"Checking if directory exists on remote server: {path}")
        try:
            cmd = f"ssh {self.server_adress} '[ -d {path} ] && echo 1 || echo 0'"
            result = self.run_ssh_command(cmd, capture_output=True)
            exists = result.stdout.strip() == '1' if result and result.stdout else False
            if self.verbose:
                print(f"Directory exists: {exists}")
            return exists
        except Exception as e:
            print(f"Error checking remote directory: {e}")
            return False

    def run_ssh_command(self, command, capture_output=False):
        """Run SSH command with password if provided"""
        if self.verbose:
            print(f"Running SSH command: {command}")
        if self.password:
            if isinstance(self.password, bool):
                if self.verbose:
                    print("Password not provided, prompting user...")
                self.password = getpass.getpass("Enter server password: ")
                if self.verbose:
                    print("Password received")
            full_command = f"sshpass -p '{self.password}' {command}"
        else:
            full_command = command
            
        try:
            if self.verbose:
                print("Executing command...")
            if capture_output:
                result = subprocess.run(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if self.verbose:
                    print("Command executed successfully")
                return result
            else:
                subprocess.run(full_command, shell=True, check=True)
                if self.verbose:
                    print("Command executed successfully")
                return None
        except subprocess.CalledProcessError as e:
            print(f"Command failed with error: {e}")
            raise

    def create_dimsum_config_file(self, config_args, barcode = bool):
        """
        Creates a config file with customizable parameters forscript.sh using class attributes.
        The config file will be saved at self.config_file_path.
        If barcode is True, the barcode will be added to the config file.
        """
        if self.verbose:
            print("Creating DiMSum config file...")
            print("Setting up default configuration...")
            
        # Default configuration matching script.sh exactly
        default_config = {
            'fastqFileDir': self.fastqFileDir,
            'outputPath': self.outputPath,
            'MinInputAny': "100",
            'MinInputAll': "50",
            'projectName': self.projectName,
            'gzipped': "TRUE",
            'experimentDesignPath': self.experiment_design_path_remote,
            'cutadapt5First': "GGTTTCCAACCACAGTCTCAAGGT",
            'cutadapt5Second': "TAAGGTGGCGGCCGCTCTAGATTA",
            'cutadaptMinLength': "5",
            'cutadaptErrorRate': "0.2",
            'vsearchMaxQual': "30",
            'vsearchMinQual': "30",
            'vsearchMaxee': "0.5",
            'vsearchMinovlen': "5",
            'wildtypeSequence': "GATGCAGAGTTCCGACATGACTCAGGATATGAAGTTCATCATCAAAAATTGGTGTTCTTTGCAGAAGATGTGGGTTCAAACAAAGGTGCAATCATTGGACTCATGGTGGGCGGTGTTGTCATAGCG",
            'numCores': "10",
            'retainIntermediateFiles': "T",
            'type': "codon",
            'seqtype': "coding",
            'barcode': "",
            'start': "0",
            'mixed': "T",
            'indels': "all",
            'maxSubstitutions': "129",
            'end': "5",
            'error_output_path': f"my_path/{self.projectName}",
            'output_path': f"my_path/{self.projectName}",
            'ram_allocation': "70G",
            'time_max_job': "04:00:00",
            'job_name': "run"
        }
        
        # Update defaults with any provided arguments from class attributes
        
        if self.verbose:
            print("Updating configuration with provided arguments...")
        config = {**default_config, **config_args}
        
        
        # Create config file content
        config_content = f"""#!/bin/bash

#SBATCH --mem={config['ram_allocation']}
#SBATCH --cpus-per-task={config['numCores']}
#SBATCH --error={config['error_output_path']}.%j.err
#SBATCH --output={config['output_path']}.%j.out
#SBATCH --time={config['time_max_job']}
#SBATCH --job-name={config['job_name']}
#SBATCH --qos=short

set -euxo pipefail

fastqFileDir="{config['fastqFileDir']}"
outputPath="{config['outputPath']}"
MinInputAny="{config['MinInputAny']}"
MinInputAll="{config['MinInputAll']}"
projectName="{config['projectName']}"
gzipped="{config['gzipped']}"
experimentDesignPath="{config['experimentDesignPath']}"
cutadapt5First="{config['cutadapt5First']}"
cutadapt5Second="{config['cutadapt5Second']}"
cutadapt3First="{config['cutadapt3First']}"
cutadapt3Second="{config['cutadapt3Second']}"
cutadaptMinLength="{config['cutadaptMinLength']}"
cutadaptErrorRate="{config['cutadaptErrorRate']}"
cutadaptOverlap="{config['cutadaptOverlap']}"
vsearchMinQual="{config['vsearchMinQual']}"
vsearchMaxee="{config['vsearchMaxee']}"
vsearchMinovlen="{config['vsearchMinovlen']}"
wildtypeSequence="{config['wildtypeSequence']}"
numCores="{config['numCores']}"
retainIntermediateFiles="{config['retainIntermediateFiles']}"
type="{config['type']}"
seqtype="{config['seqtype']}"
barcode="{config.get('barcode', '')}"
start="{config['start']}"
mixed="{config['mixed']}"
indels="{config['indels']}"
maxSubstitutions="{config['maxSubstitutions']}"
end="{config['end']}"

DiMSum  --stopStage $end \\
  --barcodeIdentityPath {f"$barcode" if config.get('barcode') else ""} \\
  --cutadapt3First $cutadapt3First \\
  --cutadapt3Second $cutadapt3Second \\
  --cutadaptOverlap $cutadaptOverlap \\
  --maxSubstitutions $maxSubstitutions \\
  --indels $indels \\
  --mixedSubstitutions $mixed \\
  --startStage $start \\
  --sequenceType $seqtype \\
  --fitnessMinInputCountAny $MinInputAny \\
  --mutagenesisType $type \\
  --retainIntermediateFiles $retainIntermediateFiles \\
  --fastqFileDir $fastqFileDir \\
  --gzipped $gzipped \\
  --experimentDesignPath $experimentDesignPath \\
  --cutadapt5First $cutadapt5First \\
  --cutadapt5Second $cutadapt5Second \\
  --cutadaptMinLength $cutadaptMinLength \\
  --cutadaptErrorRate $cutadaptErrorRate \\
  --vsearchMinovlen $vsearchMinovlen \\
  --vsearchMinQual $vsearchMinQual \\
  --vsearchMaxee $vsearchMaxee \\
  --outputPath $outputPath \\
  --projectName $projectName \\
  --wildtypeSequence $wildtypeSequence \\
  --numCores $numCores
"""
        #--fitnessMinInputCountAll $MinInputAll
        #--barcodeIdentityPath $barcode
        
        #Save the error and output paths to the self class attributes
        self.error_output_path_verbose = config['error_output_path']
        self.output_path_verbose = config['output_path']

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.scripts_local_path), exist_ok=True)
        
        if self.verbose:
            print(f"Writing config file to: {self.config_file_path}")
        # Write config to file
        with open(self.config_file_path, 'w') as f:
            f.write(config_content)
        
        if self.verbose:
            print("Config file created successfully")
        return config

    def read_verbose_output(self, job_ID):
        """
        This function reads the verbose output file from server every 60 seconds and prints the output
        In addition, if the job is finished, it prints the error output verbose and exits the loop
        """
        try:
            while True:
                # Get latest content without -f flag
                command = f"ssh {self.server_adress} 'tail {self.output_path_verbose}.{job_ID}.out'"
                result = self.run_ssh_command(command, capture_output=True)
                
                if result.stdout:
                    print(result.stdout)
                    print("-------------------------------- Job is {} still running --------------------------------".format(job_ID))
                
                # Check if job is still running
                check_command = f"ssh {self.server_adress} 'squeue -j {job_ID} -h'"
                check_result = self.run_ssh_command(check_command, capture_output=True)
                
                # If job is not in queue anymore
                if not check_result.stdout.strip():
                    # Get any error output
                    error_command = f"ssh {self.server_adress} 'tail {self.error_output_path_verbose}.{job_ID}.err'"
                    error_result = self.run_ssh_command(error_command, capture_output=True)
                    if error_result.stdout:
                        print("Error output:")
                        print(error_result.stdout)
                    break
                
                time.sleep(120)
                
        except KeyboardInterrupt:
            print("\nStopped monitoring output")

    def upload_data_to_server(self):
        """
        This function uploads the necessary data to the server and creates the fastq directory on the server if it does not exist.
        Uses class attributes initialized in __init__.
        """
        if self.verbose:
            print("Starting data upload to server...")
            print(f"Uploading data from {self.fastq_dir_local} to {self.server_path_fastq}")
            
        if self.password:
            if isinstance(self.password, bool):
                if self.verbose:
                    print("Password not provided, prompting user...")
                self.password = getpass.getpass("Enter server password: ")
            os.system(f"sshpass -p '{self.password}' scp -r {self.fastq_dir_local}/* {self.server_path_fastq}")
        else:
            os.system(f"scp -r {self.data_path} {self.server_path_fastq}")
        

    def upload_config_file_to_server_run_dimsum(self):
        """
        This function uploads the dimsum config file to the server and runs dimsum using SLURM (or any other HPC job scheduler if you modify it)
        """
        

        # Upload config file and experiment design file
        if self.password:
            if isinstance(self.password, bool):  # If password is True but not a string
                self.password = getpass.getpass("Enter server password: ")
            os.system(f"sshpass -p {self.password} scp {self.scripts_local_path}/{self.config_file} {self.server_path}")
            os.system(f"sshpass -p {self.password} scp {self.experiment_design_path_local} {self.server_path}")
        else:
            os.system(f"scp {self.scripts_local_path}/{self.config_file} {self.server_path}")
            os.system(f"scp {self.experiment_design_path_local} {self.server_path}")
        
        # Submit the job and capture the job ID
        ssh_command = f"ssh {self.server_adress} 'cd {self.wk_dir_remote} && conda activate dimsum && sbatch {self.config_file}'"
        result = self.run_ssh_command(ssh_command, capture_output=True)
        
        # Extract job ID (SLURM output format: "Submitted batch job 123456")
        job_id = result.stdout.split()[-1]
        print(f"Job submitted with ID: {job_id}")
        
        #Read the verbose output
        self.read_verbose_output(job_id)

        # # Poll until the job is complete
        # while True:
        #     try:
        #         # Check job status using squeue
        #         check_command = f"ssh {self.server_adress} 'conda activate dimsum && squeue -j {job_id} -h'"
        #         check_job = subprocess.run(
        #             f"sshpass -p {self.password} {check_command}" if self.password else check_command,
        #             shell=True, capture_output=True, text=True
        #         )
                
        #         # If no output, job is done
        #         if not check_job.stdout.strip():
        #             # Check if job completed successfully using sacct
        #             state_command = f"ssh {self.server_adress} 'sacct -j {job_id} -o State -n -P'"
        #             state_check = subprocess.run(
        #                 f"sshpass -p {self.password} {state_command}" if self.password else state_command,
        #                 shell=True, capture_output=True, text=True
        #             )
                    
        #             state = state_check.stdout.strip()
        #             if 'COMPLETED' in state:
        #                 print("Job completed successfully!")
        #                 break
        #             elif 'FAILED' in state or 'CANCELLED' in state or 'TIMEOUT' in state:
        #                 print(f"Job failed with state: {state}")
        #                 break
                
        #         print(f"Job {job_id} still running... waiting 60 seconds")
        #         time.sleep(60)
                
        #     except subprocess.CalledProcessError:
        #         print("Error checking job status - job might not exist or there might be connection issues")
        #         print("Please check job status manually")
        #         break

    def create_experiment_design(self, input_dict, output_dict = None):
        """
        Create experiment design file from input and output dictionaries.
        
        Args:
            input_dict (dict): Dictionary for input samples with format:
                {
                    'sample_name': {
                        'replicate': int,
                        'selection_id': int,
                        'selection_replicate': int,
                        'technical_replicate': int,
                        'pair1': str,
                        'pair2': str
                    }
                }
            output_dict (dict): Dictionary for output samples (same format as input_dict) (optional)
            output_file_path (str): Path where to save the experiment design file
        """
        # Validate input
        required_keys = ['replicate', 'selection_id', 'selection_replicate', 
                        'technical_replicate', 'pair1', 'pair2']
        
        if output_dict is None:
            # Only validate input_dict
            if not input_dict:
                raise ValueError("input_dict cannot be empty")
            for sample, values in input_dict.items():
                missing = [k for k in required_keys if k not in values]
                if missing:
                    raise ValueError(f"Sample {sample} missing required keys: {missing}")
        else:
            # Validate both input and output dicts
            for d, name in [(input_dict, 'input'), (output_dict, 'output')]:
                if not d:
                    raise ValueError(f"{name}_dict cannot be empty")
                for sample, values in d.items():
                    missing = [k for k in required_keys if k not in values]
                    if missing:
                        raise ValueError(f"Sample {sample} missing required keys: {missing}")

        # Create header
        header = ["sample_name", "experiment_replicate", "selection_id", 
                "selection_replicate", "technical_replicate", "pair1", "pair2"]
        
        # Combine all entries
        entries = []
        
        # Process input samples
        for sample_name, values in input_dict.items():
            entries.append([
                sample_name,
                str(values['replicate']),
                str(values['selection_id']),
                str(values['selection_replicate']),
                str(values['technical_replicate']),
                values['pair1'],
                values['pair2']
            ])
        
        # Process output samples if they exist
        if output_dict is not None:
            for sample_name, values in output_dict.items():
                entries.append([
                    sample_name,
                    str(values['replicate']),
                    str(values['selection_id']),
                    str(values['selection_replicate']),
                    str(values['technical_replicate']),
                    values['pair1'],
                    values['pair2']
                ])
        
        # Write to file
        with open(self.experiment_design_path_local, 'w') as f:
            # Write header
            f.write('\t'.join(header) + '\n')
            
            # Write entries
            for entry in entries:
                f.write('\t'.join(entry) + '\n')

    #def modify_shell_script(self, config_file_path, variable_name, new_value):
       # """
       # This function modifies the dimsum config file to include the new values for the variables based on the arguments passed to the script
        #"""
        # Escape special characters in the new value
        #escaped_value = new_value.replace('/', '\/')
        
        # Create sed command that handles quoted values
        #sed_command = f"sed -i '' 's/{variable_name}=\".*\"/{variable_name}=\"{escaped_value}\"/' {config_file_path}"
        
        # Execute the command
        #subprocess.run(sed_command, shell=True)

    #def iterate_modify_shell_script(self, config_file_path, args):
       # """
        #This function iterates over the arguments passed to the script and modifies the dimsum config file to include the new values for the variables
        #"""
        #for arg in vars(args):
        #    self.modify_shell_script(config_file_path, arg, getattr(args, arg))

    def download_results_from_server(self, list_of_extra_files_to_download = None, files_to_delete = None):
        """
        This function downloads the 3 most important results files from the server to the local machine
        List of extra files to download can be passed as an argument, should be a list of strings of supplementary files to download
        """
        results_path = self.server_adress+":"+self.outputPath + self.projectName + "/"
        results_path_tmp = self.outputPath + self.projectName + "/tmp/"
        files_to_download = [
            self.projectName + "_fitness_replicates.RData",
            self.projectName + "_variant_data_merge.RData",
            self.projectName + "_variant_data_merge.tsv",
            "report.html",
            self.projectName + "_nobarcode_variant_data_merge.tsv"
        ]

        if not os.path.exists(os.path.join(self.wk_dir,'data')):
            os.makedirs(os.path.join(self.wk_dir,'data'))

        # Add extra files to download if provided   
        if list_of_extra_files_to_download is not None:
            files_to_download.extend(list_of_extra_files_to_download)

        if isinstance(self.password, bool):  # If password is True but not a string
                self.password = getpass.getpass("Enter server password: ")
        for file in files_to_download:
            ssh_command = f"sshpass -p '{self.password}' scp {results_path}{file} {os.path.join(self.wk_dir,'data',file)}"
            self.run_ssh_command(ssh_command)

        #Rename the report.html file to projectName_report.html
        os.rename(os.path.join(self.wk_dir,'data','report.html'), os.path.join(self.wk_dir,'data',self.projectName + "_report.html"))

        if files_to_delete is not None:
            for file in files_to_delete:
                delete_file = f"sshpass -p '{self.password}' ssh {self.server_adress} 'rm -r {results_path_tmp}{file}'"
                self.run_ssh_command(delete_file)

    def run_R_pipeline(self, scripts_args, programming_language = ("R", "python")):
        """
        This function runs the R pipeline to get the clusters from the results files inside the right conda environment
        Optional args takes as input a dictionary of scripts to run with their arguments as a list of strings
        """
        
        for script in scripts_args.keys():
            args_string = ' '.join(f'"{arg}"' for arg in scripts_args[script])
            # Create the full command
            if programming_language == "R":
                command = f"source ~/mambaforge-intel/etc/profile.d/conda.sh && conda activate {self.conda_env_R} && Rscript {self.scripts_local_path}/{script} {args_string}"
            elif programming_language == "python":
                command = f"source ~/mambaforge-intel/etc/profile.d/conda.sh && conda activate {self.conda_env_python} && python {self.scripts_local_path}/{script} {args_string}"
            
            # Run the command using os.system
            exit_code = os.system(command)
            
            if exit_code == 0:
                print(f"Script {script} ran successfully")
            else:
                print(f"Error running {script}. Exit code: {exit_code}")
