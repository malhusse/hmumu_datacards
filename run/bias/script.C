void script()
{
    TFile *file = 0;
    TString labels[6] = {"BWZ", "BWZRedux", "BWZGamma", "Bernstein", "Exp Series", "Power Series"};

    TFile *output = new TFile("biasPlots2D.root", "recreate");
    for (int c = 0; c <= 4; c++)
    {

        TString name = "h2d_cat";
        name += std::to_string(c);

        TH2F *h2d = new TH2F(name, name, 3, 0, 3, 2, 0, 2);

        h2d->SetCanExtend(TH1::kAllAxes);
        h2d->SetStats(0);

        for (int i = 0; i <= 5; i++)
        {
            for (int j = 0; j <= 5; j++)
            {
                // higgsCombine_cat0_gen_0_fit_0.MultiDimFit.mH125.123456.root

                TString fn = "batchOutputs/higgsCombine_cat_";
                fn += std::to_string(c);
                fn += "_gen_";
                fn += std::to_string(i);
                fn += "_fit_";
                fn += std::to_string(j);
                fn += ".MultiDimFit.mH125.123456.root";
                file = TFile::Open(fn);
                if (file)
                {
                    TTree *tree = (TTree *)file->Get("limit");
                    TTree *bestFit = tree->CopyTree("quantileExpected == -1");
                    TTree *hiFit = tree->CopyTree("quantileExpected > 0");
                    TTree *loFit = tree->CopyTree("quantileExpected < 0 && quantileExpected > -0.5");
                    float bestFit_, hiFit_, loFit_;
                    bestFit->SetBranchAddress("r", &bestFit_);
                    hiFit->SetBranchAddress("r", &hiFit_);
                    loFit->SetBranchAddress("r", &loFit_);
                    TH1F *histo = new TH1F("h", "h", 50, -10, 10);
                    int nentries = bestFit->GetEntries();

                    for (int jentry = 0; jentry < nentries; jentry++)
                    {
                        bestFit->GetEntry(jentry);
                        hiFit->GetEntry(jentry);
                        loFit->GetEntry(jentry);
                        float iBias = 2 * (bestFit_ - 1.0) / (hiFit_ - loFit_);
                        histo->Fill(iBias);
                    }

                    TFitResultPtr fitresult = histo->Fit("gaus", "SQ");
                    double mean = fitresult->Parameter(1);
                    std::cout << c << "," << i << "," << j << "," << histo->GetMean() << "," << mean << std::endl;

                    h2d->Fill(labels[i], labels[j], histo->GetMean());
                    file->Close();
                }
            }
        }
        h2d->LabelsDeflate("X");
        h2d->LabelsDeflate("Y");
        h2d->LabelsOption("v");
        h2d->Draw("text");

        output->cd();
        h2d->Write();
    }
}
