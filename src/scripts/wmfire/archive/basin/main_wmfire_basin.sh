#!/bin/bash

# ID (customizable -> corresponds to output directory structure)
export syr=2075;    # 1991 | 2045 | 2075
export mod="IPSL"; # CSIRO | IPSL
export typ="rcp85"; # hist | rcp85
export tag="basin";

# Directories
export calldir=$(pwd);
export workdir="/weka/data/lab/adam/jonathan.gendron/rhessys/RHESSysUtil/src/scripts/wmfire/basin";
export indir="/data/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/${syr}/${mod}/brw/storage";
export outdir="/data/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/storage";
cd $workdir
export runprog="run_wmfire_basin.sh";
#export file_idx="BRW_col-row-patchID.csv";
#export file_idx=$(realpath $file_idx);

# Python Scripts
export filelist="filelist_wmfire_basin.py"
export analysis="analysis_wmfire_basin.py"

# Program Settings
export create_filelist=1;
export analysis_data=1;

# Kamiak Job Settings
export jobDy=0; # 1 day
export jobHr=1; # 2 hr
export jobMn=0;
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
	python $filelist $indir $outdir;
fi;

#tail $indir/storage/wmfire_filelist.txt -n +2 > "$indir/storage/wmfire_filelist2.txt"
export flist=$outdir/wmfire_basin_filelist.txt;
	
if [[ $analysis_data == 1 ]];
then			
	echo; echo "Analyzing WMFire Output"; echo;		
	#sbatch --partition=${jobPt} --job-name=${syr}_${mod}_${typ}_wmfire_analysis_Node-%N_JobID-%j.run --output=${log}/${i0}_${i1}_${wmfire_seed}_Node-%N_JobID-%j.out --time=$jobDy-$jobHr:$jobMn:$jobSc --cpus-per-task=$jobCPU ${runprog};
	python ${analysis} "$flist" "$outdir" "$syr" "$mod" "$typ";
fi;

rm $flist

echo "done"

