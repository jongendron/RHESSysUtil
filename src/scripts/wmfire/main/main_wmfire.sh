#!/bin/bash

# ID (customizable -> corresponds to output directory structure)
export syr=1900;    # 1991 | 2045 | 2075
export mod="nohs"; # CSIRO | IPSL
export typ="hist"; # hist | rcp85
export tag="basin";

# Directories
export calldir=$(pwd);
export workdir="/weka/data/lab/adam/jonathan.gendron/rhessys/RHESSysUtil/src/scripts/wmfire/main";
# export indir="/data/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/$syr/$mod/brw";
export indir="/data/adam/jonathan.gendron/rhessys/Kamiak/output/hist/$syr/$mod/brw/MeanMoIgn0p02-brw-1900-nohs-hist-1";
#export outdir=${indir}/storage;
export outdir="/data/adam/jonathan.gendron/rhessys/Kamiak/output/hist/$syr/$mod/brw/storage";
cd $workdir
export runprog="run_wmfire.sh";
export file_idx="../BRW_col-row-patchID.csv";
export file_idx=$(realpath $file_idx);

# Python Scripts
export filelist="filelist_wmfire.py"
export process="AnalyzeWMFire.py"

# Program Settings
export create_filelist=1;
export process_data=1;

# Kamiak Job Settings
export jobDy=0; # 1 day
export jobHr=6; # 2 hr
export jobMn=0;
export jobSc=0;
export jobPt="adam,kamiak,vcea";
#export jobPt="kamiak,vcea";
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

#tail $outdir/wmfire_filelist.txt -n +2 > "$outdir/wmfire_filelist2.txt"
#export flist="$outdir/wmfire_filelist2.txt"
tail $outdir/${syr}-${mod}-${typ}_wmfire_filelist.txt -n +2 > "$outdir/${syr}-${mod}-${typ}_filelist2.txt"
export flist="$outdir/${syr}-${mod}-${typ}_filelist2.txt"

export alen=$(cat $flist | wc -l);
export set_array=();
for ((idx = 1; idx <= $alen; idx++));
do
	set_array+=($idx,);
done;

declare -p set_array

if [[ $process_data == 1 ]];
then
	echo; echo "Submitting WMFire Processing Array"; echo;
	sbatch --partition=${jobPt} --job-name=${syr}_${mod}_${typ}_%a_wmfireoutput_Node-%N_JobID-%j_ArrayID-%A.run --output=${log}/${syr}_${mod}_${typ}_%a_wmfireoutput_Node-%N_JobID-%j_ArrayID-%A.out --time=$jobDy-$jobHr:$jobMn:$jobSc --cpus-per-task=$jobCPU --array="${set_array[*]}" ${runprog};
fi

echo "done"

