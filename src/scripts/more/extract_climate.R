library(tidyverse)
library(ncdf4)
library(raster)
library(glue)
library(data.table)

# Program settings
#syr=2075
#mod="CSIRO"
args = commandArgs(trailingOnly=TRUE)
syr = args[1]
mod = args[2]
tardir = glue("/data/adam/jonathan.gendron/rhessys/Kamiak/scenarios/gcm/{syr}/{mod}")
outdir = "/weka/data/lab/adam/jonathan.gendron/rhessys/RHESSysUtil/src/scripts/more"
patchID = raster("/weka/data/lab/adam/jonathan.gendron/rhessys/RHESSysUtil/src/scripts/more/patches.tif")

vlist = c("pr", "tasmax", "tasmin")

# Get files
setwd(tardir)
flist = list.files(".", pattern="nc")

dlist = list()
for(i in 1:length(vlist)){
	
	print(i)
	
	file = grep(vlist[i], flist, value=T)
	rtmp = raster(file, band=1)
	ncin = nc_open(file)
	
	vname = ncin$var %>% attributes() %>% .$names %>% .[1]
	dtmp = ncvar_get(ncin, vname)
	ttmp = ncvar_get(ncin,"time") %>% as.Date(., origin=as.Date("1900-01-01")) %>% lubridate::year(.)
	
	nc_close(ncin)
	
	if(vlist[i] == "pr"){
		# Data index table
		dt = data.table::as.data.table(ttmp)[, list(list(.I)), by = ttmp]
		names(dt) = c("year", "idx") # rename columns
		
		# Sum of precip per year
		dtmp = lapply(dt$idx, function(Indexes){
			apply(dtmp[,,Indexes],c(1,2), sum, na.rm=T)
		}) %>% simplify2array(.)
		
		# average precip per year
		dtmp = apply(dtmp, c(1,2), mean, na.rm=T)
		dtmp = dtmp*86400
		
	} else{
		dtmp = apply(dtmp, c(1,2), mean, na.rm=T)	
	}
	
	dtmp = raster(dtmp, crs=crs(rtmp))
	extent(dtmp) = extent(rtmp)
	dtmp = projectRaster(dtmp, crs=crs(patchID))
	dtmp = resample(dtmp, patchID)
	dlist[[vlist[i]]] = dtmp
	
}

dlist$tavg = ((dlist$tasmax + dlist$tasmin) / 2) - 273.15

setwd(outdir)

rout = stack(dlist$pr, dlist$tavg, patchID)
names(rout) = c("precip", "tavg", "patchID")

outfile=glue("{syr}_{mod}_climate.tif")
writeRaster(rout, outfile, overwrite=T)