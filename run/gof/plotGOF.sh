#!/bin/bash

hadd -f higgsCombine_postfit_asimov.GoodnessOfFit.mH125.root higgsCombine_postfit_asimov_batch*.GoodnessOfFit.mH125.*.root
mv higgsCombine_postfit_asimov_batch*.GoodnessOfFit.mH125.*.root batchOutputs

mv higgsCombine_observed.GoodnessOfFit.mH125.*.root higgsCombine_observed.GoodnessOfFit.mH125.root

combineTool.py -M CollectGoodnessOfFit --mass 125 -o gof.json --input higgsCombine_observed.GoodnessOfFit.mH125.root higgsCombine_postfit_asimov.GoodnessOfFit.mH125.root

plotGof.py gof.json -o gof --mass 125.0