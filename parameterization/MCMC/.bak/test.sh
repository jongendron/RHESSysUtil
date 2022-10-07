prefix0="veg_param"
py_likelyhood="growth_yearly_model_performance_nppratio_height_npp_LAI.py"
growth_year="output/${prefix0}_grow_stratum.yearly"
distfile="output/${prefix0}_npp_gpp_ratio.txt"

valid_start_year="1990"
valid_end_year="2015"
valid_veg_id=1

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

python ${py_likelyhood} ${growth_year} ${valid_start_year} ${valid_end_year} ${valid_veg_id} ${target[0]} ${target_stddev[0]} ${target[1]} ${target_stddev[1]} ${target[2]} ${target_stddev[2]} ${target[3]} ${target_stddev[3]} ${distfile}

