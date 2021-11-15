#!/usr/bin/env python3

from PyQt5.QtWidgets import QApplication
import sys
import numpy as np
import pyqtgraph as pg


class SignalPlot(pg.PlotWidget):
    def __init__(self, parent, range_a, range_b):
        super(SignalPlot, self).__init__(parent=parent)
        self.show()
        self.showGrid(x=True, y=True)
        self.setRange(yRange=[range_a, range_b])
        self.good_plot = pg.PlotCurveItem(pen='g')
        self.temp_plot = pg.PlotCurveItem(pen='r')
        self.plot_type = {"cur": self.temp_plot, "eq": self.good_plot}
        self.addItem(self.good_plot)
        self.addItem(self.temp_plot)

    def update_signal(self, signal, p_type):
        self.plot_type[p_type].setData(np.arange(0.0, 200.0, 1) * 5.6, signal)


if __name__ == "__main__":
    app = QApplication(['signal_plot'])
    w = SignalPlot(None, -5, 5)
    sys.exit(app.exec_())
