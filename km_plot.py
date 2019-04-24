#!/usr/bin/env python3

from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout
from PyQt5 import uic
import sys
import pyqtgraph as pg
import pycx4.qcda as cda
import json


class KickerPlot(QMainWindow):
    def __init__(self):
        super(KickerPlot, self).__init__()
        uic.loadUi("mainwindow1.ui", self)
        self.show()
        self.forming_window()
        self.init_chans()

        self.chan_Utemp_ppn.valueMeasured.connect(self.chan_proc)
        self.chan_Utemp_ppp.valueMeasured.connect(self.chan_proc)
        self.chan_Utemp_kpn.valueMeasured.connect(self.chan_proc)
        self.chan_Utemp_kpp.valueMeasured.connect(self.chan_proc)

        self.chan_Utemp_pen.valueMeasured.connect(self.chan_proc)
        self.chan_Utemp_pep.valueMeasured.connect(self.chan_proc)
        self.chan_Utemp_ken.valueMeasured.connect(self.chan_proc)
        self.chan_Utemp_kep.valueMeasured.connect(self.chan_proc)

        self.chan_ic_mode.valueChanged.connect(self.active_tab)
        self.res_chan.valueChanged.connect(self.status_info)

        self.pushButton_save.clicked.connect(self.push_save)
        self.button_stg_dflt.clicked.connect(self.stg_dflt)
        self.spinBox_hist_range.valueChanged.connect(self.hist_tun)
        self.spinBox_bins_len.valueChanged.connect(self.hist_tun)

        self.green_color = 2.5
        self.red_color = 5
        self.hist_range = 10
        self.pp_in = 0
        self.kp_in = 0
        self.pe_in = 0
        self.ke_in = 0

        self.active_tab_ = {'p': 0, 'e': 1}
        self.save_label = {'p': self.label_save_time_p, 'e': self.label_save_time_e}
        self.ic_mode = ''

        self.chan_n_interp_ppn.setValue(10)
        self.chan_histo_range_ppn.setValue(5)

        self.dict_label_st = {'cxhw:2.inj.prekick.p.pos.Utemp': self.label_st_p_p_p,
                              'cxhw:2.inj.prekick.p.neg.Utemp': self.label_st_p_p_n,
                              'cxhw:2.inj.kick.p.pos.Utemp': self.label_st_p_k_p,
                              'cxhw:2.inj.kick.p.neg.Utemp': self.label_st_p_k_n,
                              'cxhw:2.inj.prekick.e.pos.Utemp': self.label_st_e_p_p,
                              'cxhw:2.inj.prekick.e.neg.Utemp': self.label_st_e_p_n,
                              'cxhw:2.inj.kick.e.pos.Utemp': self.label_st_e_k_p,
                              'cxhw:2.inj.kick.e.neg.Utemp': self.label_st_e_k_n}
        self.dict_label_dt = {'cxhw:2.inj.prekick.p.pos.Utemp': self.label_dt_p_p_p,
                              'cxhw:2.inj.prekick.p.neg.Utemp': self.label_dt_p_p_n,
                              'cxhw:2.inj.kick.p.pos.Utemp': self.label_dt_p_k_p,
                              'cxhw:2.inj.kick.p.neg.Utemp': self.label_dt_p_k_n,
                              'cxhw:2.inj.prekick.e.pos.Utemp': self.label_dt_e_p_p,
                              'cxhw:2.inj.prekick.e.neg.Utemp': self.label_dt_e_p_n,
                              'cxhw:2.inj.kick.e.pos.Utemp': self.label_dt_e_k_p,
                              'cxhw:2.inj.kick.e.neg.Utemp': self.label_dt_e_k_n}

    def forming_window(self):
        self.win_e = pg.GraphicsLayoutWidget(parent=self)

        self.plot_histo_e_prekick_p = self.win_e.addPlot(enableMenu=False)
        self.plot_histo_e_prekick_p.showGrid(x=True, y=True)
        self.kick_plot_e_prekick_p = self.win_e.addPlot(enableMenu=False)
        self.kick_plot_e_prekick_p.showGrid(x=True, y=True)
        self.kick_plot_e_prekick_p.setRange(yRange=[-0.04, 0.5])

        self.win_e.nextRow()

        self.plot_histo_e_prekick_n = self.win_e.addPlot(enableMenu=False)
        self.plot_histo_e_prekick_n.showGrid(x=True, y=True)
        self.kick_plot_e_prekick_n = self.win_e.addPlot(enableMenu=False)
        self.kick_plot_e_prekick_n.showGrid(x=True, y=True)
        self.kick_plot_e_prekick_n.setRange(yRange=[-0.5, 0.04])

        self.win_e.nextRow()

        self.plot_histo_e_kick_p = self.win_e.addPlot(enableMenu=False)
        self.plot_histo_e_kick_p.showGrid(x=True, y=True)
        self.kick_plot_e_kick_p = self.win_e.addPlot(enableMenu=False)
        self.kick_plot_e_kick_p.showGrid(x=True, y=True)
        self.kick_plot_e_kick_p.setRange(yRange=[-0.12, 0.5])

        self.win_e.nextRow()

        self.plot_histo_e_kick_n = self.win_e.addPlot(enableMenu=False)
        self.plot_histo_e_kick_n.showGrid(x=True, y=True)
        self.kick_plot_e_kick_n = self.win_e.addPlot(enableMenu=False)
        self.kick_plot_e_kick_n.showGrid(x=True, y=True)
        self.kick_plot_e_kick_n.setRange(yRange=[-0.5, 0.04])

        le = QHBoxLayout()
        self.uni.setLayout(le)
        le.addWidget(self.win_e)

        self.win_p = pg.GraphicsWindow(parent=self)
        self.win_p.setMouseTracking(False)
        self.win_p.setContextMenuPolicy(0)

        self.plot_histo_p_prekick_p = self.win_p.addPlot(enableMenu=False)
        self.plot_histo_p_prekick_p.showGrid(x=True, y=True)
        self.kick_plot_p_prekick_p = self.win_p.addPlot(enableMenu=False)
        self.kick_plot_p_prekick_p.showGrid(x=True, y=True)
        self.kick_plot_p_prekick_p.setRange(yRange=[-0.04, 0.5])

        self.win_p.nextRow()

        self.plot_histo_p_prekick_n = self.win_p.addPlot(enableMenu=False)
        self.plot_histo_p_prekick_n.showGrid(x=True, y=True)
        self.kick_plot_p_prekick_n = self.win_p.addPlot(enableMenu=False)
        self.kick_plot_p_prekick_n.showGrid(x=True, y=True)
        self.kick_plot_p_prekick_n.setRange(yRange=[-0.5, 0.04])

        self.win_p.nextRow()

        self.plot_histo_p_kick_p = self.win_p.addPlot(enableMenu=False)
        self.plot_histo_p_kick_p.showGrid(x=True, y=True)
        self.kick_plot_p_kick_p = self.win_p.addPlot(enableMenu=False)
        self.kick_plot_p_kick_p.showGrid(x=True, y=True)
        self.kick_plot_p_kick_p.setRange(yRange=[-0.1, 0.5])

        self.win_p.nextRow()

        self.plot_histo_p_kick_n = self.win_p.addPlot(enableMenu=False)
        self.plot_histo_p_kick_n.showGrid(x=True, y=True)
        self.kick_plot_p_kick_n = self.win_p.addPlot(enableMenu=False)
        self.kick_plot_p_kick_n.showGrid(x=True, y=True)
        self.kick_plot_p_kick_n.setRange(yRange=[-0.5, 0.04])

        lp = QHBoxLayout()
        self.uni_1.setLayout(lp)
        lp.addWidget(self.win_p)

        self.dict_hist_plot = {'cxhw:2.inj.prekick.p.pos.Utemp': self.plot_histo_p_prekick_p,
                               'cxhw:2.inj.prekick.p.neg.Utemp': self.plot_histo_p_prekick_n,
                               'cxhw:2.inj.kick.p.pos.Utemp': self.plot_histo_p_kick_p,
                               'cxhw:2.inj.kick.p.neg.Utemp': self.plot_histo_p_kick_n,
                               'cxhw:2.inj.prekick.e.pos.Utemp': self.plot_histo_e_prekick_p,
                               'cxhw:2.inj.prekick.e.neg.Utemp': self.plot_histo_e_prekick_n,
                               'cxhw:2.inj.kick.e.pos.Utemp': self.plot_histo_e_kick_p,
                               'cxhw:2.inj.kick.e.neg.Utemp': self.plot_histo_e_kick_n}

        self.dict_imp_plot = {'cxhw:2.inj.prekick.p.pos.Utemp': self.kick_plot_p_prekick_p,
                              'cxhw:2.inj.prekick.p.neg.Utemp': self.kick_plot_p_prekick_n,
                              'cxhw:2.inj.kick.p.pos.Utemp': self.kick_plot_p_kick_p,
                              'cxhw:2.inj.kick.p.neg.Utemp': self.kick_plot_p_kick_n,
                              'cxhw:2.inj.prekick.e.pos.Utemp': self.kick_plot_e_prekick_p,
                              'cxhw:2.inj.prekick.e.neg.Utemp': self.kick_plot_e_prekick_n,
                              'cxhw:2.inj.kick.e.pos.Utemp': self.kick_plot_e_kick_p,
                              'cxhw:2.inj.kick.e.neg.Utemp': self.kick_plot_e_kick_n}

    def init_chans(self):
        self.chan_sel_all = cda.DChan("cxhw:18.kkr_sel_all.0")

        self.cmd_chan = cda.StrChan("cxhw:2.kickADCproc.inj.cmd", on_update=1, max_nelems=1024)
        self.res_chan = cda.StrChan("cxhw:2.kickADCproc.inj.res", on_update=1, max_nelems=1024)

        self.chan_ic_mode = cda.StrChan("cxhw:0.k500.modet", max_nelems=4)

        self.chan_Tgood_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.Tgood", max_nelems=1024)  # positrons "-" prekick
        self.chan_Ugood_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.Ugood", max_nelems=1024)
        self.chan_Ttemp_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.Ttemp", max_nelems=1024)
        self.chan_Utemp_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.Utemp", max_nelems=1024)
        self.chan_delta_a_ppn = cda.DChan("cxhw:2.inj.prekick.p.neg.delta_a")
        self.chan_delta_t_ppn = cda.DChan("cxhw:2.inj.prekick.p.neg.delta_t")
        self.chan_n_interp_ppn = cda.DChan("cxhw:2.inj.prekick.p.neg.n_interp")
        self.chan_sigma_t_ppn = cda.DChan("cxhw:2.inj.prekick.p.neg.sigma_cur")
        self.chan_delta_arr_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.delta_t_array", max_nelems=100)
        self.chan_t_peak_ppn = cda.DChan("cxhw:2.inj.prekick.p.neg.t_peak")
        self.chan_histo_range_ppn = cda.DChan("cxhw:2.inj.prekick.p.neg.histo_range")
        self.chan_histo_x_all_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.histo_x_all", max_nelems=100)
        self.chan_histo_y_all_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.histo_y_all", max_nelems=100)
        self.chan_histo_x_1_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.histo_x_1", max_nelems=101)
        self.chan_histo_y_1_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.histo_y_1", max_nelems=101)
        self.chan_histo_x_2_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.histo_x_2", max_nelems=101)
        self.chan_histo_y_2_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.histo_y_2", max_nelems=101)
        self.chan_histo_x_3_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.histo_x_3", max_nelems=101)
        self.chan_histo_y_3_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.histo_y_3", max_nelems=101)

        self.chan_Tgood_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.Tgood", max_nelems=1024)  # positrons "-" kick
        self.chan_Ugood_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.Ugood", max_nelems=1024)
        self.chan_Ttemp_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.Ttemp", max_nelems=1024)
        self.chan_Utemp_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.Utemp", max_nelems=1024)
        self.chan_delta_a_kpn = cda.DChan("cxhw:2.inj.kick.p.neg.delta_a")
        self.chan_delta_t_kpn = cda.DChan("cxhw:2.inj.kick.p.neg.delta_t")
        self.chan_n_interp_kpn = cda.DChan("cxhw:2.inj.kick.p.neg.n_interp")
        self.chan_sigma_t_kpn = cda.DChan("cxhw:2.inj.kick.p.neg.sigma_cur")
        self.chan_delta_arr_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.delta_t_array", max_nelems=200)
        self.chan_t_peak_kpn = cda.DChan("cxhw:2.inj.kick.p.neg.t_peak")
        self.chan_histo_x_all_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.histo_x_all", max_nelems=100)
        self.chan_histo_y_all_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.histo_y_all", max_nelems=100)
        self.chan_histo_x_1_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.histo_x_1", max_nelems=101)
        self.chan_histo_y_1_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.histo_y_1", max_nelems=101)
        self.chan_histo_x_2_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.histo_x_2", max_nelems=101)
        self.chan_histo_y_2_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.histo_y_2", max_nelems=101)
        self.chan_histo_x_3_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.histo_x_3", max_nelems=101)
        self.chan_histo_y_3_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.histo_y_3", max_nelems=101)

        self.chan_Tgood_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.Tgood", max_nelems=1024)  # positrons "+" prekick
        self.chan_Ugood_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.Ugood", max_nelems=1024)
        self.chan_Ttemp_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.Ttemp", max_nelems=1024)
        self.chan_Utemp_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.Utemp", max_nelems=1024)
        self.chan_delta_a_ppp = cda.DChan("cxhw:2.inj.prekick.p.pos.delta_a")
        self.chan_delta_t_ppp = cda.DChan("cxhw:2.inj.prekick.p.pos.delta_t")
        self.chan_n_interp_ppp = cda.DChan("cxhw:2.inj.prekick.p.pos.n_interp")
        self.chan_sigma_t_ppp = cda.DChan("cxhw:2.inj.prekick.p.pos.sigma_cur")
        self.chan_delta_arr_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.delta_t_array", max_nelems=200)
        self.chan_t_peak_ppp = cda.DChan("cxhw:2.inj.prekick.p.pos.t_peak")
        self.chan_histo_x_all_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.histo_x_all", max_nelems=100)
        self.chan_histo_y_all_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.histo_y_all", max_nelems=100)
        self.chan_histo_x_1_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.histo_x_1", max_nelems=101)
        self.chan_histo_y_1_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.histo_y_1", max_nelems=101)
        self.chan_histo_x_2_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.histo_x_2", max_nelems=101)
        self.chan_histo_y_2_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.histo_y_2", max_nelems=101)
        self.chan_histo_x_3_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.histo_x_3", max_nelems=101)
        self.chan_histo_y_3_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.histo_y_3", max_nelems=101)

        self.chan_Tgood_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.Tgood", max_nelems=1024)  # positrons "+" kick
        self.chan_Ugood_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.Ugood", max_nelems=1024)
        self.chan_Ttemp_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.Ttemp", max_nelems=1024)
        self.chan_Utemp_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.Utemp", max_nelems=1024)
        self.chan_delta_a_kpp = cda.DChan("cxhw:2.inj.kick.p.pos.delta_a")
        self.chan_delta_t_kpp = cda.DChan("cxhw:2.inj.kick.p.pos.delta_t")
        self.chan_n_interp_kpp = cda.DChan("cxhw:2.inj.kick.p.pos.n_interp")
        self.chan_sigma_t_kpp = cda.DChan("cxhw:2.inj.kick.p.pos.sigma_cur")
        self.chan_delta_arr_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.delta_t_array", max_nelems=200)
        self.chan_t_peak_kpp = cda.DChan("cxhw:2.inj.kick.p.pos.t_peak")
        self.chan_histo_x_all_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.histo_x_all", max_nelems=100)
        self.chan_histo_y_all_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.histo_y_all", max_nelems=100)
        self.chan_histo_x_1_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.histo_x_1", max_nelems=101)
        self.chan_histo_y_1_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.histo_y_1", max_nelems=101)
        self.chan_histo_x_2_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.histo_x_2", max_nelems=101)
        self.chan_histo_y_2_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.histo_y_2", max_nelems=101)
        self.chan_histo_x_3_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.histo_x_3", max_nelems=101)
        self.chan_histo_y_3_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.histo_y_3", max_nelems=101)

        self.chan_Tgood_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.Tgood", max_nelems=1024)  # electrons "-" prekick
        self.chan_Ugood_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.Ugood", max_nelems=1024)
        self.chan_Ttemp_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.Ttemp", max_nelems=1024)
        self.chan_Utemp_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.Utemp", max_nelems=1024)
        self.chan_delta_a_pen = cda.DChan("cxhw:2.inj.prekick.e.neg.delta_a")
        self.chan_delta_t_pen = cda.DChan("cxhw:2.inj.prekick.e.neg.delta_t")
        self.chan_n_interp_pen = cda.DChan("cxhw:2.inj.prekick.e.neg.n_interp")
        self.chan_sigma_t_pen = cda.DChan("cxhw:2.inj.prekick.e.neg.sigma_cur")
        self.chan_delta_arr_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.delta_t_array", max_nelems=200)
        self.chan_t_peak_pen = cda.DChan("cxhw:2.inj.prekick.e.neg.t_peak")
        self.chan_histo_x_all_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.histo_x_all", max_nelems=100)
        self.chan_histo_y_all_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.histo_y_all", max_nelems=100)
        self.chan_histo_x_1_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.histo_x_1", max_nelems=101)
        self.chan_histo_y_1_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.histo_y_1", max_nelems=101)
        self.chan_histo_x_2_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.histo_x_2", max_nelems=101)
        self.chan_histo_y_2_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.histo_y_2", max_nelems=101)
        self.chan_histo_x_3_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.histo_x_3", max_nelems=101)
        self.chan_histo_y_3_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.histo_y_3", max_nelems=101)

        self.chan_Tgood_ken = cda.VChan("cxhw:2.inj.kick.e.neg.Tgood", max_nelems=1024)  # electrons "-" kick
        self.chan_Ugood_ken = cda.VChan("cxhw:2.inj.kick.e.neg.Ugood", max_nelems=1024)
        self.chan_Ttemp_ken = cda.VChan("cxhw:2.inj.kick.e.neg.Ttemp", max_nelems=1024)
        self.chan_Utemp_ken = cda.VChan("cxhw:2.inj.kick.e.neg.Utemp", max_nelems=1024)
        self.chan_delta_a_ken = cda.DChan("cxhw:2.inj.kick.e.neg.delta_a")
        self.chan_delta_t_ken = cda.DChan("cxhw:2.inj.kick.e.neg.delta_t")
        self.chan_n_interp_ken = cda.DChan("cxhw:2.inj.kick.e.neg.n_interp")
        self.chan_sigma_t_ken = cda.DChan("cxhw:2.inj.kick.e.neg.sigma_cur")
        self.chan_delta_arr_ken = cda.VChan("cxhw:2.inj.kick.e.neg.delta_t_array", max_nelems=200)
        self.chan_t_peak_ken = cda.DChan("cxhw:2.inj.kick.e.neg.t_peak")
        self.chan_histo_x_all_ken = cda.VChan("cxhw:2.inj.kick.e.neg.histo_x_all", max_nelems=100)
        self.chan_histo_y_all_ken = cda.VChan("cxhw:2.inj.kick.e.neg.histo_y_all", max_nelems=100)
        self.chan_histo_x_1_ken = cda.VChan("cxhw:2.inj.kick.e.neg.histo_x_1", max_nelems=101)
        self.chan_histo_y_1_ken = cda.VChan("cxhw:2.inj.kick.e.neg.histo_y_1", max_nelems=101)
        self.chan_histo_x_2_ken = cda.VChan("cxhw:2.inj.kick.e.neg.histo_x_2", max_nelems=101)
        self.chan_histo_y_2_ken = cda.VChan("cxhw:2.inj.kick.e.neg.histo_y_2", max_nelems=101)
        self.chan_histo_x_3_ken = cda.VChan("cxhw:2.inj.kick.e.neg.histo_x_3", max_nelems=101)
        self.chan_histo_y_3_ken = cda.VChan("cxhw:2.inj.kick.e.neg.histo_y_3", max_nelems=101)

        self.chan_Tgood_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.Tgood", max_nelems=1024)  # electrons "+" prekick
        self.chan_Ugood_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.Ugood", max_nelems=1024)
        self.chan_Ttemp_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.Ttemp", max_nelems=1024)
        self.chan_Utemp_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.Utemp", max_nelems=1024)
        self.chan_delta_a_pep = cda.DChan("cxhw:2.inj.prekick.e.pos.delta_a")
        self.chan_delta_t_pep = cda.DChan("cxhw:2.inj.prekick.e.pos.delta_t")
        self.chan_n_interp_pep = cda.DChan("cxhw:2.inj.prekick.e.pos.n_interp")
        self.chan_sigma_t_pep = cda.DChan("cxhw:2.inj.prekick.e.pos.sigma_cur")
        self.chan_delta_arr_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.delta_t_array", max_nelems=200)
        self.chan_t_peak_pep = cda.DChan("cxhw:2.inj.prekick.e.pos.t_peak")
        self.chan_histo_x_all_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.histo_x_all", max_nelems=100)
        self.chan_histo_y_all_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.histo_y_all", max_nelems=100)
        self.chan_histo_x_1_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.histo_x_1", max_nelems=101)
        self.chan_histo_y_1_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.histo_y_1", max_nelems=101)
        self.chan_histo_x_2_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.histo_x_2", max_nelems=101)
        self.chan_histo_y_2_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.histo_y_2", max_nelems=101)
        self.chan_histo_x_3_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.histo_x_3", max_nelems=101)
        self.chan_histo_y_3_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.histo_y_3", max_nelems=101)

        self.chan_Tgood_kep = cda.VChan("cxhw:2.inj.kick.e.pos.Tgood", max_nelems=1024)  # electrons "+" kick
        self.chan_Ugood_kep = cda.VChan("cxhw:2.inj.kick.e.pos.Ugood", max_nelems=1024)
        self.chan_Ttemp_kep = cda.VChan("cxhw:2.inj.kick.e.pos.Ttemp", max_nelems=1024)
        self.chan_Utemp_kep = cda.VChan("cxhw:2.inj.kick.e.pos.Utemp", max_nelems=1024)
        self.chan_delta_a_kep = cda.DChan("cxhw:2.inj.kick.e.pos.delta_a")
        self.chan_delta_t_kep = cda.DChan("cxhw:2.inj.kick.e.pos.delta_t")
        self.chan_n_interp_kep = cda.DChan("cxhw:2.inj.kick.e.pos.n_interp")
        self.chan_sigma_t_kep = cda.DChan("cxhw:2.inj.kick.e.pos.sigma_cur")
        self.chan_delta_arr_kep = cda.VChan("cxhw:2.inj.kick.e.pos.delta_t_array", max_nelems=200)
        self.chan_t_peak_kep = cda.DChan("cxhw:2.inj.kick.e.pos.t_peak")
        self.chan_histo_x_all_kep = cda.VChan("cxhw:2.inj.kick.e.pos.histo_x_all", max_nelems=100)
        self.chan_histo_y_all_kep = cda.VChan("cxhw:2.inj.kick.e.pos.histo_y_all", max_nelems=100)
        self.chan_histo_x_1_kep = cda.VChan("cxhw:2.inj.kick.e.pos.histo_x_1", max_nelems=101)
        self.chan_histo_y_1_kep = cda.VChan("cxhw:2.inj.kick.e.pos.histo_y_1", max_nelems=101)
        self.chan_histo_x_2_kep = cda.VChan("cxhw:2.inj.kick.e.pos.histo_x_2", max_nelems=101)
        self.chan_histo_y_2_kep = cda.VChan("cxhw:2.inj.kick.e.pos.histo_y_2", max_nelems=101)
        self.chan_histo_x_3_kep = cda.VChan("cxhw:2.inj.kick.e.pos.histo_x_3", max_nelems=101)
        self.chan_histo_y_3_kep = cda.VChan("cxhw:2.inj.kick.e.pos.histo_y_3", max_nelems=101)

        self.dict_count = {'cxhw:2.inj.prekick.p.neg.Utemp': 0, 'cxhw:2.inj.kick.p.neg.Utemp': 0,
                           'cxhw:2.inj.prekick.p.pos.Utemp': 0, 'cxhw:2.inj.kick.p.pos.Utemp': 0,
                           'cxhw:2.inj.prekick.e.neg.Utemp': 0, 'cxhw:2.inj.kick.e.neg.Utemp': 0,
                           'cxhw:2.inj.prekick.e.pos.Utemp': 0, 'cxhw:2.inj.kick.e.pos.Utemp': 0}

        self.dict_delta_t = {'cxhw:2.inj.prekick.p.pos.Utemp': self.chan_delta_t_ppp,
                             'cxhw:2.inj.prekick.p.neg.Utemp': self.chan_delta_t_ppn,
                             'cxhw:2.inj.kick.p.pos.Utemp': self.chan_delta_t_kpp,
                             'cxhw:2.inj.kick.p.neg.Utemp': self.chan_delta_t_kpn,
                             'cxhw:2.inj.prekick.e.pos.Utemp': self.chan_delta_t_pep,
                             'cxhw:2.inj.prekick.e.neg.Utemp': self.chan_delta_t_pen,
                             'cxhw:2.inj.kick.e.pos.Utemp': self.chan_delta_t_kep,
                             'cxhw:2.inj.kick.e.neg.Utemp': self.chan_delta_t_ken}

        self.dict_sigma_t = {'cxhw:2.inj.prekick.p.pos.Utemp': self.chan_sigma_t_ppp,
                             'cxhw:2.inj.prekick.p.neg.Utemp': self.chan_sigma_t_ppn,
                             'cxhw:2.inj.kick.p.pos.Utemp': self.chan_sigma_t_kpp,
                             'cxhw:2.inj.kick.p.neg.Utemp': self.chan_sigma_t_kpn,
                             'cxhw:2.inj.prekick.e.pos.Utemp': self.chan_sigma_t_pep,
                             'cxhw:2.inj.prekick.e.neg.Utemp': self.chan_sigma_t_pen,
                             'cxhw:2.inj.kick.e.pos.Utemp': self.chan_sigma_t_kep,
                             'cxhw:2.inj.kick.e.neg.Utemp': self.chan_sigma_t_ken}

        self.dict_good_chans = {'cxhw:2.inj.prekick.p.pos.Utemp': self.chan_Ugood_ppp,
                                'cxhw:2.inj.prekick.p.neg.Utemp': self.chan_Ugood_ppn,
                                'cxhw:2.inj.kick.p.pos.Utemp': self.chan_Ugood_kpp,
                                'cxhw:2.inj.kick.p.neg.Utemp': self.chan_Ugood_kpn,
                                'cxhw:2.inj.prekick.e.pos.Utemp': self.chan_Ugood_pep,
                                'cxhw:2.inj.prekick.e.neg.Utemp': self.chan_Ugood_pen,
                                'cxhw:2.inj.kick.e.pos.Utemp': self.chan_Ugood_kep,
                                'cxhw:2.inj.kick.e.neg.Utemp': self.chan_Ugood_ken}

        self.dict_temp_chans = {'cxhw:2.inj.prekick.p.pos.Utemp': self.chan_Utemp_ppp,
                                'cxhw:2.inj.prekick.p.neg.Utemp': self.chan_Utemp_ppn,
                                'cxhw:2.inj.kick.p.pos.Utemp': self.chan_Utemp_kpp,
                                'cxhw:2.inj.kick.p.neg.Utemp': self.chan_Utemp_kpn,
                                'cxhw:2.inj.prekick.e.pos.Utemp': self.chan_Utemp_pep,
                                'cxhw:2.inj.prekick.e.neg.Utemp': self.chan_Utemp_pen,
                                'cxhw:2.inj.kick.e.pos.Utemp': self.chan_Utemp_kep,
                                'cxhw:2.inj.kick.e.neg.Utemp': self.chan_Utemp_ken}

        self.list_hist_ppp = [self.chan_histo_x_all_ppp, self.chan_histo_y_all_ppp, self.chan_histo_x_1_ppp,
                              self.chan_histo_y_1_ppp, self.chan_histo_x_2_ppp, self.chan_histo_y_2_ppp,
                              self.chan_histo_x_3_ppp, self.chan_histo_y_3_ppp]
        self.list_hist_ppn = [self.chan_histo_x_all_ppn, self.chan_histo_y_all_ppn, self.chan_histo_x_1_ppn,
                              self.chan_histo_y_1_ppn, self.chan_histo_x_2_ppn, self.chan_histo_y_2_ppn,
                              self.chan_histo_x_3_ppn, self.chan_histo_y_3_ppn]
        self.list_hist_kpp = [self.chan_histo_x_all_kpp, self.chan_histo_y_all_kpp, self.chan_histo_x_1_kpp,
                              self.chan_histo_y_1_kpp, self.chan_histo_x_2_kpp, self.chan_histo_y_2_kpp,
                              self.chan_histo_x_3_kpp, self.chan_histo_y_3_kpp]
        self.list_hist_kpn = [self.chan_histo_x_all_kpn, self.chan_histo_y_all_kpn, self.chan_histo_x_1_kpn,
                              self.chan_histo_y_1_kpn, self.chan_histo_x_2_kpn, self.chan_histo_y_2_kpn,
                              self.chan_histo_x_3_kpn, self.chan_histo_y_3_kpn]
        self.list_hist_pep = [self.chan_histo_x_all_pep, self.chan_histo_y_all_pep, self.chan_histo_x_1_pep,
                              self.chan_histo_y_1_pep, self.chan_histo_x_2_pep, self.chan_histo_y_2_pep,
                              self.chan_histo_x_3_ppp, self.chan_histo_y_3_ppp]
        self.list_hist_pen = [self.chan_histo_x_all_pen, self.chan_histo_y_all_pen, self.chan_histo_x_1_pen,
                              self.chan_histo_y_1_pen, self.chan_histo_x_2_pen, self.chan_histo_y_2_pen,
                              self.chan_histo_x_3_pen, self.chan_histo_y_3_pen]
        self.list_hist_kep = [self.chan_histo_x_all_kep, self.chan_histo_y_all_kep, self.chan_histo_x_1_kep,
                              self.chan_histo_y_1_kep, self.chan_histo_x_2_kep, self.chan_histo_y_2_kep,
                              self.chan_histo_x_3_kep, self.chan_histo_y_3_kep]
        self.list_hist_ken = [self.chan_histo_x_all_ken, self.chan_histo_y_all_ken, self.chan_histo_x_1_ken,
                              self.chan_histo_y_1_ken, self.chan_histo_x_2_ken, self.chan_histo_y_2_ken,
                              self.chan_histo_x_3_ken, self.chan_histo_y_3_ken]

        self.dict_hist = {'cxhw:2.inj.prekick.p.pos.Utemp': self.list_hist_ppp,
                          'cxhw:2.inj.prekick.p.neg.Utemp': self.list_hist_ppn,
                          'cxhw:2.inj.kick.p.pos.Utemp': self.list_hist_kpp,
                          'cxhw:2.inj.kick.p.neg.Utemp': self.list_hist_kpn,
                          'cxhw:2.inj.prekick.e.pos.Utemp': self.list_hist_pep,
                          'cxhw:2.inj.prekick.e.neg.Utemp': self.list_hist_pen,
                          'cxhw:2.inj.kick.e.pos.Utemp': self.list_hist_kep,
                          'cxhw:2.inj.kick.e.neg.Utemp': self.list_hist_ken}

    def hist_tun(self):
        self.chan_histo_range_ppn.setValue(self.spinBox_hist_range.value())
        bins_num = int(2 * self.spinBox_hist_range.value() / self.spinBox_bins_len.value())
        self.chan_n_interp_ppn.setValue(bins_num)  # not this channel yet

    def active_tab(self, chan):
        self.ic_mode = chan.val[0]
        self.tabWidget.setCurrentIndex(self.active_tab_[self.ic_mode])

    def chan_proc(self, chan):
        name = chan.name
        self.dict_count[name] += 1
        if self.dict_count[name] == 3:
            if len(self.dict_hist[name][0].val):
                self.dict_hist_plot[name].clear()
                self.dict_hist_plot[name].plot(self.dict_hist[name][0].val, self.dict_hist[name][1].val,
                                               stepMode=True, fillLevel=0, brush=(0, 0, 255, 150))
                self.dict_hist_plot[name].plot(self.dict_hist[name][2].val, 30*self.dict_hist[name][3].val,
                                               stepMode=True, fillLevel=0, brush=(196, 30, 58, 150))
                self.dict_hist_plot[name].plot(self.dict_hist[name][4].val, 25 * self.dict_hist[name][5].val,
                                               stepMode=True, fillLevel=0, brush=(255, 0, 255, 150))
                self.dict_hist_plot[name].plot(self.dict_hist[name][6].val, 20 * self.dict_hist[name][7].val,
                                               stepMode=True, fillLevel=0, brush=(255, 203, 219, 150))

            if len(self.dict_good_chans[name].val):
                self.dict_imp_plot[name].clear()
                self.dict_imp_plot[name].plot(self.chan_Tgood_ppn.val[275:351],
                                              self.dict_temp_chans[name].val[275:351], pen='r')
                self.dict_imp_plot[name].plot(self.chan_Tgood_ppn.val[275:351],
                                              self.dict_good_chans[name].val[275:351], pen='w')

                self.dict_label_st[name].setText(str(self.dict_sigma_t[name].val))

                g_c = self.green_color
                r_c = self.red_color

                if abs(self.dict_delta_t[name].val) < g_c:
                    self.dict_label_dt[name].setText(str(self.dict_delta_t[name].val))
                    self.dict_label_dt[name].setStyleSheet("background-color:rgb(0, 255, 0);")
                if r_c > abs(self.dict_delta_t[name].val) > g_c:
                    self.dict_label_dt[name].setText(str(self.dict_delta_t[name].val))
                    self.dict_label_dt[name].setStyleSheet("background-color:rgb(255, 179, 0);")
                if abs(self.dict_delta_t[name].val) > r_c:
                    self.dict_label_dt[name].setText(str(self.dict_delta_t[name].val))
                    self.dict_label_dt[name].setStyleSheet("background-color:rgb(255, 0, 0);")

            self.dict_count[name] = 0

    def push_save(self):
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
    app = QApplication(['kicker_monitor'])
    w = KickerPlot()
    sys.exit(app.exec_())
