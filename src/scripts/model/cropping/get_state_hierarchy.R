#######################################################
### Function to create table of statefile hierarchy ###
#######################################################

# If hierarchy table exists then skip and load it

state_hier = function(Statefile,
                      Hillslope = TRUE,
                      Zone = TRUE,
                      Patch = FALSE,
                      Stratum = FALSE){
  
  bas.state = read.table(Statefile,header = F,as.is = T, fill = T) %>%
    as_tibble()
  
  bas.state$idx = 1:nrow(bas.state)
  
  ids = tibble(
    V2 = c("world_id","basin_ID","hillslope_ID","zone_ID","patch_ID","canopy_strata_ID"),
    lvl = 1:6
  )
  
  bas = left_join(bas.state,ids)
  bas$lvl[is.na(bas$lvl)] = 999
  
  #########################################
  ## Indentify the world_ID and basin_ID ##
  #########################################
  bas$world_ID = 1 # set world ID
  bas$basin_ID = 1 # set basin ID
  
  bas_bk = bas
  
  if(Hillslope == TRUE){
    #################################
    ## Indentify Parent hillslopes ##
    #################################
    hs = bas %>% dplyr::filter(lvl == 3) %>%
      dplyr::select(V1,idx)
    
    hs$start = hs$idx
    hs$end = c((hs$idx[-1] - 1),nrow(bas))
    
    bas$hillslope_ID = NA
    
    n = nrow(hs)
    cat("Gathering hillslope_ID values\n")
    pb = txtProgressBar(min = 0, max = n,style = 3, width = 100, char = '*')
    
    for(i in 1:n){
      bas$hillslope_ID[hs$start[i]:hs$end[i]] = hs$V1[i]
      Sys.sleep(0.0000000000000001)
      setTxtProgressBar(pb,i)
    }
    
    close(pb) # left off
    
    bas_bk2 = bas
  } else {
    
    cat("\nHillslope must be TRUE to get hillslope_ID\n")
    
  }
  
  if(Zone == TRUE & Hillslope == TRUE){
    ###############################
    ## Indentify Parent Zones V2 ##
    ###############################
    
    bas$zone_ID = NA
    
    bas = bas %>% 
      group_by(world_ID,basin_ID,hillslope_ID) %>%
      nest() %>%
      arrange(.,desc(is.na(hillslope_ID)),hillslope_ID)
    
    bas$rid = 1:nrow(bas) # row id for nested data frame
    
    ## filter out rows not at patch level or lower
    rid.hs = bas$rid[
      (!is.na(bas$world_ID) &
         !is.na(bas$basin_ID) &
         !is.na(bas$hillslope_ID)
      )
      ]
    
    n = length(rid.hs)
    cat("Gathering zone_ID values\n")
    pb = txtProgressBar(min = 0, max = n,style = 3, width = 100, char = '*')
    
    for(i in 1:n){
      
      rid = rid.hs[i]
      
      dtmp = bas$data[[rid]]
      nr = nrow(dtmp)
      dtmp$idx2 = 1:nrow(dtmp)  # temporary id for this dataframe
      
      if(!is.na(bas$world_ID[rid]) &
         !is.na(bas$basin_ID[rid]) &
         !is.na(bas$hillslope_ID[rid])
      ){
        
        zn = dtmp %>%
          dplyr::filter(lvl == 4)
        
        zn$start = zn$idx2
        zn$end = c((zn$idx2[-1] - 1),dtmp$idx2[nr])
        
        m = nrow(zn)
        
        for(j in 1:m){dtmp$zone_ID[zn$start[j]:zn$end[j]] = zn$V1[j]}
        
      }
      
      bas$data[[rid]] = dtmp
      
      Sys.sleep(0.0000000000000001)
      setTxtProgressBar(pb,i)
      
    }
    
    close(pb)
    
    bas = bas %>%
      unnest("data") %>%
      arrange(idx) %>%
      dplyr::select(V1,V2,idx,lvl,world_ID,basin_ID,hillslope_ID,zone_ID)
    
    bas_bk3 = bas
    
  } else {
    
    cat("\nHillslope and Zone must be TRUE to get zone_ID\n")
    
  }
  
  
  if(Patch == TRUE & Zone == TRUE & Hillslope == TRUE){
    ##############################
    ## Indentify Parent Patches ##
    ##############################
    
    bas$patch_ID = NA
    
    bas = bas %>% 
      group_by(world_ID,basin_ID,hillslope_ID,zone_ID) %>%
      nest() %>%
      arrange(.,desc(is.na(zone_ID)),zone_ID)
    
    bas$rid = 1:nrow(bas) # row id for nested data frame
    
    ## filter out rows not at patch level or lower
    rid.zn = bas$rid[
      (!is.na(bas$world_ID) &
         !is.na(bas$basin_ID) &
         !is.na(bas$hillslope_ID) &
         !is.na(bas$zone_ID)
      )
      ]
    
    n = length(rid.zn)
    cat("Gathering patch_ID values\n")
    pb = txtProgressBar(min = 0, max = n,style = 3, width = 100, char = '*')
    
    for(i in 1:n){
      
      rid = rid.zn[i]
      
      dtmp = bas$data[[rid]]
      nr = nrow(dtmp)
      dtmp$idx2 = 1:nrow(dtmp)  # temporary id for this dataframe
      
      if(!is.na(bas$world_ID[rid]) &
         !is.na(bas$basin_ID[rid]) &
         !is.na(bas$hillslope_ID[rid]) &
         !is.na(bas$zone_ID[rid])
      ){
        
        pch = dtmp %>%
          dplyr::filter(lvl == 5)
        
        pch$start = pch$idx2
        pch$end = c((pch$idx2[-1] - 1),dtmp$idx2[nr])
        
        m = nrow(pch)

        for(j in 1:m){dtmp$patch_ID[pch$start[j]:pch$end[j]] = pch$V1[j]}
        
      }
      
      bas$data[[rid]] = dtmp
      
      Sys.sleep(0.0000000000000001)
      setTxtProgressBar(pb,i)
      
    }
      
      close(pb)
      
      bas = bas %>%
        unnest("data") %>%
        arrange(idx) %>%
        dplyr::select(V1,V2,idx,lvl,world_ID,basin_ID,hillslope_ID,zone_ID,patch_ID)
      
      bas_bk4 = bas
      
  } else {
    
    cat("\nHillslope, Zone, and Patch must be TRUE to get patch_ID\n")
    
  }
  
  if(Stratum == TRUE){
    ##############################
    ## Indentify Parent Stratum ##
    ##############################
    
    bas$canopy_strata_ID = NA
    
    bas = bas %>% 
      group_by(world_ID,basin_ID,hillslope_ID,zone_ID,patch_ID) %>%
      nest() %>%
      arrange(.,desc(is.na(patch_ID)),patch_ID)
    
    bas$rid = 1:nrow(bas) # row id for nested data frame
    
    ## filter out rows not at patch level or lower
    rid.pch = bas$rid[
      (!is.na(bas$world_ID) &
         !is.na(bas$basin_ID) &
         !is.na(bas$hillslope_ID) &
         !is.na(bas$zone_ID) &
         !is.na(bas$patch_ID)
      )
      ]
    
    n = length(rid.pch)
    cat("Gathering canopy_strata_ID values\n")
    pb = txtProgressBar(min = 0, max = n,style = 3, width = 100, char = '*')
    
    for(i in 1:n){
      
      #dtmp = bas$data[[i]]
      rid = rid.pch[i]
      
      dtmp = bas$data[[rid]]
      nr = nrow(dtmp)
      dtmp$idx2 = 1:nrow(dtmp)  # temporary id for this dataframe
      dtmp$canopy_strata_ID = NA
      
      #if(i > 1){
      if(!is.na(bas$world_ID[rid]) &
         !is.na(bas$basin_ID[rid]) &
         !is.na(bas$hillslope_ID[rid]) &
         !is.na(bas$zone_ID[rid]) &
         !is.na(bas$patch_ID[rid])
      ){
        
        strat = dtmp %>%
          dplyr::filter(lvl == 6)
        
        strat$start = strat$idx2
        strat$end = c((strat$idx2[-1] - 1),dtmp$idx2[nr])
        
        m = nrow(strat)
        
        for(j in 1:m){dtmp$canopy_strata_ID[strat$start[j]:strat$end[j]] = strat$V1[j]}
        
      }
      
      bas$data[[rid]] = dtmp
      
      Sys.sleep(0.0000000000000001)
      setTxtProgressBar(pb,i)
      
    }
    
    close(pb) ### left off (run this one) ###
    
    bas = bas %>%
      unnest("data") %>%
      arrange(idx) %>%
      dplyr::select(V1,V2,idx,lvl,world_ID,basin_ID,hillslope_ID,zone_ID,patch_ID,canopy_strata_ID)
    
    bas_bk5 = bas
    
  } else {
    
    cat("\nHillslope, Zone, Patch, and Stratum must be TRUE to get canopy_strata_ID\n")
    
  }
  
  return(bas)
  
} 

# TODO: Alterantive: Extract spatial hierarchy layer information for each patch for raster files
# TODO: (1) Create a raster stack of basin.tif, hillslope.tif, and patch.tif
# TODO: (2) Coerce the raster stack -> data.frame
# TODO: (3) Duplicate patch_ID column -> zone_ID column (they are the same)
# TODO: (4) Create canopy_strata_ID column -> set equal to 1 (overstory)
# TODO: (5) Duplicate steps 1-4 but set canopy_strata_ID column -> 2 (understory)
# TODO: (6) Bind the two dataframes by row
# TODO: Alternative: for step (4) set values = patch_ID and for step (5) values = patch_ID + 10^pwr