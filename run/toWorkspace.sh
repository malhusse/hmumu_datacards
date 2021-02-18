#!/bin/sh

combineCards.py ../workspaces_full/datacard_cat0.txt ../workspaces_full/datacard_bkg_cat1.txt ../workspaces_full/datacard_bkg_cat2.txt ../workspaces_full/datacard_bkg_cat3.txt ../workspaces_full/datacard_bkg_cat4.txt > datacard_cat0.txt
combineCards.py ../workspaces_full/datacard_bkg_cat0.txt ../workspaces_full/datacard_cat1.txt ../workspaces_full/datacard_bkg_cat2.txt ../workspaces_full/datacard_bkg_cat3.txt ../workspaces_full/datacard_bkg_cat4.txt > datacard_cat1.txt
combineCards.py ../workspaces_full/datacard_bkg_cat0.txt ../workspaces_full/datacard_bkg_cat1.txt ../workspaces_full/datacard_cat2.txt ../workspaces_full/datacard_bkg_cat3.txt ../workspaces_full/datacard_bkg_cat4.txt > datacard_cat2.txt
combineCards.py ../workspaces_full/datacard_bkg_cat0.txt ../workspaces_full/datacard_bkg_cat1.txt ../workspaces_full/datacard_bkg_cat2.txt ../workspaces_full/datacard_cat3.txt ../workspaces_full/datacard_bkg_cat4.txt > datacard_cat3.txt
combineCards.py ../workspaces_full/datacard_bkg_cat0.txt ../workspaces_full/datacard_bkg_cat1.txt ../workspaces_full/datacard_bkg_cat2.txt ../workspaces_full/datacard_bkg_cat3.txt ../workspaces_full/datacard_cat4.txt > datacard_cat4.txt

text2workspace.py datacard_cat0.txt 
text2workspace.py datacard_cat1.txt
text2workspace.py datacard_cat2.txt
text2workspace.py datacard_cat3.txt
text2workspace.py datacard_cat4.txt

combineCards.py ../workspaces_full/datacard_cat0.txt ../workspaces_full/datacard_cat1.txt ../workspaces_full/datacard_cat2.txt ../workspaces_full/datacard_cat3.txt ../workspaces_full/datacard_cat4.txt > datacard_all_cats.txt
text2workspace.py datacard_all_cats.txt
