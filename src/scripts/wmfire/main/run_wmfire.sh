#!/bin/bash

export OMP_NUM_THREADS=${jobCPU};
export set_idx=${SLURM_ARRAY_TASK_ID};

export i0=$(awk -v rn=${set_idx} 'NR==rn{ print $1; exit }' $flist)
export i1=$(awk -v rn=${set_idx} 'NR==rn{ print $2; exit }' $flist)
export file=$(awk -v rn=${set_idx} 'NR==rn{ print $3; exit }' $flist)
export wmfire_seed=$(awk -v rn=${set_idx} 'NR==rn{ print $5; exit }' $flist)
echo $i0 $i1 $wmfire_seed;
		
echo; echo "Extracting WMFire Output"; echo;
cat $flist | wc -l;
python ${process} "$file" "$file_idx" "$outdir" "$syr" "$mod" "$typ" "$i0" "$i1" "$wmfire_seed"
#python ${process} "${i0}_${i1}_${wmfire_seed}" "$file" "$file_idx" "$outdir";
echo "Complete"

