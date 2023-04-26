#!/bin/bash

# Directories
export calldir=$(pwd);
export workdir="/weka/data/lab/adam/jonathan.gendron/rhessys/RHESSysUtil/src/scripts/wmfire";
export indir="/data/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/2075/CSIRO/brw";
export outdir=${indir}/storage;
cd $workdir
export run="run.sh";
export file_idx="BRW_col-row-patchID.csv";
export file_idx=$(realpath $file_idx);

# Python Scripts
export filelist="filelist_wmfire.py"
export extract="extract_wmfire.py"

# Program Settings
export create_filelist=1;
export extract_data=1;

# Kamiak Job Settings
export jobDy=0; # 1 day
export jobHr=0; # 2 hr
export jobMn=15;
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
	python $filelist $indir;
fi;

tail $indir/storage/wmfire_filelist.txt -n +2 > "$indir/storage/wmfire_filelist2.txt"
export flist=$indir/storage/wmfire_filelist2.txt;
	
if [[ $extract_data == 1 ]];
then
	#echo "yes"
	while IFS= read -r line;
	do			
		export i0=$(echo $line | awk '{print $1}');
		export i1=$(echo $line | awk '{print $2}');
		export file=$(echo $line | awk '{print $3}');
		export wmfire_seed=$(echo $line | awk '{print $5}');
		echo $i0 $i1 $wmfire_seed;
		
		echo; echo "Extracting WMFire Output"; echo;
		
		#python $extract "${i0}_${i1}_${wmfire_seed}" $file $file_idx $outdir
		sbatch --partition=${jobPt} --job-name=${i0}_${i1}_${wmfire_seed}_wmfireoutput_Node-%N_JobID-%j.run --output=${log}/${i0}_${i1}_${wmfire_seed}_Node-%N_JobID-%j.out --time=$jobDy-$jobHr:$jobMn:$jobSc --cpus-per-task=$jobCPU ${run};
		
	done < $flist;
fi;

echo "done"

