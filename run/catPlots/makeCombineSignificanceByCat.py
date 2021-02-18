import os,sys
from array import array
import re,math
from subprocess import call
from optparse import OptionParser, OptionGroup

usage="program [label=]higss*OBS,EXP  OBS2,EXP2"
parser=OptionParser()
parser.add_option("-b","--batch",dest="batch",default=False,action="store_true")
parser.add_option("-u","--unblind",dest="unblind",default=False,action="store_true")
#parser.add_option("-i","--input",type='string',help="Input ROOT file. [%default]", default="Hmumu.root")
parser.add_option("-a","--all",action='store_true',help="All [%default]", default=False)
parser.add_option("-l","--lumi",help="Luminosity [%default]", default="137")
parser.add_option("-o","--outname",help="outname [%default]", default="./significancePerCat.pdf")
parser.add_option("","--pval",dest="pval",default=False,help='Actually I stored the pvalue',action="store_true")
parser.add_option("-s","--style",type='int',help="style (0=red, 1=blue) [%default]", default=0)
opts,args= parser.parse_args()

########### IMPORT ROOT #############
oldArgv=sys.argv[:]
sys.argv=[]
import ROOT
sys.argv=oldArgv[:]

garbage=[]

def GetLimitFromTree(inputFile,xsec=False):
    ''' Get Limit Histo from Combine tree'''

    ## Make Limit plot
    fInput= ROOT.TFile.Open(inputFile)

    if fInput == None:
        print "**** ERROR ****"
        print " file ",f,"does not exist"
        print "***************"

    limitTree = fInput.Get("limit")
    if limitTree == None:
        print "**** ERROR ****"
        print " limit tree not present in file",f
        print "***************"
    
    data    = []
    
    ## loop over the entries and figure out if they are median, 1s/2s or observed    
    for iEntry in range(0,limitTree.GetEntries()):
        limitTree.GetEntry(iEntry)
        mh = limitTree.mh
        l  = limitTree.limit
        if opts.pval: l = ROOT.RooStats.PValueToSignificance(limitTree.limit)
        type= 0

        #print     "DEBUG",inputFile, mh, l,q
        if abs(mh-125.) >0.01 : 
            print "Ignoring mh=",mh
            continue
            
        data.append( (mh,l) ) 

    data.sort()
    
    return  data[0][1]

c=ROOT.TCanvas("c","canvas",800,800)

c.SetTopMargin(0.10);
c.SetBottomMargin(0.15);
c.SetLeftMargin(0.15);
c.SetRightMargin(0.05);


nCats=len(args)

maxL=5

dummy = ROOT.TH2F("dummy","Significance per Category",20,0.,maxL,nCats,1-0.5,nCats+0.5);
dummy.SetStats(0);
ci = ROOT.TColor.GetColor("#00ff00");
dummy.SetFillColor(ci);

for ic,cat in enumerate(args):
    dummy.GetYaxis().SetBinLabel(nCats-ic,"cat%d"%ic);

dummy.GetXaxis().SetTickLength(0.01);
dummy.GetYaxis().SetTickLength(0);
dummy.GetXaxis().SetTitle("Significance");
dummy.GetXaxis().SetNdivisions(510);
dummy.GetXaxis().SetLabelFont(42);
dummy.GetXaxis().SetLabelSize(0.045);
dummy.GetXaxis().SetTitleSize(0.045);
dummy.GetXaxis().SetTitleOffset(0.95);
dummy.GetXaxis().SetTitleFont(42);
dummy.GetYaxis().SetNdivisions(510);
dummy.GetYaxis().SetLabelSize(0.035);
dummy.GetYaxis().SetTitleSize(0.045);
dummy.GetYaxis().SetTitleOffset(1.1);
dummy.GetYaxis().SetTitleFont(42);
dummy.GetZaxis().SetLabelFont(42);
dummy.GetZaxis().SetLabelSize(0.035);
dummy.GetZaxis().SetTitleSize(0.035);
dummy.GetZaxis().SetTitleFont(42);
dummy.Draw("");
#sigYields[(cat,proc)] = ea * config.lumi() * config.xsec(proc) *config.br() # proc+"_HToMuMu_M%d" 
width = 0.34

if opts.all:
    dummy.GetYaxis().SetBinLabel(1,"Combined")
    l=ROOT.TGraph()
    l.SetLineColor(ROOT.kBlack)
    l.SetPoint(0,0,1.5)
    l.SetPoint(1,16,1.5)
    l.Draw("L SAME")
    garbage.extend([l])


for ic,cat in enumerate(args):
    S=0.0
    print " ** Cat=",ic,"==",cat
    ybin = nCats-ic;
    ybinmin = ybin-width;
    ybinmax = ybin+width;

    if '=' in cat: 
        label=cat.split('=')[0]
        cat=cat.split('=')[1]
        dummy.GetYaxis().SetBinLabel(nCats-ic,label)

    if opts.unblind or ',' in cat:
        fobs=cat.split(',')[0]
        fexp=cat.split(',')[1]
    else:
        fexp=cat[:]

    obs = GetLimitFromTree(fobs) if opts.unblind else 0.
    exp = GetLimitFromTree(fexp)

    if opts.unblind:
        marker = ROOT.TGraphAsymmErrors()
    else:
        marker = ROOT.TGraph()
    marker2 = ROOT.TGraph()

    marker.SetMarkerStyle(21)
    marker.SetMarkerColor(ROOT.kBlack)
    marker.SetPoint(0,exp,ybin)

    if opts.unblind:
        marker.SetPointError(0,0,0,width,width)
        marker.SetLineColor(ROOT.kBlack)
        marker.SetLineWidth(2)
        marker.SetLineStyle(2)
        marker.SetMarkerSize(0.)
        marker.SetMarkerStyle(0)

        marker2.SetMarkerStyle(21)
        marker2.SetMarkerColor(ROOT.kBlack)
        marker2.SetPoint(0,obs,ybin)
    
    pave1=ROOT.TPave(0,ybinmin,min(exp,maxL),ybinmax)

    if opts.style==0: pave1.SetFillColor(ROOT.kRed-9)
    elif opts.style==1: pave1.SetFillColor(ROOT.kBlue-9)
    else : pave1.SetFillColor(ROOT.kGray)

    pave1.Draw("SAME")
    garbage.extend([pave1])

    txtmin,txtmax=0.001,2.5
    #if opts.all and ic ==nCats-1:
    #    txtmin,txtmax=5,13
    pavetext = ROOT.TPaveText(txtmin,ybinmin,txtmax,ybinmax);
    if opts.unblind:
        pavetext.AddText("%.2f (%.2f)"%(obs,exp))
    else:
        pavetext.AddText("exp=%.2f"%exp)
    pavetext.SetTextColor(ROOT.kBlack);
    pavetext.SetTextFont(43);
    pavetext.SetTextSize(18);
    pavetext.SetTextAlign(31);
    pavetext.SetFillStyle(0);
    pavetext.SetFillColor(0);
    pavetext.SetLineColor(0);
    pavetext.SetBorderSize(0);

    if opts.unblind:
        marker.Draw("PE SAME") ## exp
        marker2.Draw("P SAME") ##obs
    else:
        marker.Draw("P SAME")

    pavetext.Draw("SAME")
    garbage.extend([marker,marker2,pavetext])

l = ROOT.TLatex()
l.SetNDC()
l.SetTextSize(0.05)
l.SetTextFont(42)
l.SetTextAlign(31) #inside
xcms,ycms= 0.9,.18 # inside
l.DrawLatex(xcms,ycms,"#bf{CMS} #scale[0.75]{#it{Preliminary}}")

l.SetTextSize(0.03)
l.SetTextAlign(31)
l.DrawLatex(0.89+0.05,.91,opts.lumi+" fb^{-1} (13 TeV)")

c.Modify()
c.Update()

if not opts.batch: raw_input("ok?")
c.SaveAs(opts.outname)
c.SaveAs(re.sub('pdf','png',opts.outname))
c.SaveAs(re.sub('pdf','root',opts.outname))

