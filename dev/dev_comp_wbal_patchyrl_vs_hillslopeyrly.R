# Check wbal

library(tidyverse)

# Compare files directly
file1 = './init_cold_ndep0.01_gw0.01_hillslope.yearly'
file2 = './init_cold_ndep0.01_gw0.01_patch.yearly'

df1 = read.table(file1,header=T,as.is=T) %>% as_tibble() %>%
  dplyr::select(year,pch_pcp:hill_gw_storage)
colnames(df1) = c("year", "precip", "et", "streamflow", "return_flow", "base_flow", "hill_base_flow",
                  "gw_drainage", "rz_storage", "unsat_storage", "gw_storage")
df1$syr = 1:nrow(df1)
df1$tag='hillslope'
df1 = df1 %>% pivot_longer(cols = precip:gw_storage)

df2 = read.table(file2,header=T,as.is=T) %>% as_tibble() %>%
  dplyr::select(year,precip, et, streamflow:unsat_storage,gw_drainage,overland_flow)
df2$syr = 1:nrow(df2)
df2$tag='patch'
df2 = df2 %>% pivot_longer(cols = precip:overland_flow)

df3 = bind_rows(df1,df2)

# Merging 

flx = c("precip", "et", "streamflow", "return_flow", "base_flow", "overland_flow", "hill_base_flow", "gw_drainage")
snk = c("rz_storage", "unsat_storage", "gw_storage")

df3_flx = df3 %>% dplyr::select(tag, syr, name, value) %>%
  dplyr::filter(name %in% flx)
df3_flx$name = df3_flx$name %>% factor(.,levels=flx)

df3_snk = df3 %>% dplyr::select(tag, syr, name, value) %>%
  dplyr::filter(name %in% snk)
df3_snk$name = df3_snk$name %>% factor(.,levels=snk)

# Plotting time series
# Identical
ggplot(df3_flx, aes(x=syr,y=value,color=tag)) + geom_line() + facet_wrap(name~.)
ggplot(df3_snk, aes(x=syr,y=value,color=tag)) + geom_line() + facet_wrap(name~.,nrow=3)

# Plotting barplot of total (sum)
df3_flx_sum = df3_flx %>% group_by(tag,name) %>% summarise(value = sum(value,na.rm = T))
df3_snk_sum = df3_snk %>% group_by(tag,name) %>% summarise(value = sum(value,na.rm = T))

ggplot(df3_flx_sum, aes(x=name,y=value,fill=tag)) + geom_bar(stat="identity", position = "dodge")
ggplot(df3_snk_sum, aes(x=name,y=value,fill=tag)) + geom_bar(stat="identity", position = "dodge")

