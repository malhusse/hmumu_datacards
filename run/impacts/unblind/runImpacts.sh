#!/bin/bash
#UNBLIND

OPTIONS="--X-rtd FITTER_NEWER_GIVE_UP --X-rtd FITTER_NEW_CROSSING_ALGO --cminDefaultMinimizerStrategy 0 --cminRunAllDiscreteCombinations --cminApproxPreFitTolerance=0.01 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rtd MINIMIZER_MaxCalls=9999999 --X-rtd MINIMIZER_analytic --X-rtd FAST_VERTICAL_MORPH --cminDefaultMinimizerTolerance 0.01 --X-rtd MINIMIZER_freezeDisassociatedParams"

JOBOPTS0="+JobFlavour = \"espresso\"\nrequirements = (OpSysAndVer =?= \"CentOS7\")"
JOBOPTS="$JOBOPTS0"

combineTool.py -M Impacts -d ../../datacard_all_cats.root --doInitialFit -m 125 --expectSignal 1 -n postfit_asimov ${OPTIONS}

combineTool.py -M Impacts -d ../../datacard_all_cats.root --doFits -m 125 --expectSignal 1 ${OPTIONS} -n postfit_asimov --job-mode condor --task-name Impacts_doFits --sub-opts="$JOBOPTS\n+JobBatchName=\"Impacts\""
