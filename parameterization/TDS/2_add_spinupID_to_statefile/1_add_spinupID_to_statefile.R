# Add 1.00 spinup_object_ID to statefile under each occurence of cover_fraction
# for each stratum layer
library(tidyverse)

state0 = "./TC_hs410_evergreen.state"
state0 = read.table(state0,header = F, as.is = T) %>%
  as_tibble()
state0$idx = 1:nrow(state0)

#cover_fraction_idx = state0$idx[state0$V2 == "cover_fraction"]
#state0 = state0[1:500,]

idx = state0$idx[state0$V2 == "cover_fraction"]
#n = length(cover_fraction_idx)
n = length(idx)

state = state0 %>% dplyr::select(-idx) %>% as.matrix()
new_line = matrix(data = c("1.00","spinup_object_ID"),nrow = 1)

for(i in n:1){
  print(i)
  id0 = idx[i]
  chunk = state[(1:id0),]
  if((id0 + 1) < nrow(state)){
    end = state[(id0 + 1):nrow(state),]
    state = rbind(chunk,new_line,end)
  } else{
    state = rbind(chunk,new_line)
  }
}

#View(state)
state2 = as.data.frame(state)
state2 = Map(
  function(v1,v2){
    paste(
      sprintf("%-25s %-25s",v1,v2)
    )
  },state2$V1,state2$V2) %>%
  unlist()
names(state2) = NULL

writeLines(state2,"./TC_hs410_evergreen_spinupID.state",sep="\n")



