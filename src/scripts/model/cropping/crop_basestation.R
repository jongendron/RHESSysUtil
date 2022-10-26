###########################################################
### Mask the netCDF base station file for subbasin area ###
###########################################################
library(tidyverse)
library(raster)
home.dir = getwd()
#data.dir = normalizePath("../Util/Model+cropping/Data")
data.dir = normalizePath(".")

###########################################
## Determine which base stations to keep ##
###########################################
setwd(data.dir)
#subb.r = "./test_basin.tif"       # raster of target basin
subb.r = "./TC_sbl1_patches.tif"       # raster of target basin
bs.r = "./brw/basestationsID.tif" # parent basestation file

subb.r = raster(subb.r)
bs.r = raster(bs.r)
bs.r = mask(bs.r,subb.r)
bs.tar = bs.r[] %>% unique() %>% .[!is.na(.)]

#######################################################
## indentify lines associated with each base station ##
#######################################################
bs = "./brw/br.bs" # path to parent base station file

bs = read.table(bs,header = F, as.is = T, fill = T) %>%
  as_tibble() %>%
  mutate(idx = 1:nrow(.))
nr = nrow(bs)

sts = bs %>% dplyr::filter(V2 == "base_station_id") %>%
  mutate(
    start = idx,
    end = c((idx[-1] - 1),nr) # after hdr bs's repeat -> last bs ends at last line
  )

bs$bs_ID = NA
n = nrow(sts)
pb = txtProgressBar(min = 0, max = n,style = 3, width = 100, char = '*')

for(i in 1:n){
  bs$bs_ID[sts$start[i]:sts$end[i]] = sts$V1[i]
  Sys.sleep(0.0000000000000001)
  setTxtProgressBar(pb,i)
}

close(pb)
#print(bs, n = 50)

bs_bk = bs

###########################################
## Remove rows of unwanted base stations ##
###########################################
bs = bs %>%
  dplyr::filter(
    bs_ID %in% c(NA,bs.tar))

############################################
## Update base station (grid_cells) count ##
############################################
num_grid = bs %>%
  dplyr::filter(V2 == "base_station_id") %>%
  summarise(n = n()) %>%
  pull(.,1)
#bs.tar %>% length() == num_grid

bs$V1[1] = num_grid # replaces grid_cells with correct num base stations in file

bs_bk2 = bs

####################
## write the file ##
####################
file.name = "./test_basin.bs"

bs2 = bs[,1:2]

bs3 = Map(
  function(v1,v2){
    paste(
      sprintf("%-50s %-50s",v1,v2)
    )
  },bs2$V1,bs2$V2
) %>% 
  unname() %>%
  unlist()
#nrow(bs2) == length(bs3)

write.table(bs3,file.name, quote = F, sep = "",row.names = F, col.names = F)

setwd(home.dir)
