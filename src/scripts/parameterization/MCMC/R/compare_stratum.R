library(tidyverse)

dat0 = read.table("./test1_grow_stratum.yearly",header = T, as.is = T) %>%
  as_tibble() %>%
  mutate(stratumID = factor(stratumID,levels = c(79708,179708)))

ggplot(dat0,aes(x=year,y=height,color=stratumID)) + geom_line() + facet_wrap(~stratumID,scales = "free_y")

dat0$stratumID %>% unique()

over0 = read.table("./test_overstory_grow_stratum.yearly",header = T, as.is = T) %>%
  as_tibble() %>%
  mutate(stratumID = factor(stratumID,levels = c(79708,179708)))

under0 = read.table("./test_understory_grow_stratum.yearly",header = T, as.is = T) %>%
  as_tibble() %>%
  mutate(stratumID = factor(stratumID,levels = c(79708,179708)))

ggplot(mapping = aes(x=year,y=AGBc,color = stratumID)) +
  facet_wrap(~stratumID,scales = "free_y") +
  geom_line(data = over0) +
  geom_line(data = under0)


vlist0 = c("AGBc","height","LAI","psn_net")
plist0 = list()
labs0 = c("Evergreen","Underpine")
names(labs0) = c(79708,179708)

for(i in 1:length(vlist0)){
  plist0[[i]] = ggplot(mapping = aes_string(x="year",y=vlist0[i],color = "stratumID")) +
    facet_wrap(~stratumID,scales = "free_y",labeller = labeller(stratumID = labs0)) +
    geom_line(data = over0) +
    geom_line(data = under0)
}

library(gridExtra)
do.call("grid.arrange",c(plist0,ncol = 1))

