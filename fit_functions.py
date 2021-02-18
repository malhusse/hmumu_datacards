import ROOT as R
from array import array
import os
import sys
import glob
from math import ceil

# physics inspired functions

def getGoodnessOfFit(ws, pdfName, dataName, ndata):

    norm = R.RooRealVar("norm", "norm", ndata, .5 * ndata, 2*ndata)
    pdf = R.RooExtendPdf("ext", "ext", ws.pdf(pdfName), norm)
    mass = ws.var("mass")
    plot_chi2 = mass.frame()
    data = ws.data(dataName)

    data.plotOn(plot_chi2, R.RooFit.Name("data"))
    pdf.plotOn(plot_chi2, R.RooFit.Name("pdf"))

    np = pdf.getParameters(data).getSize()
    chi2 = plot_chi2.chiSquare("pdf", "data", np)

    nBinsForMass = data.numEntries()

    if float(ndata) / nBinsForMass < 5:
        ntoys = 500
        print(" can't use asymptotic approximation!! need to run toys")
        prob = getProbabilityFtest(chi2*(nBinsForMass-np), nBinsForMass-np)

    else:
        prob = getProbabilityFtest(chi2*(nBinsForMass-np), nBinsForMass-np)

    print("chi2 = {}".format(chi2))
    print("chi2 in observed {}".format(chi2*(nBinsForMass-np)))
    print("p-value = {}".format(prob))

    hresid = plot_chi2.residHist()
    hpull = plot_chi2.pullHist()

    return chi2, prob, hresid, hpull


def runFit(ws, pdfName, dataName):
    maxTries = 5
    numTries = 0
    stat = -1
    minimumNll = 10e08

    pdf_to_fit = ws.pdf(pdfName)
    data_to_fit = ws.data(dataName)
    fit_result = pdf_to_fit.fitTo(data_to_fit,  R.RooFit.Minimizer("Minuit","migrad"), R.RooFit.Strategy(0) , R.RooFit.SumW2Error(R.kTRUE), R.RooFit.Save(R.kTRUE))

    stat = fit_result.status()
    params_test = pdf_to_fit.getParameters(R.RooArgSet())
    while stat != 0:
        if numTries >= maxTries:
            break

        fit_result = pdf_to_fit.fitTo(data_to_fit, R.RooFit.Minimizer("Minuit","migrad"),  R.RooFit.Save(R.kTRUE), R.RooFit.Strategy(0) , R.RooFit.SumW2Error(R.kTRUE))

        stat = fit_result.status()

        minimumNll = fit_result.minNll()
        numTries += 1
        if stat != 0 and numTries < maxTries:
            params_test.assignValueOnly(fit_result.randomizePars())

    return stat, minimumNll


def getProbabilityFtest(chi2, ndof):
    prob_asym = R.TMath.Prob(chi2, ndof)
    return prob_asym

# fTest for expSeries, powSeries and Bern
# create temporary ws, test fits with different order
# and return pdf with order that we want...


def fTest(prefix, pdf, ws, dataName):
    maxOrder = 16
    alpha = 0.05
    prevNll = -1

    prevPdf = None
    prevOrder = 0
    prevStat = -1
    prob = 0

    store = []
    tws = R.RooWorkspace("tws", False)

    # import the dataset to the temporary working space
    getattr(tws, 'import')(ws.data(dataName), R.RooFit.RecycleConflictNodes())

    for order in range(1, maxOrder):
        if prob < alpha:
            thisNll = 0
            fitStatus = -1

            if pdf == "bern":
                t = getBernstein(prefix, tws, order)
            elif pdf == "exp":
                t = getExpSeries(prefix, tws, order)
            elif pdf == "pow":
                t = getPowerSeries(prefix, tws, order)

            # make sure it's not None (odd powerSeries and bern < 7)
            if (t):
                fitStatus, thisNll = runFit(tws, t.GetName(), dataName)
                if fitStatus != 0:
                    print(
                        "WARNING -- Fit status for {} is {}".format(t.GetName(), fitStatus))

                chi2 = 2.0*(prevNll - thisNll)

                if chi2 < 0 and order > 1:
                    chi2 = 0

                if prevPdf:
                    prob = getProbabilityFtest(chi2, order - prevOrder)
                    print(
                        "PDF: {} ; F-Test Prob(chi2> chi2(data)) == {}".format(t.GetName(), prob))
                else:
                    prob = 0

                # gofProb = 0

                if prob < alpha:
                    prevNll = thisNll
                    prevOrder = order
                    prevPdf = t.GetName()
                    prevStat = fitStatus

                store.append(t.GetName())

    print("return pdf {}".format(prevPdf))
    getattr(ws, 'import')(tws.pdf(prevPdf), R.RooFit.RecycleConflictNodes())
    return prevStat, ws.pdf(prevPdf)


def getBWZ(prefix, ws, dataName):
    a = R.RooRealVar("bwz_{}_a".format(prefix),
                     "bwz_{}_a".format(prefix), -1e-03, -1.0, 0.1)

    pdf = R.RooGenericPdf("bwz_{}".format(prefix), "bwz_{}".format(
        prefix), "TMath::Exp(@0*@1)/((@0-91.2)*(@0-91.2)+1.5625)", R.RooArgList(ws.var("mass"), a))

    getattr(ws, 'import')(pdf, R.RooFit.RecycleConflictNodes())

    fitStat, _ = runFit(ws, pdf.GetName(), dataName)

    return fitStat, ws.pdf("bwz_{}".format(prefix))


def getBWZGamma(prefix, ws, dataName):
    a = R.RooRealVar("bwzgamma_{}_a".format(prefix),
                     "bwzgamma_{}_a".format(prefix), -.005, -.01, 0)

    pdf1 = R.RooGenericPdf("bwzgamma_{}_pdf1".format(prefix), "bwzgamma_{}_pdf1".format(
        prefix), "TMath::Exp(@0*@1)*2.5/((@0-91.2)*(@0-91.2)+1.5625)", R.RooArgList(ws.var("mass"), a))

    pdf2 = R.RooGenericPdf("bwzgamma_{}_pdf2".format(prefix), "bwzgamma_{}_pdf2".format(
        prefix), "TMath::Exp(@0*@1)/(@0*@0)", R.RooArgList(ws.var("mass"), a))
    f = R.RooRealVar("bwzgamma_{}_f".format(prefix),
                     "bwzgamma_{}_f".format(prefix), 0.38, 0.2, 1)

    pdf = R.RooAddPdf("bwzgamma_{}".format(prefix), "bwzgamma_{}".format(
        prefix), R.RooArgList(pdf1, pdf2), R.RooArgList(f), R.kTRUE)
    getattr(ws, 'import')(pdf, R.RooFit.RecycleConflictNodes())

    fitStat, _ = runFit(ws, pdf.GetName(), dataName)

    return fitStat, ws.pdf("bwzgamma_{}".format(prefix))


def getBWZRedux(prefix, ws, dataName):
    a = R.RooRealVar("bwzred_{}_a".format(prefix),
                     "bwzred_{}_a".format(prefix), 2.0, 0, 5)
    b = R.RooRealVar("bwzred_{}_b".format(prefix),
                     "bwzred_{}_b".format(prefix), 0, -.1, .1)
    # b.setConstant()
    c = R.RooRealVar("bwzred_{}_c".format(prefix),
                     "bwzred_{}_c".format(prefix), 0, -.1, .1)

    pdf = R.RooGenericPdf("bwzred_{}".format(prefix), "bwzred_{}".format(
        prefix), "TMath::Exp(@2*@0 +@0*@0*@3 )/(TMath::Power((@0-91.2),@1)+TMath::Power(2.5/2.,@1)) ", R.RooArgList(ws.var("mass"), a, b, c))
    getattr(ws, 'import')(pdf, R.RooFit.RecycleConflictNodes())

    fitStat, _ = runFit(ws, pdf.GetName(), dataName)

    return fitStat, ws.pdf("bwzred_{}".format(prefix))

# agnostic functions


def getBernstein(prefix, ws, order):
    if order > 7:
        return None

    coeff = []
    coeff_sq = []
    for i in range(order):
        coeff.append(R.RooRealVar("bern_ord{}_{}_p{}".format(
            order, prefix, i), "bern_ord{}_{}_p{}".format(order, prefix, i), 0.1*(i+1), -6., 6.))
        coeff_sq.append(R.RooFormulaVar("bern_ord{}_{}_p{}_sq".format(order, prefix, i),
                                        "bern_ord{}_{}_p{}_sq".format(order, prefix, i), "@0*@0", R.RooArgList(coeff[i])))

    coeffList = R.RooArgList(*coeff_sq)
    pdf = R.RooBernsteinFast(order)("bern_ord{}_{}".format(
        order, prefix), "bern_ord{}_{}".format(order, prefix), ws.var("mass"), coeffList)

    getattr(ws, 'import')(pdf, R.RooFit.RecycleConflictNodes())

    return ws.pdf("bern_ord{}_{}".format(order, prefix))


def getPowerSeries(prefix, ws, order):

    if (order % 2 == 0):
        print("use odd power series order!!")
        return None

    coeffList = []
    powList = []
    fracList = []

    nfracs = (order-1)/2
    npows = order - nfracs

    for i in range(npows):
        coeffList.append(R.RooRealVar("powser_ord{}_{}_a{}".format(
            order, prefix, i), "powser_ord{}_{}_a{}".format(order, prefix, i), max(-10., -1.*(i+2)), -10, 0))
        powList.append(R.RooPower("powser_ord{}_{}_p{}".format(order, prefix, i),
                                  "powser_ord{}_{}_p{}".format(order, prefix, i), ws.var("mass"), coeffList[i]))
    for i in range(nfracs):
        fracList.append(R.RooRealVar("powser_ord{}_{}_f{}".format(
            order, prefix, i), "powser_ord{}_{}_f{}".format(order, prefix, i), .1, 0, 1.0))

    fracArgList = R.RooArgList(*fracList)
    powArgList = R.RooArgList(*powList)
    pdf = R.RooAddPdf("powser_ord{}_{}".format(order, prefix), "powser_ord{}_{}".format(
        order, prefix), powArgList, fracArgList, R.kTRUE)
    getattr(ws, 'import')(pdf, R.RooFit.RecycleConflictNodes())

    return ws.pdf("powser_ord{}_{}".format(order, prefix))

def getExpSeries(prefix, ws, order):
    if order < 2:
        return None

    coeffList = []
    expList = []
    fracList = []

    nfracs = (order-1)/2
    nexps = order - nfracs

    for i in range(nexps):
        coeffList.append(R.RooRealVar("expser_ord{}_{}_a{}".format(
            order, prefix, i), "expser_ord{}_{}_a{}".format(order, prefix, i), max(-1, -0.04*(i+2)), -1.0, 0))
        expList.append(R.RooExponential("expser_ord{}_{}_e{}".format(order, prefix, i),
                                        "expser_ord{}_{}_e{}".format(order, prefix, i), ws.var("mass"), coeffList[i]))
    for i in range(nfracs):
        fracList.append(R.RooRealVar("expser_ord{}_{}_f{}".format(order, prefix, i),
                                     "expser_ord{}_{}_f{}".format(order, prefix, i), .9-(float(i)/nfracs), 0.0001, 0.9999))

    fracArgList = R.RooArgList(*fracList)
    expArgList = R.RooArgList(*expList)
    pdf = R.RooAddPdf("expser_ord{}_{}".format(order, prefix), "expser_ord{}_{}".format(
        order, prefix), expArgList, fracArgList, R.kTRUE)
    getattr(ws, 'import')(pdf, R.RooFit.RecycleConflictNodes())

    return ws.pdf("expser_ord{}_{}".format(order, prefix))




####### CORE PDF BELOW THIS POINT #########
def getBWZReduxCore(prefix, ws, dataName):
    a = R.RooRealVar("bwzred_{}_a".format(prefix),
                     "bwzred_{}_a".format(prefix), .05, -0.1, 0.1)
    b = R.RooRealVar("bwzred_{}_b".format(prefix),
                     "bwzred_{}_b".format(prefix), 0.0, -.1, .1)
    # b.setConstant()
    c = R.RooRealVar("bwzred_{}_c".format(prefix),
                     "bwzred_{}_c".format(prefix), 2.0, 0, 5)

    pdf = R.RooModZPdf("bwzred_{}".format(prefix), "bwzred_{}".format(prefix), ws.var("mass"), a, b, c)
        
    getattr(ws, 'import')(pdf, R.RooFit.RecycleConflictNodes())
    stat,_ = runFit(ws, pdf.GetName(), dataName)
    getattr(ws, 'import')(pdf, R.RooFit.RecycleConflictNodes())

    return stat, ws.pdf("bwzred_{}".format(prefix))

def getExpSeriesCore(prefix, ws, dataName):

    a1 = R.RooRealVar("expser_ord2_{}_a1".format(prefix), "expser_ord2_{}_a1".format(prefix), -.03, -1.0, 0.0)
    a2 = R.RooRealVar("expser_ord2_{}_a2".format(prefix), "expser_ord2_{}_a2".format(prefix), -.15, -1.0, 0.0)
    f = R.RooRealVar("expser_ord2_{}_f".format(prefix),"expser_ord2_{}_f".format(prefix), .75, 0.0, 1.0)

    pdf = R.RooSumTwoExpPdf("expser_ord2_{}".format(prefix), "expser_ord2_{}".format(prefix), ws.var("mass"), a1, a2, f)

    getattr(ws, 'import')(pdf, R.RooFit.RecycleConflictNodes())
    stat,_ = runFit(ws, pdf.GetName(), dataName)
    getattr(ws, 'import')(pdf, R.RooFit.RecycleConflictNodes())
    
    return stat, ws.pdf("expser_ord2_{}".format(prefix))


def getFEWZCore(prefix, ws, dataName):
    fewzFile = "fewzFiles/fewz_1j.dat"
    fewz_mass = []
    fewz_xsec = []
    with open(fewzFile) as f:
        for line in f:
            mass, xsec = line.strip().split(",")
            fewz_mass.append(float(mass))
            fewz_xsec.append(float(xsec))


    bernCoeffList = []

    for i in range(1,4):
        bernCoeffList.append(R.RooRealVar("fewz_bern_order3_coeff{}".format(i), "fewz_bern_order3_coeff{}".format(i), 0.95, -10, 10))

    bernCoeffArgList = R.RooArgList(*bernCoeffList)

    fewz_spline = R.RooSpline1D("fewz_core_spline","fewz_core_spline",ws.var("mass"),len(fewz_mass), array("f",fewz_mass), array("f",fewz_xsec))
    fewz_spline_pdf = R.RooGenericPdf("fewz_spline_pdf", "fewz_spline_pdf","@0",R.RooArgList(fewz_spline))
    fewz_bernstein_pdf = R.RooBernsteinFast(3)("fewz_bern_order3_pdf", "fewz_bern_order3_pdf", ws.var("mass"), bernCoeffArgList)

    pdf = R.RooProdPdf("fewz_bernstein_{}".format(prefix), "fewz_bernstein_{}".format(prefix), fewz_spline_pdf, fewz_bernstein_pdf)
    # getattr(ws, 'import')(pdf, R.RooFit.RecycleConflictNodes())
    # stat,_ = runFit(ws, pdf.GetName(), dataName)
    stat = 0
    getattr(ws, 'import')(pdf, R.RooFit.RecycleConflictNodes())
    return stat, ws.pdf("fewz_bernstein_{}".format(prefix))


def getTransfer(prefix, ws, chebyOrder, transferDataName):
    bwzrChebychevCoeff = []
    expChebychevCoeff = []
    fewzChebychevCoeff = []
    
    for i in range(1, chebyOrder+1):
        bwzrChebychevCoeff.append(R.RooRealVar("bwzr_transfer_{}_coeff{}".format(
            prefix, i), "bwzr transfer_{}_coeff{}".format(prefix, i), 0, -10, 10))

        expChebychevCoeff.append(R.RooRealVar("exp_transfer_{}_coeff{}".format(
            prefix, i), "exp transfer_{}_coeff{}".format(prefix, i), 0, -10, 10))
        
        fewzChebychevCoeff.append(R.RooRealVar("fewz_transfer_{}_coeff{}".format(
            prefix, i), "fewz transfer_{}_coeff{}".format(prefix, i), 0, -10, 10))

    bwzrCheby = R.RooChebychev("bwzr_transfer_{}".format(prefix), "bwzr_transfer_{}".format(
        prefix), ws.var("mass"), R.RooArgList(*bwzrChebychevCoeff))
    expCheby = R.RooChebychev("exp_transfer_{}".format(prefix), "exp_transfer_{}".format(
        prefix), ws.var("mass"), R.RooArgList(*expChebychevCoeff))
    fewzCheby = R.RooChebychev("fewz_transfer_{}".format(prefix), "fewz_transfer_{}".format(
        prefix), ws.var("mass"), R.RooArgList(*fewzChebychevCoeff))


    getattr(ws, 'import')(bwzrCheby, R.RooFit.RecycleConflictNodes())
    getattr(ws, 'import')(expCheby, R.RooFit.RecycleConflictNodes())
    getattr(ws, 'import')(fewzCheby, R.RooFit.RecycleConflictNodes())

    stat,_ = runFit(ws, bwzrCheby.GetName(), transferDataName)
    _,_ = runFit(ws, expCheby.GetName(), transferDataName)
    _,_ = runFit(ws, fewzCheby.GetName(), transferDataName)

    getattr(ws, 'import')(bwzrCheby, R.RooFit.RecycleConflictNodes())
    getattr(ws, 'import')(expCheby, R.RooFit.RecycleConflictNodes())
    getattr(ws, 'import')(fewzCheby, R.RooFit.RecycleConflictNodes())
    
    return stat, ws.pdf(bwzrCheby.GetName()), ws.pdf(expCheby.GetName()), ws.pdf(fewzCheby.GetName())
