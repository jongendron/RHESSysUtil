#!/bin/bash

export RHESSys="${call}/RHESSys_0soil_0veg"
#export RHESSys="${call}/RHESSys_0veg"
#export RHESSys="${call}/RHESSys"

export syr=1980;
export smo=01;
export sdy=01;
export shr=01;

export eyr=2002;
export emo=12;
export edy=31;
export ehr=24;


export state="${input}/def_patch_basin.state";
export flow="${input}/patch_basin.flow";
export tec="${input}/patch_basin_1980.tec";
export hdr="${input}/def_ndep_patch_basin.hdr";
export outfile="${output}/${prefix2}";
export logfile="${log}/${prefix2}_log.txt";

export m=1.00;
export k=5.241;
export po=0.622;
export pa=0.500;
export gw1=0.010;
export gw2=0.049;

#${RHESSys} -firespin 20 50 -netcdfgrid -ncgridinterp 10 -t ${tec} -w ${state} -whdr ${hdr} -r ${flow} -st ${syr} ${smo} ${sdy} ${shr} -ed ${eyr} ${emo} ${edy} ${ehr} -pre ${outfile} -s ${m} ${k} -sv ${m} ${k} -svalt ${po} ${pa} -gw ${gw1} ${gw2} -g -b -p -c | tee ${logfile}

${RHESSys} -firespin 20 50 -netcdfgrid -ncgridinterp 10 -t ${tec} -w ${state} -whdr ${hdr} -r ${flow} -st ${syr} ${smo} ${sdy} ${shr} -ed ${eyr} ${emo} ${edy} ${ehr} -pre ${outfile} -s ${m} ${k} -sv ${m} ${k} -svalt ${po} ${pa} -gw ${gw1} ${gw2} -g -b -p -c


