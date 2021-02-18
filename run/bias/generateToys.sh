#!/bin/bash

for NUM in {0..5}
do
    combine datacard_cat0_nosyst.root -M GenerateOnly --toysFrequentist -t 2000 --expectSignal 1 --saveToys -m 125 -n _cat0_gen_$NUM --setParameters pdf_index=$NUM --freezeParameters=MH,pdf_index --freezeNuisanceGroups CMS_hmm_global
    combine datacard_cat1_nosyst.root -M GenerateOnly --toysFrequentist -t 2000 --expectSignal 1 --saveToys -m 125 -n _cat1_gen_$NUM --setParameters pdf_index=$NUM --freezeParameters=MH,pdf_index --freezeNuisanceGroups CMS_hmm_global
    combine datacard_cat2_nosyst.root -M GenerateOnly --toysFrequentist -t 2000 --expectSignal 1 --saveToys -m 125 -n _cat2_gen_$NUM --setParameters pdf_index=$NUM --freezeParameters=MH,pdf_index --freezeNuisanceGroups CMS_hmm_global
    combine datacard_cat3_nosyst.root -M GenerateOnly --toysFrequentist -t 2000 --expectSignal 1 --saveToys -m 125 -n _cat3_gen_$NUM --setParameters pdf_index=$NUM --freezeParameters=MH,pdf_index --freezeNuisanceGroups CMS_hmm_global
    combine datacard_cat4_nosyst.root -M GenerateOnly --toysFrequentist -t 2000 --expectSignal 1 --saveToys -m 125 -n _cat4_gen_$NUM --setParameters pdf_index=$NUM --freezeParameters=MH,pdf_index --freezeNuisanceGroups CMS_hmm_global

done
