Requirements for Target Driven Spinup Proceedure

1. Spinup.def file
 This explains tolerance and max sim time

2. Target File
 Shows hierarchy of each stratum layer
 in our case only run overstory
 header shows <number of targeted stratum, number of observed targets, variable name to be targeted>
 This can only be values in the stratum[0].epc structure I belelive
 basin_ID hill_ID zone_ID patch_ID stratum_ID height are main columns

3. Altering the header file to include
	(1) 1	num_spinup_default_files
	(2) <path/to/spinup.def/file>
 This goes below canopy strata files but above basestation files in your header file

4. Add the following flag to the command line arguements ...
	-vegspinup <path_to_spinup_target_file>


### Before Conducting a spinup job, input statefiles must be ammended to include spinup_object_ID w/ a value of 1 for each stratum layer in spatial hierarchy
## 1.00 "spinup_object_ID" > should be added directly 1 line under the 1.00 "veg_parm_ID" rows 
#this can be done using R or by using an awk command
# "add_spinup_default2.awk" is the script used to alter the statefiles


### To add spinup_object_ID to statefile

## use the .awk script in this directory w/in a linux terminal
# awk -f file.awk <target_statefile> output_statefile_name
# awk -f file.awk target_statefile > output_statefile_name

#### awk script was not working for the altered statefile (set vegetation state variables to 0) > so 1 day simulation was run to get new statefile in workable format for awk script #####

## Running the awk script
# in a linux termal, type the following line of code ...
# $ awk -f add_spinup_default2.awk <b4_soil_init_veg_clear.state.Y1979M10D2H1> br_b4_veg_spin
# alternatively ...
# $ awk -f add_spinup_default2.awk b4_soil_init_veg_clear.state.Y1979M10D2H1 > br_b4_veg_spin

### State files > In Chronologic order of creation

## br_soil_init_veg_clear.state > state after soil was initilized and vegetation cleared
## br_soil_init_veg_clear.state.Y1979M10D2H1 > output from 1 day simulation of model | previous format was not allowing for .awk script to to add "spinup_object_ID" line 
## br_b4_veg_spin.state > output from .awk script | script added "spinup_object_ID" lines into state file | derived from br_soil_init_veg_clear.state.Y1979M10D2H1
\ No newline at end of file

