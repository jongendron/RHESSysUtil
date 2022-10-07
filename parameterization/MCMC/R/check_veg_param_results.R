# Check vegetation parameterization results 
# Using the Metrpolis-Hasting MCMC calibration approach
# Jonathan Gendron 07/25/2022
library(tidyverse)

# Defined Variables
var0 = "height"
plist = paste("cal",0:10,sep="")
plabs = c(
  "alloc_frootc_leafc","alloc_crootc_stemc","alloc_stemc_leafc","alloc_livewoodc_woodc",
  "alloc_prop_day_growth","height_to_stem_exp","height_to_stem_coef",
  "dickenson_pa","per_N","proj_sla","max_daily_mort")
names(plabs) = plist
colz = randomcoloR::randomColor(count = length(plist))

# Load the data
param_name = "veg_param2"
tar0 = read.table("../tar_table2.txt",header = T, as.is = T) %>% as_tibble()
#val0 = read.table(paste("./",param_name,"/",param_name,"_mcmc_avg_tbl.txt",sep=""),header = T, as.is = T) %>%
val0 = read.table(paste("./",param_name,"/","mcmc_avg_tbl.txt",sep=""),header = T, as.is = T) %>%
  as_tibble() %>%
  dplyr::select(-idx.1)

# Get summary stats
val0 %>% summary()

# Plot Histogram of Model Variable Values (w/ targets)
hist.val = val0 %>% dplyr::select(idx,AGBc:NPP.GPP) %>%
   pivot_longer(cols = AGBc:NPP.GPP, names_to = "Variable", values_to = "value")

p1 = ggplot(hist.val) +
  geom_histogram(mapping = aes(x=value,fill = Variable)) +
  facet_wrap(~Variable, scales = "free") 
p1
p1 + geom_vline(tar0,mapping=aes(xintercept=value,color = Variable))

# Plot histogram of Model Parameter values
hist.param = val0 %>% dplyr::select(idx,cal0:cal10) %>%
  pivot_longer(cols = cal0:cal10, names_to = "Parameter", values_to = "value")
hist.param$Parameter = hist.param$Parameter %>% factor(.,levels = paste("cal",0:10,sep=""))

p2 = ggplot(hist.param) +
  geom_histogram(mapping = aes(x=value,fill = Parameter)) +
  facet_wrap(~Parameter, scales = "free",labeller = labeller(Parameter = plabs)) #+
  #theme(legend.position = "none")
p2
# Find optimizatio between highest total likelyhood and reasonable individual parameter values
# Identify where it falls in the distribution of parameters
# This process is manual (need to check manually by changing the range of rows in the next line)
val2 = val0 %>% dplyr::arrange(desc(likelyhood))
val2$likeid = 1:nrow(val2)

# rng = 1:30
# 
# #hi = val0 %>% dplyr::arrange(desc(likelyhood)) %>% .[rng,] # 
# 
# hi = val2 %>% dplyr::filter(
# NPP.GPP > 0.495 & NPP.GPP < 0.505,
# height > 31 & height < 33) %>%
#   dplyr::arrange(LAI)
# 
# hi2 = hi %>% dplyr::arrange(likeid)
# print(hi2,width = 1000,length = 30)
#    
# hist.hi = hi %>% dplyr::select(idx,AGBc:NPP.GPP) %>%
#   pivot_longer(cols = AGBc:NPP.GPP, names_to = "Variable", values_to = "value")
# 
# p3 = ggplot(hist.hi) +
#   geom_histogram(mapping = aes(x=value,fill = Variable)) +
#   facet_wrap(~Variable, scales = "free") 
# p3 + geom_vline(tar0,mapping=aes(xintercept=value,color = Variable))
# 
# 
# hi2 = hi %>% dplyr::filter(NPP.GPP > 0.52 & NPP.GPP < 0.54, height > 30, LAI < 4.1, AGBc < 23 & AGBc > 21)
# hi2 = hi %>% dplyr::filter(NPP.GPP < 0.58, height > 30 & height < 39, LAI < 4.1, AGBc < 23 & AGBc > 21)
# print(hi2,width = 1000)
# hi3 = hi2[1,] %>% pivot_longer(cal0:cal10,names_to = "Parameter") %>% dplyr::select(Parameter,value,AGBc:NPP.GPP)

print(val2 %>% arrange(LAI) %>% dplyr::select(idx,LAI,likeid),width = 1000,n = 50)

#best.val = val2[val2$idx == 109,] %>%
best = val2[val2$likeid == 3,]
best.val = best %>%
  pivot_longer(AGBc:NPP.GPP,names_to = "Variable") %>% dplyr::select(Variable,value)

p1 + geom_vline(tar0,mapping=aes(xintercept=value),color = "black") +
  geom_vline(best.val,mapping=aes(xintercept=value),color = "red")

#best.param = val2[val2$idx == 109,] %>%
best.param = best %>%
pivot_longer(cal0:cal10,names_to = "Parameter") %>% dplyr::select(Parameter,value)
p2 + geom_vline(data = best.param, mapping = aes(xintercept = value),color = "red")

print(best,width = 200)

# Look at correlations for each 

veg_cor = function(MC_table,Variable = var0,Plist = plist,Plabs = plabs,Colz = colz){
  n = length(plist)
  plot.list = list()
  for(i in 1:n){
    v0 = Variable
    p0 = Plist[i]
    lab0 = Plabs[i]
    col0 = Colz[i]
    dtmp = MC_table %>% dplyr::select(all_of(c(v0,p0)))
    plot.list[[i]] = ggplot(dtmp,mapping = aes_string(x=p0,y=v0)) + 
      geom_point() + geom_smooth(method = "lm",color = col0) +
      labs(x=lab0)
  }
  library(gridExtra)
  do.call("grid.arrange",c(plot.list))
  return(0)
}

veg_cor(val0,"height")
veg_cor(val0,"NPP.GPP")
veg_cor(val0,"AGBc")
veg_cor(val0,"LAI")
veg_cor(val0,"NPP")

## Min suggests taking average or median parameter value of the top 5% likelyhood
# Then doing a test run to check the bias against observed
n = 0.5*nrow(val2)
best = val2 %>% arrange(likeid) %>% .[1:n,]
avg = best %>% dplyr::select(cal0:cal10) %>% summarise_all(mean,na.rm = T) %>%
  pivot_longer(cal0:cal10,names_to = "Parameter") %>% mutate(stat = "mean")
med = best %>% dplyr::select(cal0:cal10) %>% summarise_all(median,na.rm = T) %>%
  pivot_longer(cal0:cal10,names_to = "Parameter") %>% mutate(stat = "median")

best2 = bind_rows(avg,med)

ggplot(best2) + 
  geom_bar(stat = "identity", mapping = aes(x=Parameter,y=value,fill=stat),position = "dodge")

p2 + geom_vline(data = best2, mapping=aes(xintercept = value, color = stat))

avg

############################################################################

# # Find parameter set where variable values are near their most likely range
# val = val0 # skips initial variable set
# tot = tot0[-1,] # remove first row because ^^^
# dat = cbind(tot,val) %>% as.data.frame() %>% as_tibble()
# 
# rngs = list(
#   c(31.25,43.75), # AGBc
#   c(25.00,37.5),  # height
#   c(10.5,11.5),   # LAI
#   c(1.55,1.575),  # NPP
#   c(.4875,.50)    # NPP.GPP
# )
# 
# dat2 = dat %>%
#   dplyr::filter(
#     AGBc > rngs[[1]][1] & AGBc < rngs[[1]][2] &
#       height > rngs[[2]][1] & height < rngs[[2]][2] &
#       LAI > rngs[[3]][1] & LAI < rngs[[3]][2] &
#       NPP > rngs[[4]][1] & NPP < rngs[[4]][2] &
#       NPP.GPP > rngs[[5]][1] & NPP.GPP < rngs[[5]][2]
#   )
# 
# dat2.hist = dat2 %>% dplyr::select(cal0:cal10) %>%
#   pivot_longer(cal0:cal10,names_to = "Parameter",values_to = "value")
# 
# dat2.hist$Parameter = factor(dat2.hist$Parameter,levels = paste("cal",0:10,sep=""))
# 
# 
# ggplot(dat2.hist) +
#   geom_histogram(mapping=aes(x=value,fill = Parameter)) +
#   facet_wrap(~Parameter,scales = "free")
# 
# dat3 = dat2 %>% dplyr::filter(
#   cal2 < 0.7,
#   cal3 < 0.09,
#   cal4 > 0.25 & cal4 < 0.3,
#   cal5 > 11 & cal5 < 12,
#   cal6 > 0.155 & cal6 < 0.165,
#   cal8 > 7.0 & cal8 < 7.5
# )
# 
# View(dat3)

