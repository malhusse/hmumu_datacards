#!/bin/bash

OPTIONS="--X-rtd FITTER_NEWER_GIVE_UP --X-rtd FITTER_NEW_CROSSING_ALGO --cminDefaultMinimizerStrategy 0 --cminRunAllDiscreteCombinations --cminApproxPreFitTolerance=0.01 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rtd MINIMIZER_MaxCalls=9999999 --X-rtd MINIMIZER_analytic --X-rtd FAST_VERTICAL_MORPH --cminDefaultMinimizerTolerance 0.01 --X-rtd MINIMIZER_freezeDisassociatedParams"

JOBOPTS0="+JobFlavour = \"espresso\"\nrequirements = (OpSysAndVer =?= \"CentOS7\")"
JOBOPTS="$JOBOPTS0"

combineTool.py -M AsymptoticLimits -m 125 $OPTIONS -d ../datacard_cat0.root --run both -n _cat0 --job-mode condor --task-name LimCat0 --sub-opts="$JOBOPTS\n+JobBatchName=\"asymLimits \""

combineTool.py -M AsymptoticLimits -m 125 $OPTIONS -d ../datacard_cat1.root --run both -n _cat1 --job-mode condor --task-name LimCat1 --sub-opts="$JOBOPTS\n+JobBatchName=\"asymLimits \""

combineTool.py -M AsymptoticLimits -m 125 $OPTIONS -d ../datacard_cat2.root --run both -n _cat2 --job-mode condor --task-name LimCat2 --sub-opts="$JOBOPTS\n+JobBatchName=\"asymLimits \""

combineTool.py -M AsymptoticLimits -m 125 $OPTIONS -d ../datacard_cat3.root --run both -n _cat3 --job-mode condor --task-name LimCat3 --sub-opts="$JOBOPTS\n+JobBatchName=\"asymLimits \""

combineTool.py -M AsymptoticLimits -m 125 $OPTIONS -d ../datacard_cat4.root --run both -n _cat4 --job-mode condor --task-name LimCat4 --sub-opts="$JOBOPTS\n+JobBatchName=\"asymLimits \""

combineTool.py -M AsymptoticLimits -m 125 $OPTIONS -d ../datacard_all_cats.root --run both -n _all --job-mode condor --task-name LimAll --sub-opts="$JOBOPTS\n+JobBatchName=\"asymLimits \""