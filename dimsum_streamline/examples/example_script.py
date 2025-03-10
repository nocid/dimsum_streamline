from master_script import DimSumPipeline

BB30_dict = {
    "fastqFileDir": "/users/blehner/bbolognesi/Romain/dimsum_runs/fastas_BB30_plate_merged_run/",
    "outputPath": "/users/blehner/bbolognesi/Romain/dimsum_runs/output_BB30_plate_merged_run/",
    "MinInputAny": "7",
    "MinInputAll": "10",
    "projectName": "BB30_plate_merged_run",
    "gzipped": "TRUE",
    "experimentDesignPath": "/users/blehner/bbolognesi/Romain/dimsum_runs/experiment_design_BB30_plate_merged_run.txt",
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
    "barcode": "/users/blehner/bbolognesi/Romain/dimsum_runs/variant_BB30K_unified.txt",
    "start": "0",
    "mixed": "T",
    "indels": "all",
    "maxSubstitutions": "90",
    "end": "5",
    "error_output_path": "/users/blehner/bbolognesi/Romain/dimsum_runs/output_BB30_plate_merged_run/errors_BB30_plate_merged_run",
    "output_path": "/users/blehner/bbolognesi/Romain/dimsum_runs/output_BB30_plate_merged_run/output_BB30_plate_merged_run",
    "ram_allocation": "70G",
    "time_max_job": "03:59:00",
    "job_name": "dimsum_run_BB30_plate_merged_run"
}

plate_merged_run = DimSumPipeline(wk_dir= "/Users/nocide51/Desktop/Science/Biology/IBEC/data/AB_42_BB_30K/scripts_automated/BB30_plate_merged_run",
                          wk_dir_remote= "/users/blehner/bbolognesi/Romain/dimsum_runs",
                          fastqFileDir= "fastas_BB30_plate_merged_run/",
                          server_required= True,
                          projectName= "BB30_plate_merged_run",
                          outputPath= "/users/blehner/bbolognesi/Romain/dimsum_runs/output_BB30_plate_merged_run/",
                          final_library_30000_path= "/Users/nocide51/Desktop/Science/Biology/IBEC/data/AB_42_BB_30K/scripts_automated/test/data/original_lib_design_BB30.RData",
                          conda_env_R= "R_x86",
                          conda_env_python= "pymochi",
                          server_adress= "bbolognesi@login1.hpc.crg.es",
                          config_file= "BB30_plate_merged_run_config.sh",
                          scripts_local_path= "/Users/nocide51/Desktop/Science/Biology/IBEC/data/AB_42_BB_30K/scripts_automated/test",
                          password= True,
                          experiment_design_path_remote= "/users/blehner/bbolognesi/Romain/dimsum_runs/experiment_design_BB30_plate_merged_run.txt",
                          experiment_design_path_local= "/Users/nocide51/Desktop/Science/Biology/IBEC/data/AB_42_BB_30K/scripts_automated/test/experiment_design_BB30_plate_merged_run.txt",
                          fastq_dir_local= "/Users/nocide51/Desktop/Science/Biology/IBEC/data/AB_42_BB_30K/DimSum/merge_fastas_plate_run/output_merged_BB30_3_runs",
                          verbose= True
)

input_dict = {
    "input1": {
        "replicate": 1,
        "selection_id": 0,
        "selection_replicate": " ",
        "technical_replicate": 1,
        "pair1": "input1_BB30_merged_R1.fastq.gz",
        "pair2": "input1_BB30_merged_R2.fastq.gz"
    },
    "input2": {
        "replicate": 2,
        "selection_id": 0,
        "selection_replicate": " ",
        "technical_replicate": 1,
        "pair1": "input2_BB30_merged_R1.fastq.gz",
        "pair2": "input2_BB30_merged_R2.fastq.gz"
    },
    "input3": {
        "replicate": 3,
        "selection_id": 0,
        "selection_replicate": " ",
        "technical_replicate": 1,
        "pair1": "input3_BB30_merged_R1.fastq.gz",
        "pair2": "input3_BB30_merged_R2.fastq.gz"
    }   
}

output_dict = {
    "output1": {
        "replicate": 1,
        "selection_id": 1,
        "selection_replicate": 1,
        "technical_replicate": 1,
        "pair1": "output1_BB30_merged_R1.fastq.gz",
        "pair2": "output1_BB30_merged_R2.fastq.gz"
    },
    "output2": {
        "replicate": 2,
        "selection_id": 1,
        "selection_replicate": 1,
        "technical_replicate": 1,
        "pair1": "output2_BB30_merged_R1.fastq.gz",
        "pair2": "output2_BB30_merged_R2.fastq.gz"
        },
    "output3": {
        "replicate": 3,
        "selection_id": 1,
        "selection_replicate": 1,
        "technical_replicate": 1,
        "pair1": "output3_BB30_merged_R1.fastq.gz",
        "pair2": "output3_BB30_merged_R2.fastq.gz"
    }
}

files_to_delete =["0_demultiplex", "1_qualitycontrol", "2_trim", "3_align", "3_tally"]

plate_merged_run.create_experiment_design(input_dict= input_dict, output_dict= output_dict)
#plate_merged_run.upload_data_to_server()
plate_merged_run.create_dimsum_config_file(config_args= BB30_dict, barcode= True)
plate_merged_run.upload_config_file_to_server_run_dimsum()
plate_merged_run.download_results_from_server()

scripts_args_plate_merged_run = {
    "00_data_diagnostics.R": ["/Users/nocide51/Desktop/Science/Biology/IBEC/data/AB_42_BB_30K/scripts_automated/BB30_plate_merged_run", 
                            "/Users/nocide51/Desktop/Science/Biology/IBEC/data/AB_42_BB_30K/scripts_automated/BB30_plate_1_run/data/BB30_plate_1_run_fitness_replicates.RData", 
                            "/Users/nocide51/Desktop/Science/Biology/IBEC/data/AB_42_BB_30K/scripts_automated/BB30_plate_merged_run/data/BB30_plate_merged_run_variant_data_merge.RData", 
                            "BB30_plate_merged_run", 
                            "3"],
    "01_dimsum_data.R": ["/Users/nocide51/Desktop/Science/Biology/IBEC/data/AB_42_BB_30K/scripts_automated/BB30_plate_merged_run",
                         "BB30_plate_merged_run", 
                         "3"]}

plate_merged_run.run_R_pipeline(scripts_args= scripts_args_plate_merged_run, programming_language= "R")

