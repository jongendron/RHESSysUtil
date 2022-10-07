# Check best vegetation parameter test simulations
# 1. compare with targets for target range
# 2. check long-term stability
library(tidyverse)
STRATID = 79708 # stratum layer and number to plot

#flist = grep("*grow_stratum.yearly",list.files("./"),value = T)
# flist = c("./testing1_def_rr/soilinit2_nd0p0010_grow_stratum.yearly",
#           "./testing2_cal_rr/soilinit2_nd0p0010_grow_stratum.yearly",
#           "./testing3_def_nrr/soilinit2_nd0p0010_grow_stratum.yearly",
#           "./testing4_cal_nrr/soilinit2_nd0p0010_grow_stratum.yearly"
# )
#flist = c("./testing_static_growth/soilinit_nd0p0010_patch.yearly")
flist = c("./testing_static_growth/soilinit_nd0p0010_grow_stratum.yearly")

dat.list = list()

for(i in 1:length(flist)){
  print(i)
  file0 = flist[i]
  dat0 = read.table(file0,header=T,as.is=T) %>%
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
  
  dat.list[[i]] = dat %>% 
    #mutate(tag = file0 %>% str_split(.,pattern = "_grow_") %>% .[[1]] %>% .[1])
    mutate(tag = i)
  
}

dat2 = bind_rows(dat.list)

#ttmp = "soilinit_nd0p0075"
#dat2$syr[dat2$tag != ttmp] = dat2$syr[dat2$tag != ttmp] + max(dat2$syr[dat2$tag == ttmp])
#dat2$tag = factor(dat2$tag,
#                  levels = c("soilinit_nd0p0075","veginit_nd0p0075","veginit_nd0p0050",
#                             "veginit_nd0p0025","veginit_nd0p0010"))
#dat2$tag = "veginit2_nd0p001"

# Plot the vars
vlist = c("AGBc","height","LAI","NPP","GPP","NPP.GPP")
n = length(vlist)
colz = randomcoloR::randomColor(count = n)

dat2$tag = factor(dat2$tag)

plot.list = list()
for(i in 1:n){
  #plot.list[[i]] = ggplot(dat,mapping=aes(x=year),color = colz[i]) +
  plot.list[[i]] = ggplot(dat2,mapping=aes(x=syr,color = tag)) +
    theme(legend.position = "bottom") +
    #theme(legend.position = "none") +
    #ggtitle(vlist[i]) +
    geom_line(mapping = aes_string(y = vlist[i])) +
    scale_x_continuous(n.breaks = 8) +
    scale_color_discrete(labels = c("def_rr","cal_rr","def_nrr","cal_nrr"))
}

library(gridExtra)
do.call("grid.arrange",args = c(plot.list))
#dat.list = list()
#dat.list = append(dat.list,list(dat2))

### Linear Regression to test downward trend with time

# dtmp = dat2 %>% dplyr::filter(syr >= 100) %>% dplyr::select(syr,all_of(vlist))
# 
# plot.list2 = list()
# for(i in 1:n){
#   #plot.list[[i]] = ggplot(dat,mapping=aes(x=year),color = colz[i]) +
#   plot.list2[[i]] = ggplot(dtmp,mapping=aes_string(x="syr",y=vlist[i])) +
#     theme(legend.position = "none") +
#     ggtitle(vlist[i]) +
#     geom_point() +
#     geom_smooth(method = "lm") +
#     scale_x_continuous(n.breaks = 10)
# }
# 
# library(gridExtra)
# do.call("grid.arrange",args = c(plot.list2))

