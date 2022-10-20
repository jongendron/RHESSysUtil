Min's Bayesian Calibration Workflow

1. Define Prior probability distribution(s) for parameters that will be calibrated and initial conditions for testing
	- set min, max values for parameter(s)
	- set values and stddev for target model output variables
	- Set "interval length" used during proposal distribution drawing (randomly select value from prior probability distribution of parameter(s) to test; value is used to add to existing parameter for subsequent sim)
	- set initial parameter values as f(rand_idx, min, max)
		- f = rand_idx * 0.01 * (max - min) + min

2. Conduct MCMC Method a predefined number of times (2000 used by Min)
	- Conduct RHESSys simulation
		- set model parameters in stratum_evergreen.def file as 
			(a) predefined initial parameter values if first simulatoin
			(b) previous paramter value plus randomly drawn interval length (more on this below)
	- Calculate likelihood of parameter set based on model output and targets
		- Use "growth_yearly_model_performance_nppratio_height_npp_LAI.py"
	- Test whether to keep the parameter set to inform the Posterior probability distribution
		- If first iteration keep
		- If nth simulation then calculate ...
			(a) beta = likelihood / old_likeihood
			(b) u = random number [integer?] from [0,100]
			(c) ru = u * 0.01 (1% of random integer)
		- Then if ru < beta then ...
			(a) accept parameter(s) for this iteration as informative to posterior probabiliy distribution
			(b) set old_likelihood = likelihood (current likeihood of this iteration)
			(c) set old_CAL (store current parameters in backup object) as current parameter(s)
		- Else ...
			- reject this parameter set
	- Generate new proposal parameter set from the defined proposal distribution (prior probability distribution)
		- In this workflow a Gausian distribution was defined
		- Calculate the addadive coeficent to change existing parameter value(s)
			- This value will be added to existing parameter values
			- Use "generate_gauss_random.py"
		- Change the current parameter set (old_CAL) using the addadive coeficent to scale
			- CAL[cidx] = old_CAL[cidx] + dt[cidx]
		- Ensure the new parameter value falls within the predefined range (min[cidx] & max[cidx])
			- if CAL[cidx] < min[cidx] -> CAL[cidx] = min[cidx]
			- if CAL[cidx] > max[cidx] -> CAL[cidx] = max[cidx]
		
	- Iterate back to first step using the new parameter values
			
		
		

