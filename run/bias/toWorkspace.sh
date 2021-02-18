#!/bin/sh

text2workspace.py ../../workspaces_full_sixPDFs/datacard_cat0_nosyst.txt -o datacard_cat0_nosyst.root 
text2workspace.py ../../workspaces_full_sixPDFs/datacard_cat1_nosyst.txt -o datacard_cat1_nosyst.root
text2workspace.py ../../workspaces_full_sixPDFs/datacard_cat2_nosyst.txt -o datacard_cat2_nosyst.root
text2workspace.py ../../workspaces_full_sixPDFs/datacard_cat3_nosyst.txt -o datacard_cat3_nosyst.root
text2workspace.py ../../workspaces_full_sixPDFs/datacard_cat4_nosyst.txt -o datacard_cat4_nosyst.root

combineCards.py ../../workspaces_full_sixPDFs/datacard_cat0_nosyst.txt ../../workspaces_full_sixPDFs/datacard_cat1_nosyst.txt ../../workspaces_full_sixPDFs/datacard_cat2_nosyst.txt ../../workspaces_full_sixPDFs/datacard_cat3_nosyst.txt ../../workspaces_full_sixPDFs/datacard_cat4_nosyst.txt > datacard_all_cats.txt
text2workspace.py datacard_all_cats.txt
