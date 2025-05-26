from master_script import DimSumPipeline

my_dict = {
    "fastqFileDir": "mypath",
    "outputPath": "mypath",
    "MinInputAny": "7",
    "MinInputAll": "10",
    "projectName": "myexp",
    "gzipped": "TRUE",
    "experimentDesignPath": "mypath/expdesign.txt",
   "cutadapt5First": "GGTTTCCAACCACAGTCTCAAGGT",
    "cutadapt5Second": "GGTGGCGGCCGCTCTAGATTA",
    "cutadapt3First": "TAATCTAGAGCGGCCGCCACC",
    "cutadapt3Second": "ACCTTGAGACTGTGGTTGGAAACC",
    "cutadaptMinLength": "40",
    "cutadaptErrorRate": "0.05",
    "cutadaptOverlap": "6",
    "vsearchMinQual": "30",
    "vsearchMaxee": "0.5",
    "vsearchMinovlen": "30",         
    "wildtypeSequence" : "GATGCAGAGTTCCGACATGACTCAGGATATGAAGTTCATCATCAAAAATTGGTGTTCTTTGCAGAAGATGTGGGTTCAAACAAAGGTGCAATCATTGGACTCATGGTGGGCGGTGTTGTCATAGCG",
    "numCores": "10",
    "retainIntermediateFiles": "T",
    "type": "codon",
    "seqtype": "coding",
    "barcode": "mypath/barcode.txt",
    "start": "0",
    "mixed": "T",
    "indels": "all",
    "maxSubstitutions": "90",
    "end": "5",
    "error_output_path": "myerror_path",
    "output_path": "my_error_path",
    "ram_allocation": "70G",
    "time_max_job": "03:59:00",
    "job_name": "myjob"
}

plate_merged_run = DimSumPipeline(wk_dir= "my_local_path",
                          wk_dir_remote= "my_remote_path",
                          fastqFileDir= "fastas_run/",
                          server_required= True,
                          projectName= "my_run",
                          outputPath= "myoutput_path",
                          final_library_30000_path= "my_lib_design_path",
                          conda_env_R= "my_local_R_path",
                          conda_env_python= "my_local_python_path",
                          server_adress= "my_server_adress",
                          config_file= "my_config",
                          scripts_local_path= "my_local_scripts_path",
                          password= True,
                          experiment_design_path_remote= "remote_path",
                          experiment_design_path_local= "design_path",
                          fastq_dir_local= "my_local_output_path",
                          verbose= True
)

input_dict = {
    "input1": {
        "replicate": 1,
        "selection_id": 0,
        "selection_replicate": " ",
        "technical_replicate": 1,
        "pair1": "input1_R1.fastq.gz",
        "pair2": "input1_R2.fastq.gz"
    },
    "input2": {
        "replicate": 2,
        "selection_id": 0,
        "selection_replicate": " ",
        "technical_replicate": 1,
        "pair1": "input2_R1.fastq.gz",
        "pair2": "input2_R2.fastq.gz"
    },
    "input3": {
        "replicate": 3,
        "selection_id": 0,
        "selection_replicate": " ",
        "technical_replicate": 1,
        "pair1": "input3_R1.fastq.gz",
        "pair2": "input3_R2.fastq.gz"
    }   
}

output_dict = {
    "output1": {
        "replicate": 1,
        "selection_id": 1,
        "selection_replicate": 1,
        "technical_replicate": 1,
        "pair1": "output1_R1.fastq.gz",
        "pair2": "output1_R2.fastq.gz"
    },
    "output2": {
        "replicate": 2,
        "selection_id": 1,
        "selection_replicate": 1,
        "technical_replicate": 1,
        "pair1": "output2_R1.fastq.gz",
        "pair2": "output2_R2.fastq.gz"
        },
    "output3": {
        "replicate": 3,
        "selection_id": 1,
        "selection_replicate": 1,
        "technical_replicate": 1,
        "pair1": "output3_R1.fastq.gz",
        "pair2": "output3_R2.fastq.gz"
    }
}

files_to_delete =["0_demultiplex", "1_qualitycontrol", "2_trim", "3_align", "3_tally"]

plate_merged_run.create_experiment_design(input_dict= input_dict, output_dict= output_dict)
#plate_merged_run.upload_data_to_server()
plate_merged_run.create_dimsum_config_file(config_args= my_dict, barcode= True)
plate_merged_run.upload_config_file_to_server_run_dimsum()
plate_merged_run.download_results_from_server()

scripts_args = {
    "00_my_downstream_script.R": ["my_path_to_data", 
                            "my_arg"]}

plate_merged_run.run_R_pipeline(scripts_args= scripts_args, programming_language= "R")

