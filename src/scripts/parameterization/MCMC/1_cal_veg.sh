#!/bin/bash

## This workflow is setup to work with RHESSys output from a single patch
# Presently growth_stratum.daily output is considered but can be modded
prefix0="veg_param9"

py_likelyhood="/home/jon/rhessys/tools/parameterization/2_likelyhood_growth_yearly_AGB_height.py"
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
echo "idx cal0 cal1 cal2 cal3 cal4 cal5 cal6 cal7 cal8 cal9 cal10 likelyhood" > $outpfile

# RHESSys simulation input setting #

growth_year=${droot}/output/${prefix0}_grow_stratum.yearly # defines name of RHESSys output file analyized by mcmc procedure of Python script
#distfile=${droot}/Outputs/dist_npp_gpp_ratio.txt
likefile=${droot}/output/${prefix0}_likelyhood_table.txt # logs likelyhood of each model output variable for each parameter set tested
likefile2=${droot}/output/likelyhood_table.txt
avgfile=${droot}/output/${prefix0}_avg_table.txt # logs avg values used to calculate likelyhood
avgfile2=${droot}/output/avg_table.txt
distfile=${droot}/output/${prefix0}_npp_gpp_ratio.txt # defines name of npp_gpp_ratio file for mcmc procedure of Python script
tempGaussRandom=${droot}/output/${prefix0}_testGauseRandom.txt # defines name of Guasian Random number file of mcmc procedure of Python script
valid_start_year=2054 # defines start year that mcmc will begin using RHESSys output
valid_end_year=2104   # defines end year that mcmc will end using RHESSys output
valid_veg_id=1 # defines the veg_parm_id of startum layer to be used for processing (extracted from statefile)
rhessys_syr=1979
rhessys_eyr=2105 # valid_end_year + 1 = (1979 + 125 + 1) 2105 = 1979 + 125 + 1

#target0: AGBc --> above ground biomass carbon (kgC/m2/year)
#target1: height --> overstory canopy height (m)

declare -a target
declare -a target_stddev
target[0]=22.27 # sets param 1 target AGBc (kgC/m2) | H.J. Andrews ~300 year old forest 
target_stddev[0]=`echo "scale=6; 0.3*${target[0]}" | bc` # sets param1 target standard deviation
target[1]=31.5 # height (m) | BRW ~100 year old forest (2019)
target_stddev[1]=`echo "scale=6; 0.3*${target[1]}" | bc` 
target[2]=4.0 # LAI (m2/m2) | brw 2015 - 2017 avg
target_stddev[2]=`echo "scale=6; 0.3*${target[2]}" | bc`
target[3]=0.801 # NPP (GPP - MR) (kgC/m2/yr) | brw 2015 - 2019 avg
target_stddev[3]=`echo "scale=6; 0.3*${target[3]}" | bc`
target[4]=0.528 # NPP/GPP | brw 2015 - 2019 avg
target_stddev[4]=`echo "scale=6; 0.3*${target[4]}" | bc`
printf "%-12s\t%-12s\t%-12s\t%-12s\t%-12s\t%-12s\n" "idx" "AGBc" "height" "LAI" "NPP" "NPP/GPP" > ${likefile2}
printf "%-12s\t%-12s\t%-12s\t%-12s\t%-12s\t%-12s\n" "idx" "AGBc" "height" "LAI" "NPP" "NPP/GPP" > ${avgfile2}

echo "New" > ${droot}/echo_test_likelihood.txt
#CAL0 epc.alloc_frootc_leafc    # (0.01,0.999)
#CAL1 epc.alloc_crootc_stemc    # (0.01,0.999)
#CAL2 epc.alloc_stemc_leafc     # (0.01,0.999)
#CAL3 epc.alloc_livewoodc_woodc # (0.01,0.999)
#CAL4 epc.alloc_prop_day_growth # (0.01,0.999)
#CAL5 epc.height_to_stem_exp    # (0.01,0.50)
#CAL6 epc.height_to_stem_coef   # (1.00,15.00)
#CAL7 epc.dickenson_pa          # (0.01,0.2)
#CAL8 mrc.per_N
#CAL9 epc.proj_sla
#CAL10 epc.max_daily_mortality


# calibration parameter ranges

# Old
declare -a min_c
declare -a max_c
min_c[0]=0.400	# alloc_frootc_leafc  [0.652,0.999]
max_c[0]=0.600
min_c[1]=0.350	# alloc_crootc_stemc [0.189,0.351]
max_c[1]=0.550
min_c[2]=0.750	# alloc_stemc_leafc [0.596,0.999]  
max_c[2]=0.950
min_c[3]=0.060	# alloc_livewoodc_woodc [0.0497,0.0923]
max_c[3]=0.120
min_c[4]=0.100	# alloc_prop_day_growth [0.07,0.13]  
max_c[4]=0.200
min_c[5]=0.375	# height_to_stem_exp [0.25,0.60] # more weighted lower (not +- 30%)
max_c[5]=0.575
min_c[6]=7.000	# height_to_stem_coef [7.97,14.8]
max_c[6]=9.000 
min_c[7]=0.400	# epc.dickenson_pa [0.105,0.195] -> try [0.40 - 0.60] | these control allocation of carbon to leaves (if LAI is higher LAI should decrease)
max_c[7]=0.600
min_c[8]=0.100	# mrc.per_N [0.0784,0.146]
max_c[8]=0.200 
min_c[9]=4.000	# epc.proj_sla [6.04,11.2]
max_c[9]=8.000
min_c[10]=0.025 # epc.max_daily_mortality [0.005,0.02]
max_c[10]=0.035  

# Set calibration parameters
echo "Setting calibraton parameters";
declare -a CAL
declare -a dtrange
for cidx in 0 1 2 3 4 5 6 7 8 9 10;do
    test=$(shuf -i0-100 -n1)
    min=${min_c[$cidx]}
    max=${max_c[$cidx]}
    CAL[${cidx}]=`echo "scale=6; $test*0.01*(${max}-${min})+${min}" | bc`
    dtrange[${cidx}]=`echo "scale=6; 0.05*(${max}-${min})" | bc` # This sets the step distant (standard deviation of proposal distribution) # Default: 0.05*(max - min) for each parameter 
    #dtrange[${cidx}]=`echo "scale=6; 0.20*(${max}-${min})" | bc`
    echo cidx:$cidx min:${min} max:${max}
done

#printf '%s\n' "${CAL[@]}"; 
echo
echo "Initial Parameters: ${CAL[@]}";

declare -a old_CAL
declare -a dt
idx=1 # initialize simulation index value
#while [ $idx -le 200 ]
#while [ $idx -le 2000 ]
while [ $idx -le 2000 ]
do
	echo 
	echo "Iteration: $idx"
	echo
	echo "CAL: ${CAL[@]}";
    #echo $idx $CALq10 $CALper_N
    
    # Copy default .def file -> new file
    # replace parameter values of CAL0, CAL1, and CAL2
    # with values in CAL[] array 
    cp $source_default $target_default
    sed -i "s:CAL0\s:${CAL[0]}:g" $target_default
    #sed -i "s/CAL1/${CAL[1]}/g" $target_default
    sed -i "s:CAL1\s:${CAL[1]}:g" $target_default
    sed -i "s:CAL2\s:${CAL[2]}:g" $target_default
    sed -i "s:CAL3\s:${CAL[3]}:g" $target_default
    sed -i "s:CAL4\s:${CAL[4]}:g" $target_default
    sed -i "s:CAL5\s:${CAL[5]}:g" $target_default
    sed -i "s:CAL6\s:${CAL[6]}:g" $target_default
    sed -i "s:CAL7\s:${CAL[7]}:g" $target_default
    sed -i "s:CAL8\s:${CAL[8]}:g" $target_default
    sed -i "s:CAL9\s:${CAL[9]}:g" $target_default
    #sed -i "s/CAL10/${CAL[10]}/g" $target_default
    sed -i "s:CAL10\s:${CAL[10]}:g" $target_default
    
    #run RHESSys
#    ${RHESSys} -netcdfgrid -ncgridinterp 10 -t calibration.tec -w world_file_patchID_100951_100952.txt -whdr  defFiles.hdr  -st 1979 01 01 01 -ed 2015 12 31 24 -pre ./Outputs/spinup_fire_ -s 5.200298 54.26672 -sv 5.200298 54.26672 -svalt 1.143066 3.829007 -gw 0.604857 0.3806356 -r flowtable_100951_100952.txt -b -g -p -c -h -z -firespread 100 patchGrid.txt DemGrid.txt -firemort 0.71 -9999  -9999 0.52 4.05 -10 1 -firespin 10 50
	cd ${rhessys_input_root}
	
	echo
	${RHESSys} -climrepeat -netcdfgrid -ncgridinterp 10 -t patch_basin_1979.tec -w patch_basin_init_clrveg_overstory.state -whdr cal_patch_basin.hdr -r patch_basin.flow -st ${rhessys_syr} 10 01 01 -ed ${rhessys_eyr} 09 30 24 -pre ${droot}/output/${prefix0} -s 1.00 5.241 -sv 1.00 5.241 -svalt 0.622 0.500 -gw 0.010 0.049 -g -b -c > stdout_rhessys.txt
	echo
	echo
	cd ${droot}

    #-firespin 10 50
    #cal likelihood (squre dist)
    python ${py_likelyhood} ${growth_year} ${valid_start_year} ${valid_end_year} ${valid_veg_id} ${target[0]} ${target_stddev[0]} ${target[1]} ${target_stddev[1]} ${target[2]} ${target_stddev[2]} ${target[3]} ${target_stddev[3]} ${target[4]} ${target_stddev[4]} ${idx} ${avgfile} ${likefile} ${distfile};

    likelihood=$(head -n 1 ${distfile})
    if [ $idx -eq 1 ]; then
        old_likelihood=${likelihood}
        #tv=`echo "scale=4;$idx $CALq10 $CALper_N ${likelihood}" | bc -l`
        printf "%d %.4f %.4f %.4f %.4f %.4f %.4f %.4f %.4f %.4f %.4f %.4f %.4f\n" $idx ${CAL[0]} ${CAL[1]} ${CAL[2]} ${CAL[3]} ${CAL[4]} ${CAL[5]} ${CAL[6]} ${CAL[7]} ${CAL[8]} ${CAL[9]} ${CAL[10]} ${likelihood} >> $outpfile
        update=1
        for cidx in 0 1 2 3 4 5 6 7 8 9 10;do
            old_CAL[$cidx]=${CAL[$cidx]}
        done
	cat ${likefile} >> ${likefile2}
	cat ${avgfile} >> ${avgfile2}
    else
	echo
	old_lng=${old_likelihood#*.};old_lng=${#old_lng};
	new_lng=${likelihood#*.};new_lng=${#new_lng};	
	echo "old_likelihood: ${old_likelihood} digits: ${old_lng}"
	echo "likelihood: ${likelihood} digits: ${new_lng}"
        beta=`echo "scale=6; ${likelihood}/${old_likelihood}" | bc`
        u=$(shuf -i0-100 -n1)
        ru=`echo "scale=6; ${u}*0.01" | bc`
        echo idx:$idx beta:${beta} ru:${ru} perf:${likelihood} old_perf:${old_likelihood} cal0:${CAL[0]} cal1:${CAL[1]} cal2:${CAL[2]} cal3:${CAL[3]} cal4:${CAL[4]} cal5:${CAL[5]} cal6:${CAL[6]} cal7:${CAL[7]} cal8:${CAL[8]} cal9:${CAL[9]} cal10:${CAL[10]} >> $debug_file
        if (( $(echo "${ru} <= ${beta}" | bc -l) ))
        then
            #accept
            update=1
            echo accept! >> $debug_file
            printf "%d %.4f %.4f %.4f %.4f %.4f %.4f %.4f %.4f %.4f %.4f %.4f %.8f\n" $idx ${CAL[0]} ${CAL[1]} ${CAL[2]} ${CAL[3]} ${CAL[4]} ${CAL[5]} ${CAL[6]} ${CAL[7]} ${CAL[8]} ${CAL[9]} ${CAL[10]} ${likelihood} >> $outpfile
            old_likelihood=${likelihood}
            for cidx in 0 1 2 3 4 5 6 7 8 9 10;do
                old_CAL[$cidx]=${CAL[$cidx]}
            done
	    cat ${likefile} >> ${likefile2}
	    cat ${avgfile} >> ${avgfile2}
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
    for cidx in 0 1 2 3 4 5 6 7 8 9 10;do
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
    
    #echo idx:$idx old_cal0:${old_CAL[0]} proposed_cal0:${CAL[0]} dt0:${dt[0]} old_cal1:${old_CAL[1]} proposed_cal1:${CAL[1]} dt1:${dt[1]} old_cal2:${old_CAL[2]} proposed_cal2:${CAL[2]} dt2:${dt[2]} >> $debug_file
    echo \
	idx:$idx old_cal0:${old_CAL[0]} proposed_cal0:${CAL[0]} dt0:${dt[0]} \
	old_cal1:${old_CAL[1]} proposed_cal1:${CAL[1]} dt1:${dt[1]} \
	old_cal2:${old_CAL[2]} proposed_cal2:${CAL[2]} dt2:${dt[2]} \
	old_cal3:${old_CAL[3]} proposed_cal3:${CAL[3]} dt3:${dt[3]} \
	old_cal4:${old_CAL[4]} proposed_cal4:${CAL[4]} dt4:${dt[4]} \
	old_cal5:${old_CAL[5]} proposed_cal5:${CAL[5]} dt5:${dt[5]} \
	old_cal6:${old_CAL[6]} proposed_cal6:${CAL[6]} dt6:${dt[6]} \
	old_cal7:${old_CAL[7]} proposed_cal7:${CAL[7]} dt7:${dt[7]}  \
	old_cal8:${old_CAL[8]} proposed_cal8:${CAL[8]} dt8:${dt[8]} \
        old_cal9:${old_CAL[9]} proposed_cal9:${CAL[9]} dt9:${dt[9]} \
        old_cal10:${old_CAL[10]} proposed_cal10:${CAL[10]} dt10:${dt[10]}  \
	>> $debug_file
    
    idx=$(( $idx + 1 ))

done

paste ${outpfile} ${likefile2} > ${droot}/output/${prefix0}_mcmc_like_tbl.txt
paste ${outpfile} ${avgfile2} > ${droot}/output/${prefix0}_mcmc_avg_tbl.txt

