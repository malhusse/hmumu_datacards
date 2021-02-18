import sys,glob
from array import array
import ROOT

ROOT.gROOT.SetBatch(ROOT.kTRUE)

# create some arrays to hold the results values
mass = array('d')
zeros = array('d')
exp_p2 = array('d')
exp_p1 = array('d')
exp = array('d')
exp_m1 = array('d')
exp_m2 = array('d')
obs = array('d')

# gather all the results files and sort the mass values
sortedmass = []
files=glob.glob("results_hmm/higgsCombineLimitTest.AsymptoticLimits.mH*.root")
for afile in files:
    m = afile.split('mH')[1].replace('.root','')
    sortedmass.append(float(m))
sortedmass.sort()

# loop over the mass values and fill the arrays
for m in sortedmass:
    # mass value
    mass.append(m)
    # get the limit tree for this mass value
    f = ROOT.TFile("results_hmm/higgsCombineLimitTest.AsymptoticLimits.mH"+str(m).replace('.0','')+".root","READ")
    t = f.Get("limit")
    # expected limit
    t.GetEntry(2)
    thisexp = t.limit
    exp.append(thisexp)
    #-2 sigma
    t.GetEntry(0)
    exp_m2.append(thisexp-t.limit)
    #-1 sigma
    t.GetEntry(1)
    exp_m1.append(thisexp-t.limit)
    #+1 sigma 
    t.GetEntry(3)
    exp_p1.append(t.limit-thisexp)
    #+2 sigma
    t.GetEntry(4)
    exp_p2.append(t.limit-thisexp)
    # observed limit
    t.GetEntry(5)
    obs.append(t.limit)
    # dummy array with 0.0 (for mass-uncertainty)
    zeros.append(0.0)

#new canvas

c6 = ROOT.TCanvas("c6","c6",800,800)
c6.SetGridx()
c6.SetGridy()
c6.SetRightMargin(0.06)
c6.SetLeftMargin(0.2)

# dummy historgram for axes labels, ranges, etc.
dummy = ROOT.TH1D("","", 1, 120,130)
dummy.SetStats(ROOT.kFALSE)
dummy.SetBinContent(1,0.0)
dummy.GetXaxis().SetTitle('m(H) [GeV]')
dummy.GetYaxis().SetTitle('#sigma / #sigma(SM)')
dummy.SetLineColor(0)
dummy.SetLineWidth(0)
dummy.SetFillColor(0)
dummy.SetMinimum(0.0)
dummy.SetMaximum(5.0)
dummy.Draw()

gr_exp2 = ROOT.TGraphAsymmErrors(len(mass), mass,exp,zeros,zeros,exp_m2,exp_p2)
gr_exp2.SetLineColor(ROOT.kOrange)
gr_exp2.SetFillColor(ROOT.kOrange)
gr_exp2.Draw("e3same")

gr_exp1 = ROOT.TGraphAsymmErrors(len(mass), mass,exp,zeros,zeros,exp_m1,exp_p1)
gr_exp1.SetLineColor(ROOT.kGreen+1)
gr_exp1.SetFillColor(ROOT.kGreen+1)
gr_exp1.Draw("e3same")

gr_exp = ROOT.TGraphAsymmErrors(len(mass), mass,exp,zeros,zeros,zeros,zeros)
gr_exp.SetLineColor(1)
gr_exp.SetLineWidth(2)
gr_exp.SetLineStyle(2)
gr_exp.Draw("Lsame")

gr_obs = ROOT.TGraphAsymmErrors(len(mass),mass, obs,zeros,zeros,zeros,zeros)
gr_obs.SetLineColor(1)
gr_obs.SetLineWidth(2)
gr_obs.Draw("CPsame")

# latex2 = ROOT.TLatex()
# latex2.SetNDC()
# latex2.SetTextSize(0.5*c6.GetTopMargin())
# latex2.SetTextFont(42)
# latex2.SetTextAlign(31) # align right                                                                                             
# latex2.DrawLatex(0.87, 0.95,"19.6 fb^{-1} (8 TeV)")
# latex2.SetTextSize(0.9*c6.GetTopMargin())
# latex2.SetTextFont(62)
# latex2.SetTextAlign(11) # align right                                                                                             
# latex2.DrawLatex(0.25, 0.85, "CMS")
# latex2.SetTextSize(0.7*c6.GetTopMargin())
# latex2.SetTextFont(52)
# latex2.SetTextAlign(11)
# latex2.DrawLatex(0.25, 0.8, "Tutorial")

legend = ROOT.TLegend(.60,.70,.90,.87)
legend.AddEntry(gr_obs , "Observed 95% CL", "l")
legend.AddEntry(gr_exp , "Expected 95% CL", "l")
legend.AddEntry(gr_exp1 , "#pm 1#sigma", "f")
legend.AddEntry(gr_exp2 , "#pm 2#sigma", "f")
legend.SetShadowColor(0)
legend.SetFillColor(0)
legend.SetLineColor(0)
legend.Draw("same")

ROOT.gPad.RedrawAxis()

c6.Draw()
c6.SaveAs("limit_scan.pdf")