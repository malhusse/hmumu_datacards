#!/bin/bash 

OPTIONS="--X-rtd FITTER_NEWER_GIVE_UP --X-rtd FITTER_NEW_CROSSING_ALGO --cminDefaultMinimizerStrategy 1 --cminRunAllDiscreteCombinations --cminApproxPreFitTolerance=0.01 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rtd MINIMIZER_MaxCalls=9999999 --X-rtd MINIMIZER_analytic --X-rtd FAST_VERTICAL_MORPH --cminDefaultMinimizerTolerance 0.01 --X-rtd MINIMIZER_freezeDisassociatedParams"

JOBOPTS0="+JobFlavour = \"espresso\"\nrequirements = (OpSysAndVer =?= \"CentOS7\")"
JOBOPTS="$JOBOPTS0"

for MASS in $(seq 120 0.5 130); do
    combineTool.py -n LimitTest -M AsymptoticLimits -m $MASS ../datacard_all_cats.root --run both $OPTIONS --job-mode condor --task-name limitBoth$MASS --sub-opts="$JOBOPTS\n+JobBatchName=\"Limits \""
done