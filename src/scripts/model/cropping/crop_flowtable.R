######################################################################
### Crops the flowfile to only use target hillslopes in South Fork ###
######################################################################
library(tidyverse);
home.dir = getwd()
#data.dir = normalizePath("../Util/Model+cropping/Data")
data.dir = normalizePath(".")

###########################################
## Obtain list of hillslopes and patches ##
###########################################
setwd(data.dir)
wfile = "./cal_brw_init.state"
wfile = read.table(wfile,header=F,as.is=T) %>%
  as_tibble()
wfile$idx = 1:nrow(wfile)

stbl0 = wfile %>%
  dplyr::filter(V2 %in% c("hillslope_ID","patch_ID"))

stbl = stbl0 %>%
  group_by(V2) %>%
  nest()
#stbl$data[[1]] # hillslopes
#stbl$data[[2]] # patches

########################
## Print row function ##
########################
print.row = function(...,tab = T){
  l = as.list(...)
  tmp = paste(rep("%-10s",times = length(l)),collapse = "") #%-Xs is left aligned string with X characters
  
  if(tab == T){
    cat("\n\t")
  } else {
      cat("\n")
    }
  
  cat(
    do.call(sprintf, c(tmp,as.list(l)))
    )
  #return(l)
}

hdr0 = c("idx","n","lvl","bas.p","hs.p","pch.p")

#############################################################
## Add id's for basins, hillslopes, patches, and neighbors ##
#############################################################
ffile0 = "./brw_init.flow"

ffile0 = readLines(ffile0)
flist = ffile0 %>%
  lapply(.,function(v1){
    v2 = v1 %>% stringr::str_split(.,pattern = "\\s")
    v2 = v2[[1]]
  })

ftbl00 = tibble(
  ln = flist,
  n = lapply(flist,length) %>% unlist()
)

lktbl = tibble(
  n = c(1,2,5,11),
  lvl = c(1,2,4,3) # basin > hillslope > neighbor < patch
)

ftbl0 = left_join(ftbl00,lktbl)
ftbl0$idx = 1:nrow(ftbl0)

##################################
## Parent # Hillslopes in Basin ##
##################################
ftbl0$bas.p = ftbl0$ln[[1]]

#########################
## Parent Hillslope ID ##
#########################
hs = ftbl0 %>%
  dplyr::filter(lvl == 2)

hs$st = hs$idx
hs$end = c(hs$idx[-1] - 1,nrow(ftbl0))

hs$hs.p = hs$ln %>%
  lapply(.,function(v1){v1[1]}) %>%
  unlist()

ftbl = ftbl0
ftbl$hs.p = NA

for(i in 1:nrow(hs)){
  ftbl$hs.p[hs$st[i]:hs$end[i]] = hs$hs.p[i]
}

#####################
## Parent Patch ID ##
#####################

pch = ftbl %>%
  dplyr::filter(lvl == 3)

pch$pch.p = pch$ln %>%
  lapply(.,function(v1){v1[1]}) %>%
  unlist()

ftbl_bk = ftbl
#ftbl = ftbl_bk

ftbl$pch.p = NA
n = nrow(pch)   # nrow in pch file
nr = nrow(ftbl) # nrow in parent file
pb = txtProgressBar(min = 0, max = n,style = 3, width = 100, char = '*')

for(i in 1:n){
  
  idx0 = pch$idx[i]               # idx0
  ftbl$pch.p[idx0] = pch$pch.p[i] # parent patch
  #print.row(hdr0,tab = F)
  
  if((idx0 + 1) > nr){break}      # break loop if idx + 1 is out of bounds
  
  idx = idx0 + 1                  # idx = idx0
  sw = TRUE                       # initializes switch
      
  while(sw == TRUE){
    
    if(ftbl$lvl[idx0] < ftbl$lvl[idx]){
      ftbl$pch.p[idx] = pch$pch.p[i]
      #dtmp = as.matrix(ftbl[idx,c("idx","n","lvl","bas.p","hs.p","pch.p")])[1,] %>% unname()
      #print.row(dtmp,tab = F)
    } else {
      sw = FALSE
    }
    
    idx = idx + 1
    
    if(idx > nr){
      sw = FALSE
    }
    
  }
  
  Sys.sleep(0.0000000000000001)
  setTxtProgressBar(pb,i)
  
}

close(pb) # left off

ftbl_bk = ftbl
#ftbl = ftbl_bk

#######################
## Neighbor Patch ID ##
#######################
nb = ftbl %>%
  dplyr::filter(lvl == 4)

nb$nb = nb$ln %>%
  lapply(.,function(v1){v1[2]}) %>% # 2 because [1] is currently space (empty char)
  unlist()

nb = nb[,-1]

ftbl = left_join(ftbl,nb)
ftbl_bk2 = ftbl
#ftbl = ftbl_bk

#write.table(ftbl_bk2[,-1], file = "./Data/BRW/basin_hier_tbl.txt",quote = F, col.names = T, row.names = F)

###############################################
## Filter out target hillslopes and patches  ##
###############################################
ftbl = ftbl %>%
  dplyr::filter(
    hs.p %in% c(NA,stbl$data[[1]]$V1), # parent hillslopes
    pch.p %in% c(NA,stbl$data[[2]]$V1), # parent patches
    nb %in% c(NA,stbl$data[[2]]$V1)
  ) %>%
  arrange(idx)

#length(ftbl$pch.p[!is.na(ftbl$pch.p)] %>% unique()) == length(stbl$data[[2]]$V1 %>% unique()) # same # patches
#length(ftbl$hs.p[!is.na(ftbl$hs.p)] %>% unique()) == length(stbl$data[[1]]$V1 %>% unique()) # same # hs
#length(ftbl$nb[!is.na(ftbl$nb)] %>% unique()) == length(stbl$data[[2]]$V1 %>% unique()) # same # neighbors

###########################################################
## Calculate number of elements for each hierarchy layer ##
###########################################################
hs.n = ftbl %>% 
  dplyr::filter(lvl %in% c(1,2)) %>%
  group_by(bas.p) %>%
  summarise(size = (n() - 1)) %>%
  mutate(lvl = 1)# -1 b/c don't include basin

pch.n = ftbl %>% 
  dplyr::filter(lvl %in% c(2,3)) %>%
  group_by(bas.p,hs.p) %>%
  summarise(size = (n() - 1)) %>% # -1 b/c don't include hillslope in patch count
  mutate(lvl = 2)

nb.n = ftbl %>% 
  dplyr::filter(lvl %in% c(3,4)) %>%
  group_by(bas.p,hs.p,pch.p) %>%
  summarise(size = (n() - 1)) %>% # -1 b/c don't include parent patch in neighbor count
  mutate(lvl = 3)

all.n = bind_rows(hs.n,pch.n) %>% bind_rows(.,nb.n)

ftbl_bk3 = ftbl
ftbl = left_join(ftbl,all.n)

cnt.tbl = tibble(
  lvl = 1:4,
  cnt.idx = c(1,2,11,NA)
)

ftbl = left_join(ftbl,cnt.tbl)

################################
## Change object layer counts ##
################################
ftbl_bk4 = ftbl

ftbl$ln[ftbl$lvl == 4] = ftbl$ln[ftbl$lvl == 4] %>%
  lapply(.,function(v1){v1[-1]}) # removes the extra space

ftbl$ln = Map(function(v1,v2,v3){
  w1 = v1
  w1[v2] = v3
  return(w1)
},ftbl$ln, ftbl$cnt.idx, ftbl$size
)


####################
## Write the file ##
####################
options(scipen = 999)
file.name = "./cal_brw_init.flow"

ffile = ftbl %>%
  arrange(idx) %>%
  dplyr::select(ln,lvl)

ffile = Map(
  function(v1,v2){
    txt = paste(v1, collapse = " ")
    if(v2 == 4){
      txt = paste("\t",txt,sep="")
    }
    return(txt)
  },ftbl$ln, ftbl$lvl
) %>%
  unlist()

fileConn = file(file.name)
writeLines(ffile, fileConn)
close(fileConn)

readLines("./cal_brw_init.flow")
setwd(home.dir)
