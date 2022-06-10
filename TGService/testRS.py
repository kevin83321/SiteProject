from TGBot.PlotUtils.RS_Pivots import mainPlot
import sys

if __name__ == "__main__":
    ticker = "2330"
    if len(sys.argv) >= 2:
        ticker = sys.argv[1]
    mainPlot(ticker)