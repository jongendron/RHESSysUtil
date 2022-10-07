## This script will create the target driven spinup targets file ##
library(tidyverse)
library(raster)
source("../get_state_hierarchy.R")
target = "height" # overstory canopy height (m)
Outfile = "TC_tds.txt"
# Create a spatial hierarchy table (basinID, hillslopeID, zoneID, patchID) from statefile
file0 = "./TC_hs410_evergreen.state"
hier0 = state_hier(file0,Hillslope=T,Zone=TRUE,Patch=T,Stratum=T)

# Filter to only include rows with unique canopy_strata_ID for overstory canopy strata
# In this example all patches have overstory vegetation set to evergreen (veg_parm_ID == 50)
# so we just filter by that
# depending on how you set up your model you will need to revise this scrip to isolate the rows
# There should only be one row for each unique canopy strata
# Convention for naming canopy strata is to have overstory have overstory canopy_strata_ID == patch_ID

hier = hier0 %>%
  dplyr::ungroup() %>%
  dplyr::filter(V1 == 50 & V2 == "veg_parm_ID") %>% # veg_parm_ID = 50 is evergreen statratum for overstory layer
  dplyr::select(basin_ID:canopy_strata_ID)

names(hier) = c("basin_ID","hill_ID","zone_ID","patch_ID","stratum_ID")

# Create target table
# In this case we are using canopy height (m)
target_rast= "./TC_tar_canopy_ht.tif" # raster with same dimensions & # cellls as model but with TDS targets
patchID_rast = "./TC_sb1_patches.tif" # patchID raster that links patches to their patchID
target_rast2 = stack(raster(target_rast),raster(patchID_rast))
target_tbl = target_rast2 %>% as.data.frame(xy = T) %>% as_tibble
names(target_tbl) = c("x","y",target,"patch_ID")
target_tbl = target_tbl %>% dplyr::filter(patch_ID != -9999) # remove boundary cells
target_tbl = target_tbl %>% dplyr::select(-x,-y)

# Merge target table with hierarchy table
tds = left_join(hier,target_tbl,by = "patch_ID")
tds[[target]] = round(tds[[target]],digits = 2)

# Create body of the file

body0 = Map(
  function(v1,v2,v3,v4,v5,v6){
    paste(
      sprintf("%-15s %-15s %-15s %-15s %-15s %-15s",v1,v2,v3,v4,v5,v6)
    )
  },tds$basin_ID,tds$hill_ID,tds$zone_ID,tds$patch_ID,tds$stratum_ID,tds[[target]]
) %>%
  unlist()

# Create header of file
num_stratum = nrow(tds) # number of stratum layers with targets
num_target = 1 # number of targets to spinup by

l0 = list()
for(i in 1:length(colnames(tds))){
  l0[[i]] = sprintf("%-15s",colnames(tds)[i])  
}
l0 = l0 %>% unlist()

hdr0 = list(
  paste(sprintf("%-15s %-15s",num_stratum,"num_stratum")),
  paste(sprintf("%-15s %-15s",num_target,"num_targets")),
  paste(sprintf("%-15s",target)),
  paste(l0,collapse = " ")
  
  
) %>% unlist()


# Merge the header and body
tds_file = append(hdr0,body0)

write_lines(x = tds_file, path = Outfile, sep = "\n")

