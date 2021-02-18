#!/bin/bash

combineTool.py -M Impacts -d ../datacard_all_cats.root -m 125 -o impacts.json -n postfit_asimov 
#--exclude=

plotImpacts.py -i impacts.json -o impacts

mv higgsCombine*.root batchOutputs