#!/bin/bash

export OMP_NUM_THREADS=${jobCPU};
		
echo; echo "Extracting WMFire Output"; echo;
cat $file | wc -l
python ${process} "$file" "$outdir" "$syr" "$mod" "typ"
echo "Complete"

