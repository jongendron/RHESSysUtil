## This script will create the target driven spinup targets file ##
library(tidyverse)
library(raster)
source("../get_state_hierarchy.R")

# Create a spatial hierarchy table (basinID, hillslopeID, zoneID, patchID) from statefile
file0 = "./TC_hs410.state"

state0 = read.table("TC_hs410.state",header = F, as.is = T)
state0$idx = 1:nrow(state0)
state0$V1[state0$V2 == "veg_parm_ID" & state0$V1 == 3] = 1 # switch to evergreen
state0$V1[state0$V2 == "veg_parm_ID" & state0$V1 == 51] = 50 # switch to evergreen
state0$idx = NULL
state0

write.table(state0,"TC_hs410_evergreen.state",quote = F,row.names = F, col.names = F)





