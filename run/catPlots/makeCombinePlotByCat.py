import os,sys
from array import array
import re,math
from subprocess import call
from optparse import OptionParser, OptionGroup

usage="program [label=]higss*"
parser=OptionParser()
parser.add_option("-b","--batch",dest="batch",default=False,action="store_true")
parser.add_option("-u","--unblind",dest="unblind",default=False,action="store_true")
#parser.add_option("-i","--input",type='string',help="Input ROOT file. [%default]", default="Hmumu.root")
parser.add_option("-a","--all",action='store_true',help="All [%default]", default=False)
parser.add_option("","--log",action='store_true',help="All [%default]", default=False)
parser.add_option("","--xmax",type='float',help="xmax [%default]", default=20.)
parser.add_option("-l","--lumi",help="Luminosity [%default]", default="137")
parser.add_option("","--smregex",dest='sm',help="SM regex [%default]",action='append', default=[])
parser.add_option("-o","--outname",help="outname [%default]", default="./limitPerCat.pdf")
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
		print " file ",inputFile,"does not exist"
		print "***************"

	limitTree = fInput.Get("limit")
	if limitTree == None:
		print "**** ERROR ****"
		print " limit tree not present in file",inputFile
		print "***************"
	
	#Expected
	obs=ROOT.TGraphAsymmErrors()
	obs.SetName("obs")
	
	exp=ROOT.TGraphAsymmErrors()
	exp.SetName("exp")
	
	oneSigma=ROOT.TGraphAsymmErrors()
	oneSigma.SetName("oneSigma")
	
	twoSigma=ROOT.TGraphAsymmErrors()
	twoSigma.SetName("twoSigma")
	
	data    = []
	median 	= []
	Up 	= []
	Up2 	= []
	Down 	= []
	Down2 	= []
	
	## loop over the entries and figure out if they are median, 1s/2s or observed	
	for iEntry in range(0,limitTree.GetEntries()):
		limitTree.GetEntry(iEntry)
		mh = limitTree.mh
		l  = limitTree.limit
		q  = limitTree.quantileExpected
		type= 0

		#print 	"DEBUG",inputFile, mh, l,q
		if abs(mh-125.) >0.01 : 
		    print "Ignoring mh=",mh
		    continue
			
		if abs(q-0.5)<1.e-5 : 
			#exp.SetPoint(g.GetN(), mh,l ) 
			median.append(  (mh,l) ) 
		
		if abs(q -0.0250000) <1e-5:  ## 95% 2sDown
			type=-2
			Down2.append( (mh,l) )
		if abs(q-0.1599999) <1e-5 :  ## 68% 1sDown
			type=-1
			Down.append( (mh,l) )
		if abs(q-0.8399999) <1e-5 :  ## 68% 1sUp
			type=1
			Up.append( (mh,l) )
		if abs(q-0.9750000) <1e-5 :  ## 95% 2sUp
			type=2
			Up2.append( (mh,l) )
		if q <-.5: # -1
			data.append( (mh,l) ) 
	
	if len(Up2) != len(Down2) :print "[ERROR] Count 2s"
	if len(Up) != len(Down) :print "[ERROR] Count 1s"
	
	## sort median, Up Up2 Down Down2 data with mh
	median.sort()
	Up.sort()
	Up2.sort()
	Down.sort()
	Down2.sort()
	data.sort()
    
	return  median[0][1], Up[0][1], Down[0][1], Up2[0][1],Down2[0][1],data[0][1]


c=ROOT.TCanvas("c","canvas",800,800)
c.cd()

c.SetTopMargin(0.10);
c.SetBottomMargin(0.15);
c.SetLeftMargin(0.15);
c.SetRightMargin(0.05);

if opts.log: c.SetLogx()


nCats=len(args)

#maxL=31.
maxL=opts.xmax
minL=0. if not opts.log else 0.1

dummy = ROOT.TH2F("dummy","Limits per Category",20,minL,maxL,nCats,1-0.5,nCats+0.5);
dummy.SetStats(0);
ci = ROOT.TColor.GetColor("#00ff00");
dummy.SetFillColor(ci);

for ic,cat in enumerate(args):
    dummy.GetYaxis().SetBinLabel(nCats-ic,"cat%d"%ic);

dummy.GetXaxis().SetTickLength(0.01);
dummy.GetYaxis().SetTickLength(0);
dummy.GetXaxis().SetTitle("Upper Limit (95%CL)");
dummy.GetXaxis().SetNdivisions(510);
dummy.GetXaxis().SetLabelFont(42);
dummy.GetXaxis().SetLabelSize(0.045);
dummy.GetXaxis().SetTitleSize(0.045);
dummy.GetXaxis().SetTitleOffset(1.1);
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

    exp,up,down,up2,down2,obs = GetLimitFromTree(cat)
    if opts.unblind:
        marker = ROOT.TGraphAsymmErrors()
    else:
        marker = ROOT.TGraph()
    marker2 = ROOT.TGraph()

    if len(opts.sm)>0:
        #fnamesm=re.sub(opts.sm.split(',')[0],opts.sm.split(',')[1],cat)
        fnamesm=cat
        for x in opts.sm: fnamesm=re.sub(x.split(',')[0],x.split(',')[1],fnamesm)
        print "[INFO] taking SM value for ",cat,"from",fnamesm
        exp_sm,up_sm,down_sm,up2_sm,down2_sm,obs_sm= GetLimitFromTree(fnamesm)
        marker_sm=ROOT.TGraphAsymmErrors()
        marker_sm.SetPoint(0,obs_sm,ybin)
        marker_sm.SetPointError(0,0,0,width,width)
        marker_sm.SetLineColor(ROOT.kBlue)
        marker_sm.SetLineWidth(2)
        marker_sm.SetMarkerSize(0.)
        marker_sm.SetMarkerStyle(0)
        garbage.extend([marker_sm])

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
    
    pave1 = ROOT.TPave(down,ybinmin,min(up,maxL),ybinmax);
    pave2 = ROOT.TPave(down2,ybinmin,min(up2,maxL),ybinmax);
    pave2.SetFillColor(ROOT.kOrange)
    pave1.SetFillColor(ROOT.kGreen)
    garbage.extend([pave1,pave2])

    # txtmin,txtmax=0.001,10
    txtmin,txtmax=5,11.5
    if opts.log: txtmin,txtmax=0.08,50.
    if opts.all and ic ==nCats-1:
        txtmin,txtmax=5,11.5
        if opts.log: txtmin,txtmax=0.08,50.
    pavetext = ROOT.TPaveText(txtmin,ybinmin,txtmax,ybinmax);
    if opts.unblind:
        pavetext.AddText("%.2f (%.2f)"%(obs,exp))
    else:
        pavetext.AddText("median=%.2f"%exp)
    pavetext.SetTextColor(ROOT.kBlack);
    pavetext.SetTextFont(43);
    pavetext.SetTextSize(18);
    pavetext.SetTextAlign(31);
    pavetext.SetFillStyle(0);
    pavetext.SetFillColor(0);
    pavetext.SetLineColor(0);
    pavetext.SetBorderSize(0);

    pave2.Draw("SAME")
    pave1.Draw("SAME")
    if opts.unblind:
        marker.Draw("PE SAME")
        marker2.Draw("P SAME")
    else:
        marker.Draw("P SAME")

    if len(opts.sm) >0:
        marker_sm.Draw("P SAME")
    pavetext.Draw("SAME")
    garbage.extend([marker,marker2,pavetext])

l = ROOT.TLatex()
l.SetNDC()
l.SetTextSize(0.05)
l.SetTextFont(42)
l.SetTextAlign(31) #inside
xcms,ycms= 0.93,.17 # inside
l.DrawLatex(xcms,ycms,"#bf{CMS} #scale[0.75]{#it{Preliminary}}")

l.SetTextSize(0.03)
l.SetTextAlign(31)
l.DrawLatex(0.89+0.05,.91,opts.lumi+" fb^{-1} (13 TeV)")

if True:  #new legend version
    ltx = ROOT.TLatex()
    garbage.append(ltx)
    ltx . SetNDC()
    ltx . SetTextSize(0.028)
    ltx . SetTextFont(42)
    ltx . SetTextAlign(12)
    xmin = 0.63 #was 0.61
    ymax = .87
    textSep = 0.03
    delta = 0.045
    entryDelta = 0.06

    dataPoint =  ROOT.TMarker(xmin,ymax,21)
    dataPoint.SetMarkerColor(ROOT.kBlack)
    dataPoint.SetNDC()
    #dataLine =  ROOT.TLine(xmin, ymax-delta/2. ,xmin, ymax + delta/2.)
    #dataLine.SetNDC()
    #dataLine.SetLineColor(ROOT.kBlack)
    #dataLine.SetLineWidth(1)
    #dataLine2 =  ROOT.TLine(xmin-0.003, ymax-delta/2. ,xmin+0.003, ymax - delta/2.)
    #dataLine2.SetNDC()
    #dataLine3 =  ROOT.TLine(xmin-0.003, ymax+delta/2. ,xmin+0.003, ymax + delta/2.)
    #dataLine3.SetNDC()
    garbage += [dataPoint]
    #garbage += [dataPoint,dataLine,dataLine2,dataLine3]
    ## Draw data
    dataPoint.Draw("SAME")
    #dataLine.Draw("SAME")
    #dataLine2.Draw("SAME")
    #dataLine3.Draw("SAME")
    ltx.DrawLatex(xmin+ textSep,ymax,"Observed")

    ## B Fit: Red 2, dashed
    y_b = ymax - entryDelta
    b = ROOT.TLine(xmin,y_b -delta/2., xmin,y_b+delta/2.)
    b.SetNDC()
    b.SetLineColor(ROOT.kBlack)
    b.SetLineStyle(2)
    b.SetLineWidth(1)
    garbage . extend([b])
    b.Draw("SAME")
    ltx.DrawLatex(xmin +textSep,y_b,"Expected #pm 1 s.d. (2 s.d.)")

    oneSigma = ROOT.TPave(xmin-delta*3/10.,y_b-delta/2.,xmin+delta*3/10.,y_b+delta/2.,0,"NDC")
    oneSigma.SetFillColor(ROOT.kGreen+1)
    twoSigma = ROOT.TPave(xmin-delta*6/10.,y_b-delta/2.,xmin+delta*6/10.,y_b+delta/2.,0,"NDC")
    twoSigma.SetFillColor(ROOT.kOrange)
    twoSigma.Draw("SAME")
    oneSigma.Draw("SAME")
    b.Draw("SAME")

    ## SB Fit: Red 2, solid + 1s +2s
    if len(opts.sm) >0:
        y_sb = ymax - 2*entryDelta
        sb = ROOT.TLine(xmin,y_sb -delta/2., xmin,y_sb+delta/2.)
        sb.SetNDC()
        sb.SetLineColor(ROOT.kBlue)
        #sb.SetLineStyle(2 if opts.bband else 1)
        sb.SetLineWidth(2)
        sb.Draw("SAME")
        ltx.DrawLatex(xmin +textSep,y_sb,"Expected SM Higgs")
        garbage . extend([sb,oneSigma,twoSigma])


c.Modify()
c.Update()

if not opts.batch: raw_input("ok?")
c.SaveAs(opts.outname)
c.SaveAs(re.sub('pdf','png',opts.outname))
c.SaveAs(re.sub('pdf','root',opts.outname))


