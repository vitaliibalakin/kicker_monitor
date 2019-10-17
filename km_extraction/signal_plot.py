#!/usr/bin/env python3

from PyQt5.QtWidgets import QApplication
import sys
import pyqtgraph as pg


class SignalPlot(pg.PlotWidget):
    def __init__(self, parent, range_a, range_b):
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        super(SignalPlot, self).__init__(parent=parent)
        self.showGrid(x=True, y=True)
        self.setRange(yRange=[range_a, range_b])
        self.good_plot = pg.PlotCurveItem(pen='w')
        self.temp_plot = pg.PlotCurveItem(pen='r')
        self.addItem(self.good_plot)
        self.addItem(self.temp_plot)

    def update_signal(self, signal_t, signal_g):
        self.good_plot.setData(signal_g)
        self.good_plot.setData(signal_t)


if __name__ == "__main__":
    app = QApplication(['signal_plot'])
    w = SignalPlot(None, -5, 5)
    sys.exit(app.exec_())
