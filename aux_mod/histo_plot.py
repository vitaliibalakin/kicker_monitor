#!/usr/bin/env python3

from PyQt5.QtWidgets import QApplication
import sys
import numpy as np
import pyqtgraph as pg


class HistoPlot(pg.PlotWidget):
    def __init__(self, parent):
        super(HistoPlot, self).__init__(parent=parent)
        self.showGrid(x=True, y=True)

    def update_signal(self, signal, range_a, range_b, bin_nums):
        try:
            if len(signal) > 2:
                # update data for plotting
                h_y, h_x = np.histogram(signal, bins=bin_nums, range=(range_a, range_b))
                h_y_1, h_x_1 = np.histogram(signal[-1], bins=bin_nums, range=(range_a, range_b))
                h_y_2, h_x_2 = np.histogram(signal[-2], bins=bin_nums, range=(range_a, range_b))
                h_y_3, h_x_3 = np.histogram(signal[-3], bins=bin_nums, range=(range_a, range_b))

                # plot new histo
                self.clear()
                self.setRange(xRange=[range_a, range_b])
                self.plot(h_x, h_y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 150))
                self.plot(h_x_1, 30 * h_y_1, stepMode=True, fillLevel=0, brush=(196, 30, 58, 150))
                self.plot(h_x_2, 25 * h_y_2, stepMode=True, fillLevel=0, brush=(255, 0, 255, 150))
                self.plot(h_x_3, 20 * h_y_3, stepMode=True, fillLevel=0, brush=(255, 203, 219, 150))
        except Exception as exc:
            print(exc)


if __name__ == "__main__":
    app = QApplication(['histo_plot'])
    w = HistoPlot(None, -5, 5, 10)
    sys.exit(app.exec_())
