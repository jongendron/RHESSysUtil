#!/bin/bash

dir_progset="/weka/data/lab/adam/jonathan.gendron/rhessys/RHESSysUtil/src/scripts/parameterization/Manual/progset/grow_basin_daily"
subfnc="/weka/data/lab/adam/jonathan.gendron/rhessys/RHESSysUtil/src/scripts/parameterization/Manual/sub.py"

#sub_vars=("in_path" "in_path" "in_path" "in_path" "in_path" "in_path")
search_paths=(#"/data/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/1991/CSIRO/brw"
#"/data/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/2045/CSIRO/brw"
#"/data/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/2075/CSIRO/brw"
#"/data/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/1991/IPSL/brw"
"/data/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/2045/IPSL/brw"
"/data/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/2075/IPSL/brw"
)

#search_paths=("/data/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/2075/CSIRO/brw")
storage_path="/weka/data/lab/adam/jonathan.gendron/rhessys/Kamiak/output/gcm/storage/grow_basin_daily";

#storage_idx=(1 2 3 4 5 6);
#storage_idx=("1991-CSIRO" "2045-CSIRO" "2075-CSIRO" "1991-IPSL" "2045-IPSL" "2075-IPSL");
#storage_idx=("1991-CSIRO-hist" "2045-CSIRO-rcp85" "2075-CSIRO-rcp85" "1991-IPSL-hist" "2045-IPSL-rcp85" "2075-IPSL-rcp85")
storage_idx=("2045-IPSL-rcp85" "2075-IPSL-rcp85")

varlist="litrc, soil_resp, gpsn, plant_resp, leaf_resp"
#varlist="streamflow,precip,snowfall,snowmelt,snowpack"

st=0; echo "st: ${st}";
end="$((${#search_paths[@]} - 1))"; echo "end: ${end}";
echo;

for (( iter=$st; iter<=$end; iter++ ));
do
	echo "iter: ${iter}";
	for file in $(ls ${dir_progset}/progset*);
	do
		#echo ${file};echo;		
		#python ${subfnc} "${file}" "${sub_vars[$iter]}" "${sub_values[$iter]}"
		python ${subfnc} "${file}" "${search_paths[$iter]}" "${storage_path}" "${storage_idx[$iter]}" "${varlist}";
		cat ./progset_tmp.csv | awk 'NR==4{print $5}';
		python main_param.py "progset_tmp.csv" "false" "${storage_idx[$iter]}"; echo;
		#rm "progset_tmp.csv"
	done;
echo;
done

	
