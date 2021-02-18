import sys,glob
from array import array
import ROOT

ROOT.gROOT.SetBatch(ROOT.kTRUE)

unsortedmass = []

mass = array('d')
zeros = array('d')
exp = array('d')
obs = array('d')

files=glob.glob("results_hmm/higgsCombineSignifExp.Significance.mH*.root")
for afile in files:
    m = afile.split('mH')[1].replace('.root','')
    unsortedmass.append(float(m))
unsortedmass.sort()

for m in unsortedmass:
    # mass value
    mass.append(m)
    # get the expected p-value
    f_exp = ROOT.TFile("results_hmm/higgsCombineSignifExp.Significance.mH"+str(m).replace('.0','')+".root","READ")
    t_exp = f_exp.Get("limit")
    t_exp.GetEntry(0)
    exp.append(t_exp.limit)
    # get the observed p-value
    f_obs = ROOT.TFile("results_hmm/higgsCombineSignifObs.Significance.mH"+str(m).replace('.0','')+".root","READ")
    t_obs = f_obs.Get("limit")
    t_obs.GetEntry(0)
    obs.append(t_obs.limit)
    # dummy, for mass error
    zeros.append(0.0)

# convert array to TVector
# mass = ROOT.TVectorD(len(mass),mass)
# zeros = ROOT.TVectorD(len(zeros),zeros)
# exp = ROOT.TVectorD(len(exp),exp)
# obs = ROOT.TVectorD(len(obs),obs)
# new canvas
c7 = ROOT.TCanvas("c7","c7",800, 800)
c7.SetLogy()
c7.SetRightMargin(0.06)
c7.SetLeftMargin(0.2)
# dummy histogram, for axis labels, ranges, etc.
dummy = ROOT.TH1D("","", 1, 120,130)
dummy.SetStats(ROOT.kFALSE)
dummy.SetBinContent(1,0.0)
dummy.GetXaxis().SetTitle('m(H) [GeV]')
dummy.GetYaxis().SetTitle('Local p-value')
dummy.SetLineColor(0)
dummy.SetLineWidth(0)
dummy.SetFillColor(0)
dummy.SetMinimum(0.0001)
dummy.SetMaximum(1.0)
dummy.Draw()

# Draw some lines corresponding to 1,2,3 sigma 
latexf = ROOT.TLatex()
latexf.SetTextSize(0.4*c7.GetTopMargin())
latexf.SetTextColor(2)
f1 = ROOT.TF1("f1","0.15866",115,145)
f1.SetLineColor(2)
f1.SetLineWidth(2)
f1.Draw("lsame")
latexf.DrawLatex(129, 0.15866*1.1,"1#sigma")
f2 = ROOT.TF1("f1","0.02275",115,145)
f2.SetLineColor(2)
f2.SetLineWidth(2)
f2.Draw("lsame")
latexf.DrawLatex(129, 0.02275*1.1,"2#sigma")
f3 = ROOT.TF1("f1","0.0013499",115,145)
f3.SetLineColor(2)
f3.SetLineWidth(2)
f3.Draw("lsame")
latexf.DrawLatex(129, 0.0013499*1.1,"3#sigma")

# Draw the expected p-value graph
gr_exp = ROOT.TGraphAsymmErrors(len(mass),mass,exp,zeros,zeros,zeros,zeros)
gr_exp.SetLineColor(4)
gr_exp.SetLineWidth(2)
gr_exp.SetLineStyle(2)
gr_exp.Draw("Lsame")
# Draw the observed p-value graph
gr_obs = ROOT.TGraphAsymmErrors(len(mass),mass,obs,zeros,zeros,zeros,zeros)
gr_obs.SetLineColor(1)
gr_obs.SetLineWidth(2)
gr_obs.Draw("CPsame")

# latex2 = ROOT.TLatex()
# latex2.SetNDC()
# latex2.SetTextSize(0.5*c7.GetTopMargin())
# latex2.SetTextFont(42)
# latex2.SetTextAlign(31) # align right                                                                                                                              
# latex2.DrawLatex(0.87, 0.95,"19.6 fb^{-1} (8 TeV)")
# latex2.SetTextSize(0.7*c7.GetTopMargin())
# latex2.SetTextFont(62)
# latex2.SetTextAlign(11) # align right                                                                                                                              
# latex2.DrawLatex(0.20, 0.95, "CMS")
# latex2.SetTextSize(0.6*c7.GetTopMargin())
# latex2.SetTextFont(52)
# latex2.SetTextAlign(11)
# latex2.DrawLatex(0.32, 0.95, "Tutorial")

c7.Draw()
c7.SaveAs("pvalue.pdf")
