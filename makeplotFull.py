import ROOT as R
import os, sys, glob
R.gROOT.SetBatch(R.kTRUE)

def make_plot_sig(path):
    canvas = R.TCanvas("c1","c1", 500, 600)
    canvas.SetCanvasSize(500, 600)
    canvas.SetRightMargin(.05)
    canvas.SetLeftMargin(.10)
    sigNames = ["ggH", "qqH", "WH", "ZH", "ttH"]
    cat = path.split("_cat")[1].split(".root")[0]
    rfile = R.TFile(path)
    w = rfile.Get("w")
    x = w.var("mass")

    for sig in sigNames:
        xf = x.frame()
        xf.GetXaxis().SetTitle("M(\mu\mu)")
        xf.SetTitle("{} cat {}".format(sig,cat))
        data = w.data("{}_M125_cat{}_data".format(sig,cat))
        pdf = w.pdf("DoubleCB_{}_cat{}".format(sig,cat))
        data.plotOn(xf, R.RooFit.Binning(80,110,150))
        data.plotOn(xf, R.RooFit.Invisible())
        pdf.plotOn(xf)
        xf.Draw()
        canvas.SaveAs("fit_results/plots/sig_fit_{}_cat{}.pdf".format(sig,cat))
    del w

def make_plot_sig_interpolate(path):
    canvas = R.TCanvas("c1","c1", 500, 600)
    canvas.SetCanvasSize(500, 600)
    canvas.SetRightMargin(.05)
    canvas.SetLeftMargin(.13)
    canvas.SetTopMargin(.05)
    sigNames = ["ggH", "qqH", "wH", "zH", "ttH"]
    cat = path.split("_cat")[1].split(".root")[0]
    rfile = R.TFile(path)
    w = rfile.Get("w")
    x = w.var("mass")
    mh = w.var("MH")

    for sig in sigNames:
        leg = R.TLegend(0.6,0.6,0.89,0.84)
        leg.SetFillColor(0)
        leg.SetLineColor(0)

        xf = x.frame()
        xf.GetXaxis().SetTitle("M(\mu\mu)")
        xf.SetTitle("")
        xf.GetYaxis().SetMaxDigits(3)
        data = w.data("{}_M125_cat{}_data".format(sig,cat))
        pdf = w.pdf("DoubleCB_{}_cat{}".format(sig,cat))
        # data.plotOn(xf, R.RooFit.Invisible())
        data.plotOn(xf,R.RooFit.Binning(80,110,150))#, R.RooFit.Invisible())
        datLeg = xf.getObject(int(xf.numItems()-1))
        leg.AddEntry(datLeg, "{} cat {}".format(sig, cat),"P")
        
        mh.setVal(125)
        pdf.plotOn(xf)#, R.RooFit.LineColor(R.kRed))

        norm = w.function("{}_cat{}_norm_spline".format(sig,cat))
        
        for imh in range(120,125) + range(126,131):
            mh.setVal(imh)
            inorm = norm.getVal()

            pdf.plotOn(xf, R.RooFit.Normalization(inorm, 2), R.RooFit.LineStyle(R.kDashed), R.RooFit.LineColor(R.kBlue), R.RooFit.LineWidth(2))

        xf.Draw()
        leg.Draw()
        canvas.SaveAs("fit_results/plots/sig_fit_interp_{}_cat{}.pdf".format(sig,cat))

        del xf
        del leg
    del w

def getBkgPdfTitle(pdfName):

    if pdfName.startswith("bwzred"):
        return "BWZRedux"
    elif pdfName.startswith("bwzgamma"):
        return "BWZGamma"
    elif pdfName.startswith("bwz"):
        return "BWZ"
    elif pdfName.startswith("bern"):
        return "Bernstein ord-{}".format(pdfName.split("_ord")[1])
    elif pdfName.startswith("expser"):
        return "Exponential ord-{}".format(pdfName.split("_ord")[1])
    elif pdfName.startswith("powser"):
        return "Power ord-{}".format(pdfName.split("_ord")[1])

def make_plot_bkg(path):
    canvas = R.TCanvas("c1","c1",500,600)
    canvas.SetCanvasSize(500, 600)
    canvas.cd()
    pad1 = R.TPad("pad1", "pad1", 0, 0.24, 1, 1.0)
    pad1.SetLeftMargin(.10)
    pad1.SetRightMargin(.05)
    pad1.SetBottomMargin(0.05)
    pad1.SetTopMargin(.05)

    pad1.SetTicks(1,1)
    pad1.Draw()
    canvas.cd()
    pad2 = R.TPad("pad2", "pad2", 0, 0, 1, 0.24)
    pad2.Draw()
    pad2.cd()
    pad2.SetRightMargin(.05)
    pad2.SetLeftMargin(.10)
    pad2.SetTopMargin(.03)
    pad2.SetBottomMargin(0.25)

    leg = R.TLegend(0.6,0.6,0.89,0.84)
    leg.SetFillColor(0)
    leg.SetLineColor(0)
    
    cat = path.split("_cat")[1].split(".root")[0]
    rfile = R.TFile(path)
    w = rfile.Get("w")
    x = w.var("mass")

    data = w.data("data_cat{}".format(cat))
    pdf = w.pdf("bkg_cat{}".format(cat))

    xf = x.frame()
    xf.GetXaxis().SetTitle("")
    xf.GetYaxis().SetMaxDigits(3)
    xf.GetYaxis().SetTitleSize(14)
    xf.GetYaxis().SetTitleFont(43)
    xf.GetYaxis().SetTitleOffset(2.0)
    xf.GetXaxis().SetLabelSize(0)

    xf.SetTitle("")
    data.plotOn(xf,R.RooFit.Binning(80,110,150))

    data.plotOn(xf, R.RooFit.Invisible())
    
    datLeg = xf.getObject(int(xf.numItems()-1))
    leg.AddEntry(datLeg, "Data - Run II cat {}".format(cat),"P")

    colors = [R.kBlue, R.kRed, R.kRed+2, R.kCyan, R.kGreen, R.kMagenta+2]
    bwzHist = pdf.getPdf(1).createHistogram("{}_hist".format(pdf.getPdf(1).GetName()),w.var("mass"))

    pad2.cd()

    for i in range(0,6):
        ipdf = pdf.getPdf(i)
        ipdf.plotOn(xf, R.RooFit.LineColor(colors[i]), R.RooFit.LineStyle(R.kSolid))
        pdfLeg = xf.getObject(int(xf.numItems()-1))
        legName = ipdf.GetName().split("_cat{}".format(cat))[0]
        legName = getBkgPdfTitle(legName)
        leg.AddEntry(pdfLeg,legName,"L"); 
        hratio = ipdf.createHistogram("{}_hist".format(ipdf.GetName()),w.var("mass"))
        hratio.Divide(bwzHist)
        hratio.SetLineColor(colors[i])
        hratio.SetLineWidth(2)

        hratio.SetStats(R.kFALSE)
        hratio.SetTitle("")
        hratio.GetYaxis().SetTitle("Ratio PDFs")
        hratio.GetXaxis().SetTitle("M(\mu\mu)")
        hratio.GetYaxis().SetTitleSize(14)
        hratio.GetYaxis().SetTitleFont(43)
        hratio.GetYaxis().SetTitleOffset(2.0)
        hratio.GetYaxis().SetLabelFont(43)
        hratio.GetYaxis().SetLabelSize(12)
        hratio.GetXaxis().SetTitleSize(12)
        hratio.GetXaxis().SetTitleFont(43)
        hratio.GetXaxis().SetTitleOffset(4.4)
        hratio.GetXaxis().SetLabelFont(43)
        hratio.GetXaxis().SetLabelOffset(.04)
        hratio.GetXaxis().SetLabelSize(12)
        hratio.SetMaximum(1.04)
        hratio.SetMinimum(0.96)
        hratio.GetYaxis().SetNdivisions(6)
        hratio.Draw("same")

    
    pad1.cd()
    xf.Draw()
    leg.Draw()
    R.gPad.Modified()
    canvas.Draw()

    canvas.SaveAs("fit_results/plots/bkg_fit_cat{}.pdf".format(cat))
    del w

def make_plot_bkg_core(path):
    canvas = R.TCanvas("c1","c1",500,600)
    canvas.SetCanvasSize(500, 600)
    canvas.cd()
    pad1 = R.TPad("pad1", "pad1", 0, 0.24, 1, 1.0)
    pad1.SetLeftMargin(.10)
    pad1.SetRightMargin(.05)
    pad1.SetBottomMargin(0.05)
    pad1.SetTopMargin(.05)

    pad1.SetTicks(1,1)
    pad1.Draw()
    canvas.cd()
    pad2 = R.TPad("pad2", "pad2", 0, 0, 1, 0.24)
    pad2.Draw()
    pad2.cd()
    pad2.SetRightMargin(.05)
    pad2.SetLeftMargin(.10)
    pad2.SetTopMargin(.03)
    pad2.SetBottomMargin(0.25)
    pad2.SetGridy()
    leg = R.TLegend(0.6,0.7,0.89,0.94)
    leg.SetFillColor(0)
    leg.SetLineColor(0)
    
    cat = path.split("_cat")[1].split(".root")[0]
    rfile = R.TFile(path)
    w = rfile.Get("w")
    x = w.var("mass")

    data = w.data("transfer_cat{}".format(cat))
    pdf = w.pdf("bwzr_transfer_cat{}".format(cat))

    xf = x.frame()
    xf.GetYaxis().SetTitle("a.u.")
    xf.GetXaxis().SetTitle("")
    xf.GetYaxis().SetMaxDigits(3)
    xf.GetYaxis().SetTitleSize(14)
    xf.GetYaxis().SetTitleFont(43)
    xf.GetYaxis().SetTitleOffset(2.0)
    xf.GetXaxis().SetLabelSize(0)
    userRange = (7e-3, 13e-3) if int(cat) < 3 else (6e-3,18e-3)
    xf.SetTitle("")
    data.plotOn(xf,R.RooFit.Binning(100,110,150))

    # data.plotOn(xf, R.RooFit.Invisible())
    datLeg = xf.getObject(int(xf.numItems()-1))
    leg.AddEntry(datLeg, "Shape Modifier - Cat {}".format(cat),"P")

    pdf.plotOn(xf, R.RooFit.LineColor(R.kRed), R.RooFit.LineStyle(R.kSolid))
    pdfLeg = xf.getObject(int(xf.numItems()-1))
    leg.AddEntry(pdfLeg, "Polynomial Fit","L")

    xf.GetYaxis().SetRangeUser(userRange[0],userRange[1])

    # colors = [R.kBlue, R.kRed, R.kGreen]
    # bwzHist = pdf.getPdf(1).createHistogram("{}_hist".format(pdf.getPdf(1).GetName()),w.var("mass"))

    pad2.cd()
    dataHist = data.createHistogram("data_hist", w.var("mass"), R.RooFit.Binning(100,110, 150))
    pdfHist = pdf.createHistogram("pdf_hist", w.var("mass"), R.RooFit.Binning(100,110, 150))

    hratio = dataHist.Clone()
    for i in range(1,hratio.GetNbinsX()+1):
        hratio.SetBinContent(i,dataHist.GetBinContent(i)/pdfHist.GetBinContent(i))
        hratio.SetBinError(i, dataHist.GetBinError(i)/dataHist.GetBinContent(i))
    # hratio.Divide(pdfHist)

    hratio.SetStats(R.kFALSE)
    hratio.SetTitle("")
    hratio.GetYaxis().SetTitle("Data / Pred")
    hratio.GetXaxis().SetTitle("M(\mu\mu)")
    hratio.GetYaxis().SetTitleSize(14)
    hratio.GetYaxis().SetTitleFont(43)
    hratio.GetYaxis().SetTitleOffset(2.0)
    hratio.GetYaxis().SetLabelFont(43)
    hratio.GetYaxis().SetLabelSize(12)
    hratio.GetXaxis().SetTitleSize(12)
    hratio.GetXaxis().SetTitleFont(43)
    hratio.GetXaxis().SetTitleOffset(4.4)
    hratio.GetXaxis().SetLabelFont(43)
    hratio.GetXaxis().SetLabelOffset(.04)
    hratio.GetXaxis().SetLabelSize(12)
    hratio.SetMaximum(1.1)
    hratio.SetMinimum(0.9)
    hratio.SetMarkerStyle(20)
    hratio.SetMarkerSize(0.7)
    hratio.SetLineColor(R.kBlack)
    hratio.GetYaxis().SetNdivisions(4)
    hratio.Draw("E1")

    
    pad1.cd()
    xf.Draw()
    leg.Draw()
    R.gPad.Modified()
    canvas.Draw()

    canvas.SaveAs("fit_results/plots/bkg_fit_cat{}_transfer.pdf".format(cat))
    del w
    
bkgFiles = glob.glob("workspaces_full_sixPDFs/workspace_bkg_cat*.root")
sigFiles = glob.glob("workspaces_full/workspace_sig_cat*.root")
bkgFilesFinal = glob.glob("workspaces_full/workspace_bkg_cat*.root")


for b in bkgFiles:
    make_plot_bkg(b)
for b in bkgFilesFinal:
    make_plot_bkg_core(b)
for s in sigFiles:
    make_plot_sig(s)
    make_plot_sig_interpolate(s)
