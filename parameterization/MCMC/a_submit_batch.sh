#!/bin/bash

printf "Starting RHESSys batch job.\n\n";

# Define global variables
export prefix="def_cold";
export call=$(pwd);
export sbatch2="${call}/b_run_rhessys.sh";
export parfile=${call}/ndeplist.txt; # single column table where each row is a different n_deposition value (kg-N/m2/yr)

export input="${call}/input";
export output="${call}/output/${prefix}";
mkdir -p ${output};
export log="${call}/logs/${prefix}";
mkdir -p ${log};

# Define awk program variables
export awkfnc="${call}/chgndep.awk";
export awkin="${input}/defs/zone_zone.def.bak";
export awkout="${input}/defs/zone_zone_ndep.def";

# Loop through input parameter file
# change zone_zone.def file to use parameter read from file
# redefine prefix


while IFS= read -r line;
do
	printf "n_deposition = ${line}\n";
	awk -f ${awkfnc} par=${line} ${awkin} > ${awkout};
	export prefix2="${prefix}_ndep${line}";
	cat ${awkout};
	printf "\n\n";

	cd ${input};
	${sbatch2};
	cd ${call};

	printf "\n\n";

	sleep $(( $RANDOM % 3 + 3 ))

done < ${parfile};

printf "\nDone with the job!\n";


