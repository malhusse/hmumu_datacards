#!/bin/bash

OPTIONS="--X-rtd FITTER_NEWER_GIVE_UP --X-rtd FITTER_NEW_CROSSING_ALGO --cminDefaultMinimizerStrategy 0 --cminRunAllDiscreteCombinations --cminApproxPreFitTolerance=0.01 --cminFallbackAlgo Minuit2,Migrad,0:0.01 --cminFallbackAlgo Minuit2,Migrad,0:0.1 --X-rtd MINIMIZER_MaxCalls=9999999 --X-rtd MINIMIZER_analytic --X-rtd FAST_VERTICAL_MORPH --cminDefaultMinimizerTolerance 0.01 --X-rtd MINIMIZER_freezeDisassociatedParams"

JOBOPTS0="+JobFlavour = \"espresso\"\nrequirements = (OpSysAndVer =?= \"CentOS7\")"
JOBOPTS="$JOBOPTS0"

combineTool.py -M Significance -m 125 $OPTIONS -d ../datacard_cat0.root -t -1 --expectSignal=1 --toysFrequentist  -nexp_cat0 --job-mode condor --task-name expSigCat0 --sub-opts="$JOBOPTS\n+JobBatchName=\"significance \""

combineTool.py -M Significance -m 125 $OPTIONS -d ../datacard_cat1.root -t -1 --expectSignal=1 --toysFrequentist  -nexp_cat1 --job-mode condor --task-name expSigCat1 --sub-opts="$JOBOPTS\n+JobBatchName=\"significance \""

combineTool.py -M Significance -m 125 $OPTIONS -d ../datacard_cat2.root -t -1 --expectSignal=1 --toysFrequentist  -nexp_cat2 --job-mode condor --task-name expSigCat2 --sub-opts="$JOBOPTS\n+JobBatchName=\"significance \""

combineTool.py -M Significance -m 125 $OPTIONS -d ../datacard_cat3.root -t -1 --expectSignal=1 --toysFrequentist  -nexp_cat3 --job-mode condor --task-name expSigCat3 --sub-opts="$JOBOPTS\n+JobBatchName=\"significance \""

combineTool.py -M Significance -m 125 $OPTIONS -d ../datacard_cat4.root -t -1 --expectSignal=1 --toysFrequentist  -nexp_cat4 --job-mode condor --task-name expSigCat4 --sub-opts="$JOBOPTS\n+JobBatchName=\"significance \""

combineTool.py -M Significance -m 125 $OPTIONS -d ../datacard_all_cats.root -t -1 --expectSignal=1 --toysFrequentist  -nexp_all --job-mode condor --task-name expSigAll --sub-opts="$JOBOPTS\n+JobBatchName=\"significance \""

combineTool.py -M Significance -m 125 $OPTIONS -d ../datacard_cat0.root  -nobs_cat0 --job-mode condor --task-name obsSigCat0 --sub-opts="$JOBOPTS\n+JobBatchName=\"significance \""

combineTool.py -M Significance -m 125 $OPTIONS -d ../datacard_cat1.root  -nobs_cat1 --job-mode condor --task-name obsSigCat1 --sub-opts="$JOBOPTS\n+JobBatchName=\"significance \""

combineTool.py -M Significance -m 125 $OPTIONS -d ../datacard_cat2.root  -nobs_cat2 --job-mode condor --task-name obsSigCat2 --sub-opts="$JOBOPTS\n+JobBatchName=\"significance \""

combineTool.py -M Significance -m 125 $OPTIONS -d ../datacard_cat3.root  -nobs_cat3 --job-mode condor --task-name obsSigCat3 --sub-opts="$JOBOPTS\n+JobBatchName=\"significance \""

combineTool.py -M Significance -m 125 $OPTIONS -d ../datacard_cat4.root  -nobs_cat4 --job-mode condor --task-name obsSigCat4 --sub-opts="$JOBOPTS\n+JobBatchName=\"significance \""

combineTool.py -M Significance -m 125 $OPTIONS -d ../datacard_all_cats.root  -nobs_all --job-mode condor --task-name obsSigAll --sub-opts="$JOBOPTS\n+JobBatchName=\"significance \""
