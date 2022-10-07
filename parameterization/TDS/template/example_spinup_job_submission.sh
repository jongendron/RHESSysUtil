
#!/bin/bash
#   Set the requested resources
#PBS -l nodes=1:ppn=32,mem=8gb
#PBS -l walltime=168:00:00
#PBS -q hydro
#PBS -m bea

#PBS -M jgendron@wsu.edu
#   Combine log and error file paths
#PBS -j oe
#printf(   Request email on (a)bort, (b)eginning, and (e)nd.
#PBS -V

# Load intel compiler and set number of parallel CPU - should equal ppn
module purge
module load compilers/gcc/6.1.0
module load netcdf/4.4.1_intel

export OMP_NUM_THREADS=8

HOME_DIR="/data/hydro/users/jgendron/rhessys/rhessys_spinup_veg/rhessys"
OUT_DIR="/data/hydro/users/jgendron/rhessys/rhessys_spinup_veg/rhessys/output"


echo ------------------------------------------------------
echo -n 'Number of available processors: $nproc'
echo -n 'Job is running on node '; cat $PBS_NODEFILE
echo ------------------------------------------------------
echo ' '


##########################################################################################################

### File location variables
tecfile=$HOME_DIR/tecs/spinup_target.tec # need change
worldfile=$HOME_DIR/world/br_pre_spin.state
flowfile=$HOME_DIR/flow/br_flow.flow
worldhr=$HOME_DIR/hdr/spinup_target.hdr   # here under2 is the correct defs file
spinup=$HOME_DIR/spin/spinup_targets.txt

### Parameter variables
m=3.333    # need change maybe
k=258.01
po=0.7037
pa=0.9
gw1=0.1029
gw2=0.1500273
#outpre="target_spin" # need change and also below the time

#################################

$HOME_DIR/bin/rhessys8 -t $tecfile -w $worldfile -whdr $worldhr  -r $flowfile -st 1979 10 1 1 -ed 2480 10 2 1 -pre $OUT_DIR/target -s $m $k -sv $m $k -svalt $po $pa -gw $gw1 $gw2 -ncgridinterp 10 -climrepeat -netcdfgrid -b -g -vegspinup $spinup


 

