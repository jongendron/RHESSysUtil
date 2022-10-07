#!/bin/bash

## This workflow is setup to work with RHESSys output from a single patch
# Presently growth_stratum.daily output is considered but can be modded

#RHESSys="/home/liuming/RHESSys_Ning/RHESSys/build/Qt/gcc/build-RHESSys-Generic_Linux-Debug/RHESSys"
#RHESSys="/home/jon/rhessys/tools/parameterization/RHESSys"
#py_likelyhood="/home/liuming/dev/toolkit/ForRHESSys/growth_yearly_model_performance.py"
#py_likelyhood="/home/liuming/dev/toolkit/ForRHESSys/growth_yearly_model_performance_nppratio_height_npp_LAI.py"
#py_likelyhood="/home/jon/rhessys/tools/parameterization/growth_yearly_model_performance_nppratio_height_npp_LAI.py"
py_likelyhood="/home/jon/rhessys/tools/parameterization/growth_yearly_model_performance_AGBc_height_LAI.py"
#droot="/home/liuming/mnt/hydronas2/Projects/FireEarth/Cedar"
droot="/home/jon/rhessys/tools/parameterization"
RHESSys="${droot}/RHESSys_8p2"
rhessys_input_root="${droot}/input"

# Define definitation files paths to parameterize
source_default=${droot}/stratum_evergreen_mode.def # default version (contains CAL0, CAL1, CAL2 ...)
target_default=${droot}/stratum_evergreen.def      # updated version (copy of source -> modified to replace CAL0, CAL1, CAL2 below)

#outpfile=${droot}/Outputs/mrcoef_likelihood_mcmc.txt
outpfile=${droot}/output/mrcoef_likelihood_mcmc.txt # output file1 from mcmc procedure (Python script)

debug_file=${droot}/output/echo_test_likelihood.txt # output file2 from mcm procedure (Python script)

echo
echo "idx cal0 cal1 cal2 likelyhood" > $outpfile

# RHESSys simulation input setting #
prefix0="veg_param"

#growth_year=${droot}/Outputs/spinup_fire__grow_stratum.yearly # name of file to go into python script for grow_Stratum_yearly | prefix in prefix_grow_stratum.yearly must be same as what is used in RHESSys output
growth_year=${droot}/output/${prefix0}_grow_stratum.yearly # defines name of RHESSys output file analyized by mcmc procedure of Python script
#distfile=${droot}/Outputs/dist_npp_gpp_ratio.txt
distfile=${droot}/output/${prefix0}_npp_gpp_ratio.txt # defines name of npp_gpp_ratio file for mcmc procedure of Python script
#tempGaussRandom=${droot}/Outputs/testGauseRandom.txt
tempGaussRandom=${droot}/output/${prefix0}_testGauseRandom.txt # defines name of Guasian Random number file of mcmc procedure of Python script
valid_start_year=2279 # defines start year that mcmc will begin using RHESSys output
valid_end_year=2329   # defines end year that mcmc will end using RHESSys output
valid_veg_id=1 # defines the veg_parm_id of startum layer to be used for processing (extracted from statefile)
rhessys_syr=1979
rhessys_eyr=2330 # valid_end_year + 1
#valid_stratum_id=79708 # defines the stratum ID to be used 

#target0: npp/gpp ratio (old) --> Above ground biomass carbon (kgC/m2/year) (new)
#target1: height (m) --> height (m)
#target2: npp (kgC/m2/year) --> LAI (m2/m2) (new)
#target3: LAI (m2/m2ï¼‰--> NA

declare -a target
declare -a target_stddev
target[0]=0.5 # sets param 1 target value (npp/gpp)
target_stddev[0]=0.051 # sets param1 target standard deviation
target[1]=39 # height
target_stddev[1]=`echo "scale=6; 0.3*${target[1]}" | bc`
target[2]=1.4 # npp
target_stddev[2]=`echo "scale=6; 0.3*${target[2]}" | bc`
#from MODIS (5%), then double it
#target_stddev[2]=`echo "scale=6; 0.1*${target[2]}" | bc`
target[3]=9.0 # LAI
target_stddev[3]=`echo "scale=6; 0.3*${target[3]}" | bc`
#target[0]=22.27 # ABGc (kgC/m2)(above ground biomass carbon) H.J Andrews 1996
#target_stddev[0]=`echo "scale=6; 0.3*${target[0]}" | bc`
#target[1]=30 # height (m) of mature evergreen forest of H.J Andrews 1996
#target_stddev[1]=`echo "scale=6; 0.3*${target[1]}" | bc`
#target[2]=7.1 # LAI
#target_stddev[2]=`echo "scale=6; 0.3*${target[2]}" | bc`
#from MODIS (5%), then double it
#target_stddev[2]=`echo "scale=6; 0.1*${target[2]}" | bc`
#target[3]=9.0 # LAI
#target_stddev[3]=`echo "scale=6; 0.3*${target[3]}" | bc`

#1.8-2.2
#CALq10=1.9
#0.1-0.5
#CALper_N=0.25
echo "New" > ${droot}/echo_test_likelihood.txt
#CAL0 mrc.per_N
#CAL1 epc.proj_sla
#CAL2 epc.max_daily_mortality

#first try
#min_c0=0.05
#max_c0=0.25
#min_c1=10
#max_c1=30
#min_c2=0.001
#max_c2=0.02

#second try
declare -a min_c
declare -a max_c
min_c[0]=0.06  # (orig) 0.06
max_c[0]=0.14  # (orig) 0.14
min_c[1]=3     # (orig) 3
max_c[1]=20    # (orig) 20
min_c[2]=0.005 # (orig) 0.005
max_c[2]=0.02  # (orig) 0.02

declare -a CAL
declare -a dtrange
for cidx in 0 1 2;do
    test=$(shuf -i0-100 -n1)
    min=${min_c[$cidx]}
    max=${max_c[$cidx]}
    CAL[${cidx}]=`echo "scale=6; $test*0.01*(${max}-${min})+${min}" | bc`
    dtrange[${cidx}]=`echo "scale=6; 0.05*(${max}-${min})" | bc` # This sets the step distant (standard deviation of proposal distribution) # Default: 0.05*(max - min) for each parameter 
    #dtrange[${cidx}]=`echo "scale=6; 0.20*(${max}-${min})" | bc`
    echo cidx:$cidx min:${min} max:${max}
done

declare -a old_CAL
declare -a dt
idx=1 # initialize simulation index value
#while [ $idx -le 200 ]
#while [ $idx -le 2000 ]
while [ $idx -le 2000 ]
do
	echo 
	echo "Iteration: $idx"
    #echo $idx $CALq10 $CALper_N
    
    # Copy default .def file -> new file
    # replace parameter values of CAL0, CAL1, and CAL2
    # with values in CAL[] array 
    cp $source_default $target_default
    sed -i "s/CAL0/${CAL[0]}/g" $target_default
    sed -i "s/CAL1/${CAL[1]}/g" $target_default
    sed -i "s/CAL2/${CAL[2]}/g" $target_default
    
    #run RHESSys
#    ${RHESSys} -netcdfgrid -ncgridinterp 10 -t calibration.tec -w world_file_patchID_100951_100952.txt -whdr  defFiles.hdr  -st 1979 01 01 01 -ed 2015 12 31 24 -pre ./Outputs/spinup_fire_ -s 5.200298 54.26672 -sv 5.200298 54.26672 -svalt 1.143066 3.829007 -gw 0.604857 0.3806356 -r flowtable_100951_100952.txt -b -g -p -c -h -z -firespread 100 patchGrid.txt DemGrid.txt -firemort 0.71 -9999  -9999 0.52 4.05 -10 1 -firespin 10 50
	cd ${rhessys_input_root}
	
	echo
	${RHESSys} -climrepeat -netcdfgrid -ncgridinterp 10 -t patch_basin_1979.tec -w patch_basin_init_clrveg.state -whdr cal_patch_basin.hdr -r patch_basin.flow -st ${rhessys_syr} 10 01 01 -ed ${rhessys_eyr} 09 30 24 -pre ${droot}/output/${prefix0} -s 1.00 5.241 -sv 1.00 5.241 -svalt 0.622 0.500 -gw 0.010 0.049 -g -b -c > stdout_rhessys.txt
	echo
	echo
	cd ${droot}

    #-firespin 10 50
    #cal likelihood (squre dist)
    python ${py_likelyhood} ${growth_year} ${valid_start_year} ${valid_end_year} ${valid_veg_id} ${target[0]} ${target_stddev[0]} ${target[1]} ${target_stddev[1]} ${target[2]} ${target_stddev[2]} ${target[3]} ${target_stddev[3]} ${distfile}

    likelihood=$(head -n 1 ${distfile})
    if [ $idx -eq 1 ]; then
        old_likelihood=${likelihood}
        #tv=`echo "scale=4;$idx $CALq10 $CALper_N ${likelihood}" | bc -l`
        printf "%d %.4f %.4f %.4f %.4f\n" $idx ${CAL[0]} ${CAL[1]} ${CAL[2]} ${likelihood} >> $outpfile
        update=1
        for cidx in 0 1 2;do
            old_CAL[$cidx]=${CAL[$cidx]}
        done
    else
	echo
	old_lng=${old_likelihood#*.};old_lng=${#old_lng};
	new_lng=${likelihood#*.};new_lng=${#new_lng};	
	echo "old_likelihood: ${old_likelihood} digits: ${old_lng}"
	echo "likelihood: ${likelihood} digits: ${new_lng}"
        beta=`echo "scale=6; ${likelihood}/${old_likelihood}" | bc`
        u=$(shuf -i0-100 -n1)
        ru=`echo "scale=6; ${u}*0.01" | bc`
        echo idx:$idx beta:${beta} ru:${ru} perf:${likelihood} old_perf:${old_likelihood} cal0:${CAL[0]} cal1:${CAL[1]} cal2:${CAL[2]} >> $debug_file
        if (( $(echo "${ru} <= ${beta}" | bc -l) ))
        then
            #accept
            update=1
            echo accept! >> $debug_file
            printf "%d %.4f %.4f %.4f %.8f\n" $idx ${CAL[0]} ${CAL[1]} ${CAL[2]} ${likelihood} >> $outpfile
            old_likelihood=${likelihood}
            for cidx in 0 1 2;do
                old_CAL[$cidx]=${CAL[$cidx]}
            done
        else
            #not accept
            echo not accept! >> $debug_file
            #CAL0=${old_CAL0}
            #CAL1=${old_CAL1}
            #CAL1=${old_CAL2}
        fi
    fi
    
    #old_CAL0=${CAL0}
    #old_CAL1=${CAL1}
    #old_CAL2=${CAL2}

    #generate proposal
    for cidx in 0 1 2;do
    python ${droot}/generate_gauss_random.py 0 ${dtrange[${cidx}]} $tempGaussRandom # generates value to be added to old target parameter (changes for next sim)
        dt[${cidx}]=$(head -n 1 ${tempGaussRandom})
        ldt=${dt[${cidx}]}
        orig=${old_CAL[${cidx}]}
        CAL[${cidx}]=`echo "scale=6; ${orig}+${ldt}" | bc -l`
        min=${min_c[${cidx}]} # minimum boundary of parameter
        max=${max_c[${cidx}]} # maximum boundary of paramter
        current=${CAL[${cidx}]}
        if (( $(echo "${current} > ${max}" | bc -l) )); then
            CAL[${cidx}]=${max}
        else
            if (( $(echo "${current} < ${min}" | bc -l) )); then
                CAL[${cidx}]=${min}
            fi
        fi
    done
    
    echo idx:$idx old_cal0:${old_CAL[0]} proposed_cal0:${CAL[0]} dt0:${dt[0]} old_cal1:${old_CAL[1]} proposed_cal1:${CAL[1]} dt1:${dt[1]} old_cal2:${old_CAL[2]} proposed_cal2:${CAL[2]} dt2:${dt[2]} >> $debug_file
    
    idx=$(( $idx + 1 ))

done

