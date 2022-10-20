library(tidyverse)

# Load template definition file
temp = read.table("./stratum_evergreen_mode.def",header=F,as.is=T) %>% as_tibble()
temp$idx = 1:nrow(temp)
idx = grep("CAL",temp$V1)

sset = temp[idx,]

# load table containing best parameter set
best = read.table("./veg_param9_avg_top_5pct_likelyhood.txt",header=T,as.is=T) %>% as_tibble()

# Merge
sset2 = left_join(sset,best)
sset3 = sset2 %>% mutate(V1 = as.character(value)) %>% dplyr::select(-value)

# Change in place
temp2 = temp
temp2[idx,] = sset3
temp2$idx = NULL
# Output the definition file
write.table(temp2,file = "./stratum_evergreen_cal.def",quote = F, row.names = F, col.names = F,sep="\t")

