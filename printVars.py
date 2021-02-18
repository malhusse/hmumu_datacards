import ROOT as R
import sys

def printVars(file):
    f = R.TFile(file)
    w = f.Get("w")
    w.Print()
    args = w.allVars()
    iter = args.createIterator()
    var = iter.Next()
    while var:
       var.Print()
       var = iter.Next()


if __name__ == "__main__":
    file = sys.argv[1]
    print(file)
    printVars(file)
