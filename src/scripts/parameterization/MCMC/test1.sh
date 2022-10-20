#!/bin/bash

droot="/home/jon/rhessys/tools/parameterization"
source_default=${droot}/stratum_evergreen_mode.def # default version (contains CAL0, CAL1, CAL2 ...)
target_default=${droot}/stratum_evergreen.def      # updated version (copy of source -> modified to replace CAL0, CAL1, CAL2 below)

cp $source_default $target_default

CAL=(0 1 2 3 4 5 6 7 8 9 10);

sed -i "s/CAL0/${CAL[0]}/g" $target_default
sed -i "s/CAL1/${CAL[1]}/g" $target_default
sed -i "s/CAL2/${CAL[2]}/g" $target_default
sed -i "s/CAL3/${CAL[3]}/g" $target_default
sed -i "s/CAL4/${CAL[4]}/g" $target_default
sed -i "s/CAL5/${CAL[5]}/g" $target_default
sed -i "s/CAL6/${CAL[6]}/g" $target_default
sed -i "s/CAL7/${CAL[7]}/g" $target_default
sed -i "s/CAL8/${CAL[8]}/g" $target_default
sed -i "s/CAL9/${CAL[9]}/g" $target_default
sed -i "s/CAL10/${CAL[10]}/g" $target_default


