# Check wbal

library(tidyverse)

# Compare files directly
flist = list.files('./',pattern="patch.yearly")
flist = flist[-grep('grow',flist)]
taglist = flist %>% stringr::str_split(.,pattern="_") %>% lapply(.,function(v1){v1[4]}) %>% unlist()
n = length(flist)

flx = c("psn","denitrif","uptake","leach")
snk = c("soilc", "soiln", "plantc", "plantn", "lai", "litrc")
keep = c("year",flx,snk)

datlist = list()
flxlist = list()
snklist = list()

for(i in 1:n){
  datlist[[i]] = read.table(flist[i],header=T,as.is=T) %>% as_tibble() %>%
    dplyr::select(all_of(keep))
  
  datlist[[i]]$syr = 1:nrow(datlist[[i]])
  datlist[[i]]$tag = taglist[i]
  datlist[[i]] = datlist[[i]] %>% dplyr::select(tag,syr,all_of(keep))
  datlist[[i]] = datlist[[i]] %>% pivot_longer(cols = keep[-(1:2)])
  
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
ggplot(dat_snk, aes(x=syr,y=value,color=tag)) + geom_line() + facet_wrap(name~.,nrow=3,scale="free_y")

# Plotting barplot of total (sum)
dat_flx_sum = dat_flx %>% group_by(tag,name) %>% summarise(value = sum(value,na.rm = T))
dat_snk_sum = dat_snk %>% group_by(tag,name) %>% summarise(value = sum(value,na.rm = T))

ggplot(dat_flx_sum, aes(x=name,y=value,fill=tag)) + geom_bar(stat="identity", position = "dodge")
ggplot(dat_snk_sum, aes(x=name,y=value,fill=tag)) + geom_bar(stat="identity", position = "dodge")

