import ROOT as R
from array import array
import os, sys, glob
import fit_functions
import json

R.gROOT.SetBatch(R.kTRUE)

doBkg = False
doSig = False
doMultiPDF = False
doCorePDF = True

rfile = R.TFile("histosFullRun2.root")
corePDF_results = {}
corePDF_results["bwzrCore"] = {}
corePDF_results["expCore"] = {}
corePDF_results["fewzCore"] = {}

bkg_stats = []
bkg_fit_results = {}


if doCorePDF:
    dataStack = R.THStack("full_ggh_data","")
    for cat in range(0, 5):
        prefix = "cat{}".format(cat)
        data_histoname = "data_{}_fullRun2".format(prefix)
        data_histogram = rfile.Get(data_histoname)
        dataStack.Add(data_histogram)

    dataStackSum = dataStack.GetStack().Last()

    wt = R.RooWorkspace("wt", False)

    mass = R.RooRealVar("mass","invariant mass",125.0,110.0,150.0)

    fullDataSet = R.RooDataHist("core_data","core_data",R.RooArgList(mass),dataStackSum)
    fullDataName = fullDataSet.GetName()
    getattr(wt, 'import')(fullDataSet)

    stat, bwzCore = fit_functions.getBWZReduxCore("core", wt, fullDataName)
    corePDF_results["bwzrCore"]["status"] = stat

    stat, expCore = fit_functions.getExpSeriesCore("core", wt, fullDataName)
    corePDF_results["expCore"]["status"] = stat

    stat, fewzCore = fit_functions.getFEWZCore("core", wt, fullDataName)
    corePDF_results["fewzCore"]["status"] = stat

    core_norm = R.RooRealVar("bkg_core_norm".format(prefix), "bkg_core_norm".format(prefix), fullDataSet.sumEntries(), -float('inf'), float('inf'))
    core_norm.setConstant()

    chi2, pval, _, _ = fit_functions.getGoodnessOfFit(wt, bwzCore.GetName(), fullDataName, fullDataSet.sumEntries())
    corePDF_results["bwzrCore"]["chi2"] = chi2
    corePDF_results["bwzrCore"]["pvalue"] = pval

    chi2, pval, _, _ = fit_functions.getGoodnessOfFit(wt, expCore.GetName(), fullDataName, fullDataSet.sumEntries())
    corePDF_results["expCore"]["chi2"] = chi2
    corePDF_results["expCore"]["pvalue"] = pval

    chi2, pval, _, _ = fit_functions.getGoodnessOfFit(wt, fewzCore.GetName(), fullDataName, fullDataSet.sumEntries())
    corePDF_results["fewzCore"]["chi2"] = chi2
    corePDF_results["fewzCore"]["pvalue"] = pval

    for cat in range(0,5):
        w = R.RooWorkspace("w", False)
        getattr(w, 'import')(wt.pdf(bwzCore.GetName()), R.RooFit.RecycleConflictNodes())
        getattr(w, 'import')(wt.pdf(expCore.GetName()), R.RooFit.RecycleConflictNodes())
        prefix = "cat{}".format(cat)

        corePDF_results["transfer_{}".format(prefix)] = {}

        data_histoname = "data_{}_fullRun2".format(prefix)
        data_histogram = rfile.Get(data_histoname)
        
        transferHist = data_histogram.Clone()
        transferHist.Divide(dataStackSum)
        transferHist.Scale( 1 / transferHist.Integral())

        transferDataSet = R.RooDataHist("transfer_{}".format(prefix),"transfer_{}".format(prefix),R.RooArgList(mass),transferHist)
        transferDataName = transferDataSet.GetName()
        getattr(wt, 'import')(transferDataSet)
        getattr(w, 'import')(transferDataSet)

        chebyOrder = 3 if cat < 1 else 2 
        stat, bwzrCheby, expCheby, fewzCheby = fit_functions.getTransfer(prefix, wt, chebyOrder, transferDataName)
        corePDF_results["transfer_{}".format(prefix)]["status"] = stat

        chi2, pval, _, _ = fit_functions.getGoodnessOfFit(wt, bwzrCheby.GetName(), transferDataName, transferDataSet.sumEntries())
        
        corePDF_results["transfer_{}".format(prefix)]["chi2"] = chi2
        corePDF_results["transfer_{}".format(prefix)]["pvalue"] = pval
        

        corePDFs = R.RooArgList()
        
        coreBWZR = R.RooProdPdf("bkg_bwzred_{}".format(
        prefix), "bkg_bwzred_{}".format(prefix), wt.pdf(bwzCore.GetName()), wt.pdf(bwzrCheby.GetName()))
        
        coreEXP = R.RooProdPdf("bkg_exp_{}".format(prefix), "bkg_exp_{}".format(
        prefix), wt.pdf(expCore.GetName()), wt.pdf(expCheby.GetName()))
        
        coreFEWZ = R.RooProdPdf("bkg_fewz_{}".format(prefix), "bkg_fewz_{}".format(
        prefix), wt.pdf(fewzCore.GetName()), wt.pdf(fewzCheby.GetName()))

        getattr(w, 'import')(coreBWZR, R.RooFit.RecycleConflictNodes())
        getattr(w, 'import')(coreEXP, R.RooFit.RecycleConflictNodes())
        getattr(w, 'import')(coreFEWZ, R.RooFit.RecycleConflictNodes())

        
        corePDFs.add(w.pdf(coreBWZR.GetName()))
        corePDFs.add(w.pdf(coreEXP.GetName()))
        corePDFs.add(w.pdf(coreFEWZ.GetName()))

        pdfIndex = R.RooCategory("corepdf_index", "Index of Core PDF")

        multipdf = R.RooMultiPdf("bkg_{}_pdf".format(
        prefix), "bkg_{}_pdf".format(prefix), pdfIndex, corePDFs)

        multipdf.setCorrectionFactor(0.0)

        cat_dataSet = R.RooDataHist("data_{}".format(prefix),"data_{}".format(prefix),R.RooArgList(mass),data_histogram)
        ndata = cat_dataSet.sumEntries()
        cat_norm = R.RooRealVar("bkg_{}_pdf_norm".format(prefix), "bkg_{}_pdf_norm".format(prefix), ndata, -float('inf'), float('inf'))
    
        getattr(w, 'import')(cat_dataSet)
        getattr(w, 'import')(cat_norm, R.RooFit.RecycleConflictNodes())   
        getattr(w, 'import')(multipdf, R.RooFit.RecycleConflictNodes())
        getattr(w, 'import')(core_norm)

        outfile = R.TFile("workspaces_full/workspace_bkg_{}.root".format(prefix),"recreate")
        w.Write()
    
        del w
    del wt

    

if doBkg:
    for cat in range(0, 5):
        prefix = "cat{}".format(cat)

        bkg_fit_results[prefix] = {}

        data_histoname = "data_{}_fullRun2".format(prefix)

        data_histogram = rfile.Get(data_histoname)
        # Initialize workspace and the observable variable
        w = R.RooWorkspace("w", False)

        mass = R.RooRealVar("mass","invariant mass",125.0,110.0,150.0)
        dataSet = R.RooDataHist("data_{}".format(prefix),"data",R.RooArgList(mass),data_histogram)
        getattr(w, 'import')(dataSet)

        dataName = dataSet.GetName()

        # mass.setRange('sideband_low', 110, 120)
        # mass.setRange('sideband_high', 130, 150)
        
        bkg_funcs = []
        ndata = dataSet.sumEntries()

        if doMultiPDF:
            print("### FITTING BWZ")
            stat, bwz = fit_functions.getBWZ(prefix, w, dataName) 
            bkg_funcs.append(bwz)
            bkg_stats.append(stat)

        print("### FITTING BWZRedux")
        stat, bwzr = fit_functions.getBWZRedux(prefix, w, dataName)
        bkg_funcs.append(bwzr)
        bkg_stats.append(stat)

        if doMultiPDF:
            print("### FITTING BWZGAMMA")
            stat, bwzg = fit_functions.getBWZGamma(prefix, w, dataName)
            bkg_funcs.append(bwzg)
            bkg_stats.append(stat)

            print("### FITTING BERNSTEIN POLYNOMIAL")
            stat, bern = fit_functions.fTest(prefix, "bern", w, dataName)
            bkg_funcs.append(bern)
            bkg_stats.append(stat)

            print("### FITTING EXPONENTIAL SERIES")
            stat, expSeries = fit_functions.fTest(prefix, "exp", w, dataName)
            bkg_funcs.append(expSeries)
            bkg_stats.append(stat)

            print("### FITTING POWER SERIES")
            stat, powSeries = fit_functions.fTest(prefix, "pow", w, dataName)
            bkg_funcs.append(powSeries)
            bkg_stats.append(stat)

        bkgPdfs = R.RooArgList()
        resids = []
        pulls = []
        for bkg_func in bkg_funcs:
            chi2, pval, resid, pull = fit_functions.getGoodnessOfFit(w, bkg_func.GetName(), dataName, ndata)
            shortName = bkg_func.GetName().split("_{}".format(prefix))[0]
            bkg_fit_results[prefix][shortName] = {}
            bkg_fit_results[prefix][shortName]["chi2"] = chi2
            bkg_fit_results[prefix][shortName]["pvalue"] = pval

            resid.SetNameTitle("resid_bkg_{}".format(shortName),"resid_bkg_{}".format(shortName))
            pull.SetNameTitle("pull_bkg_{}".format(shortName),"pull_bkg_{}".format(shortName))
            resids.append(resid)
            pulls.append(pull)

            bkgPdfs.add(bkg_func)

        if doMultiPDF:
            # pdfIndex = R.RooCategory("pdf_index_{}".format(prefix), "pdf_index_{}".format(prefix))
            pdfIndex = R.RooCategory("pdf_index", "pdf_index")
            multipdf = R.RooMultiPdf("bkg_{}".format(prefix), "bkg_{}".format(prefix) , pdfIndex, bkgPdfs)
            multipdf_norm = R.RooRealVar("bkg_{}_norm".format(prefix), "bkg_{}_norm".format(prefix), ndata, .5 * ndata, 2*ndata)
            getattr(w, 'import')(multipdf, R.RooFit.RecycleConflictNodes()) 
            getattr(w, 'import')(multipdf_norm, R.RooFit.RecycleConflictNodes())   

        else:
            bwzredux_norm = R.RooRealVar("bwzred_{}_norm".format(prefix), "bwzred_{}_norm".format(prefix), ndata, .5 *ndata, 2*ndata)
            getattr(w, 'import')(bwzredux_norm, R.RooFit.RecycleConflictNodes())
            getattr(w, 'import')(bwzr, R.RooFit.RecycleConflictNodes())
                
        if doMultiPDF:
            folder = "workspaces_full_sixPDFs"
        else:
            folder = "workspaces_full"
        outfile = R.TFile("{}/workspace_bkg_{}.root".format(folder, prefix),"recreate")
        w.Write()
        del w

        # outfile2 = R.TFile("pulls/pulls_bkg_{}.root".format(prefix),"recreate")
        # for i in range(len(resids)):
        #     resids[i].Write()
        #     pulls[i].Write()


sig_stats = []

if doSig:
    sigNames = ["ggH", "qqH", "ttH", "wH", "zH"]
    # sig_fit_results = {}
    # make lists for parameter values at different points?
    # fit each model, then create the splines, then create new PDFs and just save them w/out refitting. 
    # each prod mod * cat * param gets a spline... 5*5*5 = 125 splines...?
    mass_splineList = [120, 125, 130]
    MH = R.RooRealVar("MH","Higgs Mass",125, 120,130)
    MH.setVal(125)
    MH.setConstant(R.kTRUE)

    mass = R.RooRealVar("mass","invariant mass",125.0,110.0,150.0)

    for cat in range(0,5):
        catName = "cat{}".format(cat)

        # sig_fit_results[catName] = {}
        outfile = R.TFile("workspaces_full/workspace_sig_cat{}.root".format(cat),"RECREATE")
        w = R.RooWorkspace("w", False)
        

        CMS_hmm_peak = R.RooRealVar("CMS_hmm_peak_cat{}".format(cat), "CMS peak", 0, -5, 5)
        CMS_hmm_sigma = R.RooRealVar("CMS_hmm_sigma_cat{}".format(cat), "CMS sigma",0, -5, 5)

        for prodMode in sigNames:
            # sig_fit_results[catName][prodMode] = {}
            peak_splineList = []
            sigma_splineList = []
            a1_splineList = []
            a2_splineList = []
            n1_splineList = []
            n2_splineList  = []
            norm_splintList = []

            for mass_point in mass_splineList:
                tws = R.RooWorkspace("tws", False)    
                signal_histoname = "{}_{}_{}".format(prodMode, mass_point, catName) 
                # print(hname)
                signal_histogram = rfile.Get(signal_histoname)
                # # Initialize workspace and the observable variable
                dataSet = R.RooDataHist("{}_M{}_{}_data".format(prodMode, mass_point, catName),"data",R.RooArgList(mass),signal_histogram)

                getattr(tws, 'import')(dataSet)
                norm = R.RooRealVar("TDoubleCB_{}_{}_norm".format(prodMode, catName),"norm for {}_{}".format(prodMode, catName), dataSet.sumEntries(), -float('inf'), float('inf'))
                norm_splintList.append(norm.getVal())
            
                peak = R.RooRealVar("TPeak_{}_{}".format(prodMode,catName),"peak {} {}".format(prodMode,catName), mass_point, 115.0, 135.0)
                width = R.RooRealVar("TWidth_{}_{}".format(prodMode,catName),"width {} {}".format(prodMode,catName), 1.8, 1.0, 2.0)

                a1 = R.RooRealVar("a1_{}_{}".format(prodMode,catName),"a1_{}_{} coeff".format(prodMode,catName),1.1,1.0,2.1)
                a2 = R.RooRealVar("a2_{}_{}".format(prodMode,catName),"a2_{}_{} coeff".format(prodMode,catName),1.1,1.0,2.1)
                n1 = R.RooRealVar("n1_{}_{}".format(prodMode,catName),"n1_{}_{} coeff".format(prodMode,catName),2.0,0,5.0)
                n2 = R.RooRealVar("n2_{}_{}".format(prodMode,catName),"n2_{}_{} coeff".format(prodMode,catName),5.0,0,10.0)
            

                sig_model = R.RooDoubleCBFast("TDoubleCB_{}_M{}_{}".format(prodMode,mass_point, catName),"TDouble CB {}_M{}_{}".format(prodMode,mass_point, catName),mass,peak,width,a1,n1,a2,n2)    
                
                # sig_model.fitTo(dataSet,  R.RooFit.Minimizer("Minuit2","minimize"),  R.RooFit.SumW2Error(R.kTRUE))

                # result = sig_model.fitTo(dataSet, R.RooFit.Minimizer("Minuit2","minimize"), R.RooFit.SumW2Error(R.kTRUE))
                result = sig_model.fitTo(tws.data("{}_M{}_{}_data".format(prodMode, mass_point, catName)), R.RooFit.Minimizer("Minuit2","migrad"),  R.RooFit.Save(R.kTRUE), R.RooFit.Strategy(1) , R.RooFit.SumW2Error(R.kTRUE))
                # result = sig_model.fitTo(tws.data("{}_M{}_{}_data".format(prodMode, mass_point, catName)), R.RooFit.Minimizer("Minuit2","migrad"),  R.RooFit.Save(R.kTRUE), R.RooFit.Strategy(1) , R.RooFit.SumW2Error(R.kTRUE))
                
                sig_stats.append(result.status())

                # getattr(tws, 'import')(sig_model, R.RooFit.RecycleConflictNodes())
                
                # if mass_point == 125:
                    # chi2, _,iresid,ipull = fit_functions.getGoodnessOfFit(tws, sig_model.GetName(), dataSet.GetName(), dataSet.sumEntries())
                    # sig_fit_results[catName][prodMode]["chi2"] = chi2
                    # sig_fit_results[catName][prodMode]["pvalue"] = pval

                # sig_resids.append(iresid)
                # sig_pulls.append(ipull)

                peak_splineList.append(peak.getVal())
                sigma_splineList.append(width.getVal())
                a1_splineList.append(a1.getVal())
                a2_splineList.append(a2.getVal())
                n1_splineList.append(n1.getVal())
                n2_splineList.append(n2.getVal())
                
                if mass_point == 125:
                    getattr(w, 'import')(dataSet , R.RooFit.RecycleConflictNodes())
                
                del tws



            # make splines then make PDF. Write PDF to workspace?
            peak_spline = R.RooSpline1D("{}_{}_peak_spline".format(prodMode,catName),"peak {} {} spline".format(prodMode,catName),MH,len(peak_splineList), array("f",mass_splineList), array("f",peak_splineList))
            sigma_spline = R.RooSpline1D("{}_{}_sigma_spline".format(prodMode,catName),"sigma {} {} spline".format(prodMode,catName),MH,len(sigma_splineList), array("f",mass_splineList), array("f",sigma_splineList))
            a1_spline = R.RooSpline1D("{}_{}_a1_spline".format(prodMode,catName),"a1 {} {} spline".format(prodMode,catName),MH,len(a1_splineList), array("f",mass_splineList), array("f",a1_splineList))
            a2_spline = R.RooSpline1D("{}_{}_a2_spline".format(prodMode,catName),"a2 {} {} spline".format(prodMode,catName),MH,len(a2_splineList), array("f",mass_splineList), array("f",a2_splineList))
            n1_spline = R.RooSpline1D("{}_{}_n1_spline".format(prodMode,catName),"n1 {} {} spline".format(prodMode,catName),MH,len(n1_splineList), array("f",mass_splineList), array("f",n1_splineList))
            n2_spline = R.RooSpline1D("{}_{}_n2_spline".format(prodMode,catName),"n2 {} {} spline".format(prodMode,catName),MH,len(n2_splineList), array("f",mass_splineList), array("f",n2_splineList))
            norm_spline = R.RooSpline1D("{}_{}_norm_spline".format(prodMode,catName),"norm {} {} spline".format(prodMode,catName),MH,len(norm_splintList), array("f",mass_splineList), array("f",norm_splintList))

            FinalPeak = R.RooFormulaVar("{}_{}_peak".format(prodMode,catName), "@0*(1+@1)", R.RooArgList(peak_spline,CMS_hmm_peak))
        
            FinalWidth = R.RooFormulaVar("{}_{}_width".format(prodMode,catName),"@0*(1+@1)", R.RooArgList(sigma_spline,CMS_hmm_sigma))

            SignalModel = R.RooDoubleCBFast("DoubleCB_{}_{}".format(prodMode,catName),"Double CB {}_{}".format(prodMode,catName),mass,FinalPeak,FinalWidth,a1_spline,n1_spline,a2_spline,n2_spline)
            FinalNorm = R.RooFormulaVar("DoubleCB_{}_{}_norm".format(prodMode, catName),"@0", R.RooArgList(norm_spline))
            
            # result = sig_model.fitTo(dataSet, R.RooFit.Strategy(0),  R.RooFit.Save(R.kTRUE), R.RooFit.SumW2Error(R.kTRUE))
            getattr(w, 'import')(SignalModel, R.RooFit.RecycleConflictNodes() )
            getattr(w, 'import')(FinalNorm, R.RooFit.RecycleConflictNodes())

            
        w.Write()
        del w

        # outfile2 = R.TFile("pulls/pulls_sig_cat{}.root".format(cat),"recreate")
        # for i in range(len(sig_resids)):
        #     sig_resids[i].Write()
        #     sig_pulls[i].Write()

if doBkg or doMultiPDF:
    print(bkg_stats)
    print(bkg_fit_results)

if doSig:
    print(sig_stats)

if doCorePDF:
    print(corePDF_results)

if doMultiPDF:
    with open("fit_results/bkg_fit_results.json", "w") as jsonFile:
        json.dump(bkg_fit_results, jsonFile, sort_keys=True, indent=4)

# print(sig_fit_results)
# with open("fit_results/sig_fit_results_{}.json".format(year), "w") as jsonFile:
#     json.dump(sig_fit_results, jsonFile, sort_keys=True, indent=4)
