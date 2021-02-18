#!/bin/bash 

OPTIONS="--X-rtd FITTER_NEWER_GIVE_UP --X-rtd FITTER_NEW_CROSSING_ALGO --cminDefaultMinimizerStrategy 1 --cminRunAllDiscreteCombinations --cminApproxPreFitTolerance=0.01 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rtd MINIMIZER_MaxCalls=9999999 --X-rtd MINIMIZER_analytic --X-rtd FAST_VERTICAL_MORPH --cminDefaultMinimizerTolerance 0.01 --X-rtd MINIMIZER_freezeDisassociatedParams"

JOBOPTS0="+JobFlavour = \"microcentury\"\nrequirements = (OpSysAndVer =?= \"CentOS7\")"
JOBOPTS="$JOBOPTS0"

combine -M GenerateOnly -d ../datacard_all_cats.root -m 125 -t -1 --expectSignal 1 --toysFrequentist --saveToys $OPTIONS

for i in $(seq 120 0.5 130); do
    echo Computing p-value for MH = $i
    combineTool.py -n SignifExp -M Significance -m $i -d ../datacard_all_cats.root $OPTIONS --toysFile higgsCombineTest.GenerateOnly.mH125.123456.root --toysFrequentist -t -1 --pvalue --expectSignal=1 
    #--job-mode condor --task-name pvalExp$MASS --sub-opts="$JOBOPTS\n+JobBatchName=\"pval \""
    combineTool.py -n SignifObs -M Significance -m $i -d ../datacard_all_cats.root $OPTIONS --pvalue 
    #--job-mode condor --task-name pvalObs$MASS --sub-opts="$JOBOPTS\n+JobBatchName=\"pval \""
done                                                                                  
