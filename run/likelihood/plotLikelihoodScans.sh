hadd -f higgsCombineNominal.MultiDimFit.mH125.root higgsCombineNominal.POINTS.*.MultiDimFit.mH125.root
mv higgsCombineNominal.POINTS.*.MultiDimFit.mH125.root batchOutputs

hadd -f higgsCombineStatOnly.MultiDimFit.mH125.root higgsCombineStatOnly.POINTS.*.MultiDimFit.mH125.root
mv higgsCombineStatOnly.POINTS.*.MultiDimFit.mH125.root batchOutputs

plot1DScan.py higgsCombineNominal.MultiDimFit.mH125.root --main-color 1 --main-label "H#rightarrow#mu#mu (13 TeV) Expected" -o likelihoodExp --y-cut 10 --y-max 6

plot1DScan.py higgsCombineNominal.MultiDimFit.mH125.root --main-color 1 --main-label "H#rightarrow#mu#mu (13 TeV) Expected" -o likelihoodExpSplit --y-cut 10 --y-max 6 --others higgsCombineStatOnly.MultiDimFit.mH125.root:Stat:38  --breakdown "Syst.,Stat."
