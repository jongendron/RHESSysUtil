library(tidyverse)
library(raster)

calldir = getwd()

#%% Load all spatial layer rasters and overstory
tardir = normalizePath("C:/Users/PETBUser/OneDrive - Washington State University (email.wsu.edu)/Research/BRW_project/Modeling/RHESSys/5_calibration/1_mask_basin/3_gen_wrld_and_flow/1_build_world/input/rasters")
setwd(tardir)

flist = c(
  "bullrun_basin.tif",
  "subbasins.tif",
  "patches.tif",
  "patches.tif",
  "stratum.tif"
)

tlist = c(
  "basinID",
  "hillslopeID",
  "zoneID",
  "patchID",
  "stratumID"
)

for(i in 1:length(flist)){
  rtmp = raster(flist[i])
  names(rtmp) = tlist[i]
  if(i == 1){
    rover = rtmp
  } else{
    rover = stack(rover, rtmp)
  }
}

rover$stratumID[] %>% table() %>% as.data.frame()

# load all spatial layer rasters and understory
flist = c("bullrun_basin.tif",
          "subbasins.tif",
          "patches.tif",
          "patches.tif",
          "understory.tif"
)

tlist = c(
  "basinID",
  "hillslopeID",
  "zoneID",
  "patchID",
  "stratumID"
)

for(i in 1:length(flist)){
  rtmp = raster(flist[i])
  names(rtmp) = tlist[i]
  if(i == 1){
    runder = rtmp
  } else{
    runder = stack(runder, rtmp)
  }
}

runder$stratumID[] %>% table() %>% as.data.frame()

# Convert both to dataframe and merge
over = as.data.frame(rover, xy=TRUE) %>% dplyr::filter(!is.na(basinID))
under = as.data.frame(runder, xy=TRUE) %>% dplyr::filter(!is.na(basinID))
rhier = bind_rows(over,under)
rhier_cal = rhier %>% dplyr::arrange(., basinID, hillslopeID, zoneID, patchID, stratumID)

setwd(calldir)
write_csv(rhier_cal,file="cal_hier_tbl.csv")


# #%% Load Full model data
# tardir = normalizePath("C:/Users/PETBUser/OneDrive - Washington State University (email.wsu.edu)/Research/BRW_project/Modeling/Create/BRW/Input/rasters")
# setwd(tardir)
# 
# flist = c(
#   "bullrun_basin.tif",
#   "subbasins.tif",
#   "patches.tif",
#   "patches.tif",
#   "stratum.tif"
# )
# 
# tlist = c(
#   "basinID",
#   "hillslopeID",
#   "zoneID",
#   "patchID",
#   "stratumID"
# )
# 
# for(i in 1:length(flist)){
#   rtmp = raster(flist[i])
#   names(rtmp) = tlist[i]
#   if(i == 1){
#     rover = rtmp
#   } else{
#     rover = stack(rover, rtmp)
#   }
# }
# 
# rover$stratumID[] %>% table() %>% as.data.frame()
# 
# # load all spatial layer rasters and understory
# flist = c("bullrun_basin.tif",
#           "subbasins.tif",
#           "patches.tif",
#           "patches.tif",
#           "understory.tif"
# )
# 
# tlist = c(
#   "basinID",
#   "hillslopeID",
#   "zoneID",
#   "patchID",
#   "stratumID"
# )
# 
# for(i in 1:length(flist)){
#   rtmp = raster(flist[i])
#   names(rtmp) = tlist[i]
#   if(i == 1){
#     runder = rtmp
#   } else{
#     runder = stack(runder, rtmp)
#   }
# }
# 
# runder$stratumID[] %>% table() %>% as.data.frame()
# 
# # Convert both to dataframe and merge
# over = as.data.frame(rover, xy=TRUE) %>% dplyr::filter(!is.na(basinID))
# under = as.data.frame(runder, xy=TRUE) %>% dplyr::filter(!is.na(basinID))
# rhier = bind_rows(over,under)
# rhier_full = rhier %>% dplyr::arrange(., basinID, hillslopeID, zoneID, patchID, stratumID)
# 
# 
# #%% Compare calibration zone with full model
# rhier_cal %>% dim()
# rhier_full %>% dim()
# 
# # use only hillslopes found in rhier_cal to mask
# ths = rhier_cal$hillslopeID %>% unique()
# 
# htbl_cal = rhier_cal$hillslopeID %>% table() %>% as.data.frame()
# htbl_full = rhier_full %>% dplyr::filter(hillslopeID %in% ths) %>% dplyr::pull(hillslopeID) %>% table() %>% as.data.frame()
# 
# htbl_cal %>% dim()
# htbl_full %>% dim()
# 
# htbl = cbind(htbl_cal,htbl_full[,-1])
# names(htbl) = c("hillslopeID", "cal", "full")
# htbl[htbl$cal != htbl$full,] # only hillslope that is different
# 
# # check that hillslope
# tardir = normalizePath("C:/Users/PETBUser/OneDrive - Washington State University (email.wsu.edu)/Research/BRW_project/Modeling/RHESSys/5_calibration/1_mask_basin/3_gen_wrld_and_flow/1_build_world/input/rasters")
# setwd(tardir)
# hs_284_cal = raster("subbasins.tif")
# hs_284_cal[hs_284_cal[] != 284] = NA
# hs_284_cal[hs_284_cal[] == 284] = 1
# 
# tardir = normalizePath("C:/Users/PETBUser/OneDrive - Washington State University (email.wsu.edu)/Research/BRW_project/Modeling/Create/BRW/Input/rasters")
# setwd(tardir)
# hs_284_full = raster("subbasins.tif")
# hs_284_full[hs_284_full[] != 284] = NA
# hs_284_full[hs_284_full[] == 284] = 1
# 
# #extent(hs_284_full) = extent(hs_284_cal)
# hs_284_full = crop(hs_284_full, hs_284_cal)
# 
# hs_284 = stack(hs_284_cal, hs_284_full)
# names(hs_284) = c("hillslopeID_cal", "hillslopeID_full")
# 
# plot(hs_284$hillslopeID_full)
# plot(hs_284$hillslopeID_cal)
# 
# rhs_284 = hs_284 %>% as.data.frame(.,xy=TRUE) %>%
#   pivot_longer(hillslopeID_cal:hillslopeID_full,names_to="model", values_to="hillslopeID")
# rhs_284$model[is.na(rhs_284$hillslopeID)] = NA
# rhs_284 = rhs_284 %>% dplyr::filter(!is.na(model))
# 
# ggplot(rhs_284) +
#   geom_raster(mapping=aes(x=x,y=y,fill=model)) +
#   facet_wrap(~model, ncol=2)
#   
# # check that area
# tardir = normalizePath("C:/Users/PETBUser/OneDrive - Washington State University (email.wsu.edu)/Research/BRW_project/Modeling/RHESSys/5_calibration/1_mask_basin/3_gen_wrld_and_flow/1_build_world/input/rasters")
# setwd(tardir)
# sb_cal = raster("subbasins.tif")
# sb_cal[!(sb_cal[] %in% ths)] = NA
# sb_cal[sb_cal[] %in% ths] = 1
# 
# tardir = normalizePath("C:/Users/PETBUser/OneDrive - Washington State University (email.wsu.edu)/Research/BRW_project/Modeling/Create/BRW/Input/rasters")
# setwd(tardir)
# sb_full = raster("subbasins.tif")
# sb_full[!(sb_full[] %in% ths)] = NA
# sb_full[sb_full[] %in% ths] = 1
# 
# #extent(sb_full) = extent(sb_cal)
# sb_full = crop(sb_full, sb_cal)
# 
# sb = stack(sb_cal, sb_full)
# names(sb) = c("hillslopeID_cal", "hillslopeID_full")
# 
# plot(sb$hillslopeID_full)
# plot(sb$hillslopeID_cal)
# 
# rsb = sb %>% as.data.frame(.,xy=TRUE) %>%
#   pivot_longer(hillslopeID_cal:hillslopeID_full,names_to="model", values_to="hillslopeID")
# rsb$model[is.na(rsb$hillslopeID)] = NA
# rsb = rsb %>% dplyr::filter(!is.na(model))
# 
# ggplot(rsb) +
#   theme_bw() +
#   theme(legend.position = "bottom") +
#   geom_raster(mapping=aes(x=x,y=y,fill=model,alpha="entire")) +
#   facet_wrap(~model, ncol=2) +
#   geom_raster(data=rhs_284,mapping=aes(x=x,y=y,fill=model,alpha="hs_284")) +
#   scale_alpha_manual(values=c(0.25,1.0)) +
#   labs(fill="Model", alpha="Area")
