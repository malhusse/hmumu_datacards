#!/bin/bash

OPTIONS="--X-rtd FITTER_NEWER_GIVE_UP --X-rtd FITTER_NEW_CROSSING_ALGO --cminDefaultMinimizerStrategy 0 --cminRunAllDiscreteCombinations --cminApproxPreFitTolerance=0.01 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rtd MINIMIZER_MaxCalls=9999999 --X-rtd MINIMIZER_analytic --X-rtd FAST_VERTICAL_MORPH --cminDefaultMinimizerTolerance 0.01 --X-rtd MINIMIZER_freezeDisassociatedParams"

JOBOPTS0="+JobFlavour = \"microcentury\"\nrequirements = (OpSysAndVer =?= \"CentOS7\")"
JOBOPTS="$JOBOPTS0"

combineTool.py -d ../datacard_all_cats.root -M GoodnessOfFit -m 125 $OPTIONS --expectSignal=0 -t 0  -n _observed --job-mode condor --task-name GoF_Obs --sub-opts="$JOBOPTS\n+JobBatchName=\"GoF\"" --algo=saturated -s -1 

for idx in {1..20}; do
    combineTool.py -d ../datacard_all_cats.root -M GoodnessOfFit -m 125 $OPTIONS --expectSignal=0 -t 50 -n _postfit_asimov_batch${idx} --job-mode condor --task-name GoF_MC_batch${idx} --sub-opts="$JOBOPTS\n+JobBatchName=\"GoF MC\"" --algo=saturated -s -1 --toysFrequentist
done
