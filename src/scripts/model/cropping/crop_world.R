#############################################################################
### Crops the Basin Worldfile to only use target hillslopes in South Fork ###
#############################################################################
library(tidyverse);
library(raster);
library(rgdal);
library(sf);
library(RColorBrewer)

Input = "."             # Basin be cropped (directory name)
Input_dir = "."    # Input Directory
#Input_dir = "../Templates"
Input_file = "br_veg_spun_and_stable.state.Y2015M1D1H1.state"
Output = "."     # Cropped basin name (directory name)
Output_dir = "."
Output_file = "cal_brw_init.state"

Home_dir = getwd()
Input_dir = normalizePath(Input_dir)     # path to data for statefile to be cropped
Output_dir = normalizePath(Output_dir)  # path to Output directory to write cropped statefile 
source("./get_state_hierarchy.R")

#################################
## Load Hillslopes and patches ##
## If using a mask raster      ##
#################################
setwd(Input_dir)
#basin.hs = raster("./TC_patches.tif");
#basin.pch = raster("./basin/patches.tif");
# basin.sb = raster("./basin/subbasins.tif");
# subbas = raster("./sfork/sfork.tif");


############################################
## mask hillslopes and patches for subbas  ##
## and get list of hillslopes and sbasins ##
############################################
##subbas.pch = mask(basin.pch,subbas);
#subbas.pch = raster("./TC_sb1_patches.tif")
#subbas.pch[subbas.pch[] == -9999] = NA
#tar.pch = subbas.pch[] %>% unique() %>% .[!is.na(.)]
## subbas.sb = mask(basin.sb,subbas)
## tar.sb = subbas.sb[] %>% unique() %>% .[!is.na(.)]
#tar.sb = 410
##tar.pch = c(79708,79709,80100) # patches in test_basin 1
##tar.sb = c(356)
tar.hier = read.csv("./cal_hier_tbl.csv") %>% as_tibble()
tar.sb = tar.hier$hillslopeID %>% unique()
tar.pch = tar.hier$patchID %>% unique()

################################################
## Identify hierarchy components of worldfile ##
################################################

# If hierarchy table exists then skip and load it
statefile = Input_file # select full model state file to crop
basin = state_hier(statefile)

#################################
## mask hillslopes and patches ##
#################################
basin = basin %>%
  dplyr::filter(
    hillslope_ID %in% c(NA,tar.sb),
    zone_ID %in% c(NA,tar.pch)
    )

basin_bk4 = basin

########################################
## Count number members in each layer ##
########################################
nlvl = tibble(
  #V2 = c("num_basins", "num_hillslopes", "num_zones", "num_patches", "num_canopy_strat"),
  V2 = c("num_basins", "num_hillslopes", "num_zones"),
  lvl2 = 1:3
)  

basin = left_join(basin,nlvl)

num_basins = tibble(
  world_ID = 1,
  basin_ID = 1,
  size = 1,
  lvl = 999,
  lvl2 = 1
)  # only 1

# num_basins = basin %>%
#   dplyr::filter(lvl == 2) %>%
#   group_by(world_ID) %>%
#   summarise(size = n()) %>%
#   mutate(
#     lvl = 999,
#     lvl2 = 1
#   )

num_hillslopes = basin %>%
  dplyr::filter(lvl == 3) %>%
  group_by(world_ID,basin_ID) %>%
  summarise(size = n()) %>%
  mutate(
    lvl = 999,
    lvl2 = 2
  )

num_zones = basin %>%
  dplyr::filter(lvl == 4) %>%
  group_by(world_ID,basin_ID,hillslope_ID) %>%
  summarise(size = n()) %>%
  mutate(
    lvl = 999,
    lvl2 = 3
  )

# num_patches = 1 for every zone
# num_canopy_strata = 1 for every patch

num_tbl = bind_rows(num_zones,num_hillslopes,num_basins) %>%
  arrange(lvl2,world_ID,basin_ID,hillslope_ID)

basin = left_join(basin,num_tbl)

basin_bk5 = basin

#######################################
## Update the hierarchy layer counts ##
#######################################
#tmp = basin[!is.na(basin$lvl2),]
#tmp[tmp$V1 != tmp$size,] # only two counts differ from original values]
#basin$V1[!is.na(basin$lvl2)] == basin$size[!is.na(basin$lvl2)]
basin$V1[!is.na(basin$lvl2)] = basin$size[!is.na(basin$lvl2)] # set V2 = size (updates count)
#basin$V1[!is.na(basin$lvl2)] == basin$size[!is.na(basin$lvl2)] # double check

basin_bk6 = basin

####################
## Write the file ##
####################
options(scipen = 999)

subbas = basin %>%
  ungroup() %>%
  dplyr::select(V1,V2)

subbas = Map(
  function(v1,v2){
    paste(
      sprintf("%-25s %-25s",v1,v2)
    )
  },subbas$V1,subbas$V2
) %>%
  unlist()

dir.create(Output_dir,showWarnings = T,recursive = T)
setwd(Output_dir)
#write.table(x = subbas, file = Output_file, quote = F, sep = "\t", row.names = F, col.names = F)
write_lines(x = subbas, path = Output_file, sep = "\n")

readLines("./cal_brw_init.state")
setwd(Home_dir)
