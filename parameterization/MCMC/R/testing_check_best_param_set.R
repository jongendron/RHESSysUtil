# Check best vegetation parameter test simulations
# 1. compare with targets for target range
# 2. check long-term stability
library(tidyverse)
STRATID = 79708 # stratum layer and number to plot

# tar = read.table("./tar_table2.txt",header=T,as.is=T) %>% as_tibble() %>% dplyr::select(-Param,-stddev) %>%
#   rename(target = value) #targets
# tar.syr = 2054
# tar.eyr = 2104
#tar.syr:tar.eyr %>% length()

# Load model output for grow_stratum.yearly

flist = c(
  #"./testing/overstory_test_grow_stratum.yearly"
  "./vegcal3_grow_stratum.yearly"
  #"./soilinit2_grow_stratum.yearly"
)

#dat0 = read.table("./testing/overstory_medmort4_grow_stratum.yearly",as.is = T, header = T) %>% as_tibble()

#tlist = c("cal","low-mort","med-mort")
#tlist = "med-mort4"
tlist = "soilinit3"

#tar.list = list()
dat.list = list()

for(i in 1:length(flist)){
  print(i)
  #dat0 = read.table("./testing/test_overstory_cal_grow_stratum.yearly",header=T,as.is=T) %>% 
  #dat0 = read.table("./testing/overstory_medmort_grow_stratum.yearly",header=T,as.is=T) %>% 
  dat0 = read.table(flist[i],header=T,as.is=T) %>%
    as_tibble() %>%
    dplyr::filter(stratumID == STRATID) %>%
    mutate(
      syr = 1:nrow(.)
    ) 
  #dat = dat0
  
  dat = dat0 %>%
    mutate(
      NPP = psn_net,
      GPP = NPP + mr + gr,
      NPP.GPP = NPP/GPP
    ) %>%
    dplyr::select(-psn_net,-mr,-gr)
  
  #dat0$stratumID %>% unique()
  # dat.tar = dat %>% dplyr::filter(year %in% tar.syr:tar.eyr, patchID == "79708") %>%
  #   dplyr::select(AGBc,height,LAI,NPP,NPP.GPP) %>%
  #   summarise_all(mean,na.rm=T) %>%
  #   pivot_longer(AGBc:NPP.GPP,names_to = "Variable",values_to = "model") %>%
  #  left_join(.,tar)
  
  dat.list[[i]] = dat %>% mutate(tag = tlist[i])
  #tar.list[[i]] = dat.tar %>% mutate(tag = tlist[i])
  
}

dat2 = bind_rows(dat.list)
#tar2 = bind_rows(tar.list)

# Plot the vars
vlist = c("AGBc","height","LAI","NPP","GPP","NPP.GPP")
#vlist = c("AGBc","stemc","leafc","rootc","height","LAI")
n = length(vlist)
colz = randomcoloR::randomColor(count = n)

plot.list = list()
for(i in 1:n){
  #plot.list[[i]] = ggplot(dat,mapping=aes(x=year),color = colz[i]) +
  plot.list[[i]] = ggplot(dat2,mapping=aes(x=syr,color = tag)) +
    theme(legend.position = "none") +
    ggtitle(vlist[i]) +
    geom_line(mapping = aes_string(y = vlist[i])) +
    scale_x_continuous(n.breaks = 10)
}

library(gridExtra)
do.call("grid.arrange",args = c(plot.list))


#dat.list = list()
#dat.list = append(dat.list,list(dat2))

### Linear Regression to test downward trend with time

dtmp = dat2 %>% dplyr::filter(syr >= 100) %>% dplyr::select(syr,all_of(vlist))

plot.list2 = list()
for(i in 1:n){
  #plot.list[[i]] = ggplot(dat,mapping=aes(x=year),color = colz[i]) +
  plot.list2[[i]] = ggplot(dtmp,mapping=aes_string(x="syr",y=vlist[i])) +
    theme(legend.position = "none") +
    ggtitle(vlist[i]) +
    geom_point() +
    geom_smooth(method = "lm") +
    scale_x_continuous(n.breaks = 10)
}

library(gridExtra)
do.call("grid.arrange",args = c(plot.list2))

