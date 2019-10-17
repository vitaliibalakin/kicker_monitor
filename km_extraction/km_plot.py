#!/usr/bin/env python3

from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout
from PyQt5 import uic
import sys
import pycx4.qcda as cda
import json
import os
from kicker_monitor.km_extraction.histo_plot import HistoPlot
from kicker_monitor.km_extraction.signal_plot import SignalPlot
from kicker_monitor.km_extraction.cx_data_exchange import CXDataExchange
from kicker_monitor.km_extraction.file_data_exchange import FileDataExchange


class KickerPlot(QMainWindow):
    def __init__(self):
        super(KickerPlot, self).__init__()

        uic.loadUi("mainwindow1.ui", self)
        self.show()

        # plot area
        self.e_signal_plots = {"pre_pos": SignalPlot(self, -0.05, 0.5), "pre_neg": SignalPlot(self, -0.5, 0.05),
                               "kick_pos": SignalPlot(self, -0.12, 0.5), "kick_neg": SignalPlot(self, -0.5, 0.04)}
        self.e_histo_plots = {key: HistoPlot(self) for key, val in self.signal_plots.items()}
        # widgets positioning
        e_layout = QGridLayout()
        e_layout.addWidget(self.e_histo_plots["pre_pos"], 0, 0)
        e_layout.addWidget(self.e_signal_plots["pre_pos"], 0, 1)
        e_layout.addWidget(self.e_histo_plots["pre_neg"], 1, 0)
        e_layout.addWidget(self.e_signal_plots["pre_neg"], 1, 1)
        e_layout.addWidget(self.e_histo_plots["kick_pos"], 2, 0)
        e_layout.addWidget(self.e_signal_plots["kick_pos"], 2, 1)
        e_layout.addWidget(self.e_histo_plots["kick_neg"], 3, 0)
        e_layout.addWidget(self.e_signal_plots["kick_neg"], 3, 1)
        self.uni_e.setLayout(e_layout)

        self.p_signal_plots = {"pre_pos": SignalPlot(self, -0.05, 0.5), "pre_neg": SignalPlot(self, -0.5, 0.05),
                               "kick_pos": SignalPlot(self, -0.12, 0.5), "kick_neg": SignalPlot(self, -0.5, 0.04)}
        self.p_histo_plots = {key: HistoPlot(self) for key, val in self.signal_plots.items()}
        p_layout = QGridLayout()
        p_layout.addWidget(self.e_histo_plots["pre_pos"], 0, 0)
        p_layout.addWidget(self.e_signal_plots["pre_pos"], 0, 1)
        p_layout.addWidget(self.e_histo_plots["pre_neg"], 1, 0)
        p_layout.addWidget(self.e_signal_plots["pre_neg"], 1, 1)
        p_layout.addWidget(self.e_histo_plots["kick_pos"], 2, 0)
        p_layout.addWidget(self.e_signal_plots["kick_pos"], 2, 1)
        p_layout.addWidget(self.e_histo_plots["kick_neg"], 3, 0)
        p_layout.addWidget(self.e_signal_plots["kick_neg"], 3, 1)
        self.uni_p.setLayout(p_layout)

        self.chan_data_t = {"e": [CXDataExchange(self.data_receiver, "cxhw:2.inj.prekick.e.pos.Utemp", "e", "pre_pos",
                                                 n_elems=1024),
                                  CXDataExchange(self.data_receiver, "cxhw:2.inj.prekick.e.neg.Utemp", "e", "pre_neg",
                                                 n_elems=1024),
                                  CXDataExchange(self.data_receiver, "cxhw:2.inj.kick.e.pos.Utemp", "e", "kick_pos",
                                                 n_elems=1024),
                                  CXDataExchange(self.data_receiver, "cxhw:2.inj.kick.e.neg.Utemp", "e", "kick_neg",
                                                 n_elems=1024)],
                            "p": [CXDataExchange(self.data_receiver, "cxhw:2.inj.prekick.p.pos.Utemp", "p", "pre_pos",
                                                 n_elems=1024),
                                  CXDataExchange(self.data_receiver, "cxhw:2.inj.prekick.p.neg.Utemp", "p", "pre_neg",
                                                 n_elems=1024),
                                  CXDataExchange(self.data_receiver, "cxhw:2.inj.kick.p.pos.Utemp", "p", "kick_pos",
                                                 n_elems=1024),
                                  CXDataExchange(self.data_receiver, "cxhw:2.inj.kick.p.neg.Utemp", "p", "kick_neg",
                                                 n_elems=1024)]}
        self.chan_hist_t = {"e": [CXDataExchange(self.data_receiver, "cxhw:2.inj.prekick.e.pos.delta_t_array", "h_e",
                                                 "pre_pos", n_elems=200),
                                  CXDataExchange(self.data_receiver, "cxhw:2.inj.prekick.e.neg.delta_t_array", "h_e",
                                                 "pre_neg", n_elems=200),
                                  CXDataExchange(self.data_receiver, "cxhw:2.inj.kick.e.pos.delta_t_array", "h_e",
                                                 "kick_pos", n_elems=200),
                                  CXDataExchange(self.data_receiver, "cxhw:2.inj.kick.e.neg.delta_t_array", "h_e",
                                                 "kick_neg", n_elems=200)],
                            "p": [CXDataExchange(self.data_receiver, "cxhw:2.inj.prekick.p.pos.delta_t_array", "h_p",
                                                 "pre_pos", n_elems=200),
                                  CXDataExchange(self.data_receiver, "cxhw:2.inj.prekick.p.neg.delta_t_array", "h_p",
                                                 "pre_neg", n_elems=200),
                                  CXDataExchange(self.data_receiver, "cxhw:2.inj.kick.p.pos.delta_t_array", "h_p",
                                                 "kick_pos", n_elems=200),
                                  CXDataExchange(self.data_receiver, "cxhw:2.inj.kick.p.neg.delta_t_array", "h_p",
                                                 "kick_neg", n_elems=200)]}

        # variables for histo
        self.range_a = -5
        self.range_b = 5
        self.bins_num = 10

        self.chan_ic_mode.valueChanged.connect(self.active_tab)     # OK
        self.res_chan.valueChanged.connect(self.status_info)        # NOT OK

        self.pushButton_save.clicked.connect(self.push_save)    # NOT OK
        self.button_stg_dflt.clicked.connect(self.stg_dflt)     # OK
        self.spinBox_hist_range.valueChanged.connect(self.hist_tun)     # OK
        self.spinBox_bins_len.valueChanged.connect(self.hist_tun)       # OK

        self.green_color = 2.5
        self.red_color = 5
        self.hist_range = 10

        # for some operations e.g. switching
        self.active_tab_ = {'p': 0, 'e': 1}
        self.ic_mode = ''
        self.save_label = {'p': self.label_save_time_p, 'e': self.label_save_time_e}

        self.dict_label_st = {'cxhw:2.inj.prekick.p.pos.Utemp': self.label_st_p_p_p,
                              'cxhw:2.inj.prekick.p.neg.Utemp': self.label_st_p_p_n,
                              'cxhw:2.inj.kick.p.pos.Utemp': self.label_st_p_k_p,
                              'cxhw:2.inj.kick.p.neg.Utemp': self.label_st_p_k_n,
                              'cxhw:2.inj.prekick.e.pos.Utemp': self.label_st_e_p_p,
                              'cxhw:2.inj.prekick.e.neg.Utemp': self.label_st_e_p_n,
                              'cxhw:2.inj.kick.e.pos.Utemp': self.label_st_e_k_p,
                              'cxhw:2.inj.kick.e.neg.Utemp': self.label_st_e_k_n}       # NOT OK
        self.dict_label_dt = {'cxhw:2.inj.prekick.p.pos.Utemp': self.label_dt_p_p_p,
                              'cxhw:2.inj.prekick.p.neg.Utemp': self.label_dt_p_p_n,
                              'cxhw:2.inj.kick.p.pos.Utemp': self.label_dt_p_k_p,
                              'cxhw:2.inj.kick.p.neg.Utemp': self.label_dt_p_k_n,
                              'cxhw:2.inj.prekick.e.pos.Utemp': self.label_dt_e_p_p,
                              'cxhw:2.inj.prekick.e.neg.Utemp': self.label_dt_e_p_n,
                              'cxhw:2.inj.kick.e.pos.Utemp': self.label_dt_e_k_p,
                              'cxhw:2.inj.kick.e.neg.Utemp': self.label_dt_e_k_n}       # NOT OK

    def data_receiver(self, data, source, inf_type):
        if source == 'p':
            self.p_signal_plots[inf_type].update_signal(data, self.good_signal[inf_type])
        elif source == 'e':
            self.e_signal_plots[inf_type].update_signal(data, self.good_signal[inf_type])
        elif source == 'h_p':
            self.p_histo_plots[inf_type].update_signal(data)
        elif source == 'h_e':
            self.e_histo_plots[inf_type].update_signal(data)
        else:
            print("shouldn't be here")

    def hist_tun(self):
        self.range_a = -1 * self.spinBox_hist_range.value()
        self.range_b = self.spinBox_hist_range.value()
        self.bins_num = int(2 * self.spinBox_hist_range.value() / self.spinBox_bins_len.value())

    def active_tab(self, chan):
        self.ic_mode = chan.val[0]
        self.tabWidget.setCurrentIndex(self.active_tab_[chan.val[0]])

    def push_save(self):
        # don't force daemon to do this
        print(json.loads(self.cmd_chan.val))
        if json.loads(self.cmd_chan.val)['cmd'] == 'ready':
            print("save")
            self.cmd_chan.setValue(json.dumps({'cmd': 'save'}))

    def stg_dflt(self):
        print('stg_dflt')
        self.cmd_chan.setValue(json.dumps({'cmd': 'stg_dflt'}))

    def status_info(self, chan):
        try:
            rdict = json.loads(chan.val)
        except Exception as err:
            print(err)
        try:
            if rdict['res'] == 'good':
                if rdict['last_cmd'] == 'save':
                    self.save_label[self.ic_mode].setText(rdict['time'])
        except KeyError:
            print(KeyError)


if __name__ == "__main__":
    DIR = os.getcwd()
    app = QApplication(['kicker_monitor'])
    w = KickerPlot()
    sys.exit(app.exec_())
