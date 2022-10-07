# Check wbal

library(tidyverse)

# Compare files directly
flist = list.files('./',pattern="hillslope.yearly")
flist = flist[-grep('grow',flist)]
taglist = flist %>% stringr::str_split(.,pattern="_") %>% lapply(.,function(v1){v1[4]}) %>% unlist()
n = length(flist)

flx = c("precip", "et", "streamflow", "return_flow", "base_flow", "overland_flow", "hill_base_flow", "gw_drainage")
snk = c("rz_storage", "unsat_storage", "gw_storage")

datlist = list()
flxlist = list()
snklist = list()

for(i in 1:n){
  datlist[[i]] = read.table(flist[i],header=T,as.is=T) %>% as_tibble() %>%
    dplyr::select(year,pch_pcp:hill_gw_storage)
  
  colnames(datlist[[i]]) = c("year", "precip", "et", "streamflow", "return_flow", "base_flow", "hill_base_flow",
                             "gw_drainage", "rz_storage", "unsat_storage", "gw_storage")
  datlist[[i]]$syr = 1:nrow(datlist[[i]])
  datlist[[i]]$tag = taglist[i]
  datlist[[i]] = datlist[[i]] %>% pivot_longer(cols = precip:gw_storage)
  
  flxlist[[i]] = datlist[[i]] %>% dplyr::select(tag, syr, name, value) %>%
    dplyr::filter(name %in% flx)
  
  flxlist[[i]]$name = flxlist[[i]]$name %>% factor(.,levels=flx)
  
  snklist[[i]] = datlist[[i]] %>% dplyr::select(tag, syr, name, value) %>%
    dplyr::filter(name %in% snk)
  snklist[[i]]$name = snklist[[i]]$name %>% factor(.,levels=snk)
  
}

dat_flx = bind_rows(flxlist)
dat_snk = bind_rows(snklist)

# Plotting time series
# Identical
ggplot(dat_flx, aes(x=syr,y=value,color=tag)) + geom_line() + facet_wrap(name~.)
ggplot(dat_snk, aes(x=syr,y=value,color=tag)) + geom_line() + facet_wrap(name~.,nrow=3)

# Plotting barplot of total (sum)
dat_flx_sum = dat_flx %>% group_by(tag,name) %>% summarise(value = sum(value,na.rm = T))
dat_snk_sum = dat_snk %>% group_by(tag,name) %>% summarise(value = sum(value,na.rm = T))

ggplot(dat_flx_sum, aes(x=name,y=value,fill=tag)) + geom_bar(stat="identity", position = "dodge")
ggplot(dat_snk_sum, aes(x=name,y=value,fill=tag)) + geom_bar(stat="identity", position = "dodge")

