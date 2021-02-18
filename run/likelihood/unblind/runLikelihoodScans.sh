#!/bin/bash
# blind

OPTIONS="--X-rtd FITTER_NEWER_GIVE_UP --X-rtd FITTER_NEW_CROSSING_ALGO --cminDefaultMinimizerStrategy 0 --cminRunAllDiscreteCombinations --cminApproxPreFitTolerance=0.01 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rtd MINIMIZER_MaxCalls=9999999 --X-rtd MINIMIZER_analytic --X-rtd FAST_VERTICAL_MORPH --cminDefaultMinimizerTolerance 0.01 --X-rtd MINIMIZER_freezeDisassociatedParams"

JOBOPTS0="+JobFlavour = \"espresso\"\nrequirements = (OpSysAndVer =?= \"CentOS7\")"
JOBOPTS="$JOBOPTS0"

combineTool.py -d ../../datacard_all_cats.root -M MultiDimFit -m 125 $OPTIONS -n Nominal --rMin=-1 --rMax=4 --algo=grid --points=100 --expectSignal=1 --split-points 10 --job-mode condor --task-name likelihood_full --sub-opts="$JOBOPTS\n+JobBatchName=\"likelihood scans full\""

combineTool.py -d ../../datacard_all_cats.root -M MultiDimFit -m 125 $OPTIONS -n StatOnly --rMin=-1 --rMax=4 --algo=grid --points=100 --expectSignal=1 --freezeParameters  allConstrainedNuisances --split-points 10 --job-mode condor --task-name likelihood_statOnly --sub-opts="$JOBOPTS\n+JobBatchName=\"likelihood scans stat\""