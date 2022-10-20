library(tidyverse)
library(raster)

pch0 = raster("./TC_sb1_patches.tif")
pch0[pch0[] == -9999] = NA

dtmp = pch0[]
idx = is.na(dtmp)

heights = rnorm(n = length(dtmp), mean = 60, sd = 0.03*(200))
heights[idx] = NA

tar.ht = pch0
tar.ht[] = heights

plot(tar.ht)

writeRaster(tar.ht,"TC_tar_canopy_ht.tif")

