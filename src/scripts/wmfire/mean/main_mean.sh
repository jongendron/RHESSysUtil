#!/bin/bash

# ID (customizable -> corresponds to output directory structure)
export syr=2075;    # 1991 | 2045 | 2075
export mod="CSIRO"; # CSIRO | IPSL
export typ="hist"; # hist | rcp85
export tag="basin";

# Directories
export calldir=$(pwd);
export workdir="/weka/data/lab/adam/jonathan.gendron/rhessys/RHESSysUtil/src/scripts/wmfire/mean";
#export indir="/data/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/storage/time-avg_WMFireGridTable"
#export outdir="/data/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/storage/time-avg_WMFireGridTable/storage";
export indir="/data/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/storage/time-avg_WMFireGridTable"
export outdir="/data/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/storage/time-avg_WMFireGridTable/storage"
cd $workdir
export runprog="run_mean.sh";

# Python Scripts
export filelist="filelist_mean.py"
export process="process_mean.py"

# Program Settings
export create_filelist=1;
export process_data=1;

# Kamiak Job Settings
export jobDy=0; # 1 day
export jobHr=0; # 2 hr
export jobMn=10;
export jobSc=0;
export jobPt="adam,kamiak,vcea";
export jobCPU=1; # CPU's per job
export log=${outdir}/log;
mkdir -p ${log};

########################
### Run the programs ###
########################
cd $workdir

if [[ $create_filelist == 1 ]];
then
	python $filelist "$indir" "$outdir" "$syr" "$mod" "$typ";
fi;

export file="$outdir/${syr}-${mod}-${typ}_wmfire_filelist.txt"
ls $flist

if [[ $process_data == 1 ]];
then
	echo; echo "Submitting WMFire Processing Array"; echo;
	#sbatch --partition=${jobPt} --job-name=${syr}_${mod}_${typ}_wmfireoutput_Node-%N_JobID-%j.run --output=${log}/${syr}_${mod}_${typ}_wmfireoutput_Node-%N_JobID-%j.out --time=$jobDy-$jobHr:$jobMn:$jobSc --cpus-per-task=$jobCPU ${runprog};
	./${runprog};
fi

echo "done"

