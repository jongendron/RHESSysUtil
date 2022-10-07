# Check best vegetation parameter test simulations
# 1. compare with targets for target range
# 2. check long-term stability
library(tidyverse)

tar = read.table("./tar_table2.txt",header=T,as.is=T) %>% as_tibble() %>% dplyr::select(-Param,-stddev) %>%
  rename(target = value) #targets
tar.syr = 2054
tar.eyr = 2104
#tar.syr:tar.eyr %>% length()

# Load model output for grow_stratum.yearly

flist = c(
  "./testing/overstory_cal_grow_stratum.yearly",
  "./testing/overstory_lowmort_grow_stratum.yearly",
  "./testing/overstory_medmort_grow_stratum.yearly"
)

tlist = c("cal","low-mort","med-mort")

tar.list = list()
dat.list = list()

for(i in 1:length(flist)){
  print(i)
  #dat0 = read.table("./testing/test_overstory_cal_grow_stratum.yearly",header=T,as.is=T) %>% 
  #dat0 = read.table("./testing/overstory_medmort_grow_stratum.yearly",header=T,as.is=T) %>% 
  dat0 = read.table(flist[i],header=T,as.is=T) %>%
    as_tibble() 
  
  dat = dat0 %>%
    mutate(
      NPP = psn_net,
      GPP = NPP + mr + gr,
      NPP.GPP = NPP/GPP
    ) %>%
    dplyr::select(-psn_net,-mr,-gr)
  
  #dat0$stratumID %>% unique()
  dat.tar = dat %>% dplyr::filter(year %in% tar.syr:tar.eyr, patchID == "79708") %>%
    dplyr::select(AGBc,height,LAI,NPP,NPP.GPP) %>%
    summarise_all(mean,na.rm=T) %>%
    pivot_longer(AGBc:NPP.GPP,names_to = "Variable",values_to = "model") %>%
    left_join(.,tar)
  
  dat.list[[i]] = dat %>% mutate(tag = tlist[i])
  tar.list[[i]] = dat.tar %>% mutate(tag = tlist[i])
  
}

dat2 = bind_rows(dat.list)
tar2 = bind_rows(tar.list)

# Plot the vars
vlist = c("AGBc","height","LAI","NPP","GPP","NPP.GPP")
#vlist = c("AGBc","height","LAI","NPP","stemc","rootdepth_mm")
n = length(vlist)
colz = randomcoloR::randomColor(count = n)

plot.list = list()
for(i in 1:n){
  #plot.list[[i]] = ggplot(dat,mapping=aes(x=year),color = colz[i]) +
  plot.list[[i]] = ggplot(dat2,mapping=aes(x=year,color = tag)) +
    theme(legend.position = "none") +
    ggtitle(vlist[i]) +
    geom_line(mapping = aes_string(y = vlist[i]))
}

do.call("grid.arrange",args = c(plot.list))

