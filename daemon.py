#!/usr/bin/env python3

import numpy as np
from scipy import optimize
from scipy import interpolate
from aux.service_daemon import QtService
import os
import pycx4.qcda as cda
import json
from kicker_monitor.aux.adc import ADC


class KickerApp(object):
    def __init__(self):
        super(KickerApp, self).__init__()
        self.init_chans()

        self.adcs = [ADC(self.data_receiver, "adc200_kkr1"), ADC(self.data_receiver, "adc200_kkr2")]

        self.chan_ic_mode = cda.StrChan("cxhw:0.k500.modet", max_nelems=4)
        self.chan_sel_all = cda.DChan("cxhw:18.kkr_sel_all.0")
        self.cmd_chan = cda.StrChan("cxhw:2.kickADCproc.inj.cmd", on_update=1, max_nelems=1024)
        self.res_chan = cda.StrChan("cxhw:2.kickADCproc.inj.res", on_update=1, max_nelems=1024)

        self.list_GC = [self.chan_Ugood_ppn, self.chan_Ugood_kpn, self.chan_Ugood_ppp, self.chan_Ugood_kpp,
                        self.chan_Ugood_pen, self.chan_Ugood_ken, self.chan_Ugood_pep, self.chan_Ugood_kep]
        self.list_TC = [self.chan_Utemp_ppn, self.chan_Utemp_kpn, self.chan_Utemp_ppp, self.chan_Utemp_kpp,
                        self.chan_Utemp_pen, self.chan_Utemp_ken, self.chan_Utemp_pep, self.chan_Utemp_kep]

        self.u_data_good = np.zeros((76,), dtype=np.double)
        self.u_data = np.zeros((76,), dtype=np.double)
        self.t_data_good = np.zeros((76,), dtype=np.double)
        self.fit_data = np.zeros((76,), dtype=np.double)

        self.n_interp = 20
        self.STEP = 5.6 / self.n_interp

        self.ic_mode = ''
        self.time_stamp = 0

        self.ki_time = np.zeros((75 * self.n_interp,), dtype=np.double)
        self.ki_amp_g = np.zeros((75 * self.n_interp,), dtype=np.double)  # g = good
        self.ki_amp_c = np.zeros((75 * self.n_interp,), dtype=np.double)  # c = compare

        self.T = np.zeros((1024,), dtype=np.double)                       # time array
        for i in range(0, 1024):
            self.T[i] = 5.6 * i
        self.active_tab = {'p': 1, 'e': 0}

        self.cmd_chan.valueMeasured.connect(self.daemon_cmd)
        self.chan_ic_mode.valueChanged.connect(self.kkr_sel)
        print("prog_start")

    def data_receiver(self):
        pass

    def init_chans(self):
        self.chan_Tgood_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.Tgood", max_nelems=1024)  # positrons "-" prekick
        self.chan_Ugood_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.Ugood", max_nelems=1024)
        self.chan_Ttemp_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.Ttemp", max_nelems=1024)
        self.chan_Utemp_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.Utemp", max_nelems=1024)
        self.chan_n_interp_ppn = cda.DChan("cxhw:2.inj.prekick.p.neg.n_interp")
        self.chan_delta_arr_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.delta_t_array", max_nelems=200)

        self.chan_Tgood_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.Tgood", max_nelems=1024)  # positrons "-" prekick
        self.chan_Ugood_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.Ugood", max_nelems=1024)
        self.chan_Ttemp_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.Ttemp", max_nelems=1024)
        self.chan_Utemp_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.Utemp", max_nelems=1024)
        self.chan_n_interp_ppn = cda.DChan("cxhw:2.inj.prekick.p.neg.n_interp")
        self.chan_delta_arr_ppn = cda.VChan("cxhw:2.inj.prekick.p.neg.delta_t_array", max_nelems=200)

        self.chan_Tgood_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.Tgood", max_nelems=1024)  # positrons "-" kick
        self.chan_Ugood_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.Ugood", max_nelems=1024)
        self.chan_Ttemp_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.Ttemp", max_nelems=1024)
        self.chan_Utemp_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.Utemp", max_nelems=1024)
        self.chan_n_interp_kpn = cda.DChan("cxhw:2.inj.kick.p.neg.n_interp")
        self.chan_delta_arr_kpn = cda.VChan("cxhw:2.inj.kick.p.neg.delta_t_array", max_nelems=200)

        self.chan_Tgood_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.Tgood", max_nelems=1024)  # positrons "+" prekick
        self.chan_Ugood_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.Ugood", max_nelems=1024)
        self.chan_Ttemp_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.Ttemp", max_nelems=1024)
        self.chan_Utemp_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.Utemp", max_nelems=1024)
        self.chan_n_interp_ppp = cda.DChan("cxhw:2.inj.prekick.p.pos.n_interp")
        self.chan_delta_arr_ppp = cda.VChan("cxhw:2.inj.prekick.p.pos.delta_t_array", max_nelems=200)

        self.chan_Tgood_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.Tgood", max_nelems=1024)  # positrons "+" kick
        self.chan_Ugood_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.Ugood", max_nelems=1024)
        self.chan_Ttemp_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.Ttemp", max_nelems=1024)
        self.chan_Utemp_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.Utemp", max_nelems=1024)
        self.chan_n_interp_kpp = cda.DChan("cxhw:2.inj.kick.p.pos.n_interp")
        self.chan_delta_arr_kpp = cda.VChan("cxhw:2.inj.kick.p.pos.delta_t_array", max_nelems=200)

        self.chan_Tgood_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.Tgood", max_nelems=1024)  # electrons "-" prekick
        self.chan_Ugood_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.Ugood", max_nelems=1024)
        self.chan_Ttemp_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.Ttemp", max_nelems=1024)
        self.chan_Utemp_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.Utemp", max_nelems=1024)
        self.chan_n_interp_pen = cda.DChan("cxhw:2.inj.prekick.e.neg.n_interp")
        self.chan_delta_arr_pen = cda.VChan("cxhw:2.inj.prekick.e.neg.delta_t_array", max_nelems=200)

        self.chan_Tgood_ken = cda.VChan("cxhw:2.inj.kick.e.neg.Tgood", max_nelems=1024)  # electrons "-" kick
        self.chan_Ugood_ken = cda.VChan("cxhw:2.inj.kick.e.neg.Ugood", max_nelems=1024)
        self.chan_Ttemp_ken = cda.VChan("cxhw:2.inj.kick.e.neg.Ttemp", max_nelems=1024)
        self.chan_Utemp_ken = cda.VChan("cxhw:2.inj.kick.e.neg.Utemp", max_nelems=1024)
        self.chan_n_interp_ken = cda.DChan("cxhw:2.inj.kick.e.neg.n_interp")
        self.chan_delta_arr_ken = cda.VChan("cxhw:2.inj.kick.e.neg.delta_t_array", max_nelems=200)

        self.chan_Tgood_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.Tgood", max_nelems=1024)  # electrons "+" prekick
        self.chan_Ugood_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.Ugood", max_nelems=1024)
        self.chan_Ttemp_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.Ttemp", max_nelems=1024)
        self.chan_Utemp_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.Utemp", max_nelems=1024)
        self.chan_n_interp_pep = cda.DChan("cxhw:2.inj.prekick.e.pos.n_interp")
        self.chan_delta_arr_pep = cda.VChan("cxhw:2.inj.prekick.e.pos.delta_t_array", max_nelems=200)

        self.chan_Tgood_kep = cda.VChan("cxhw:2.inj.kick.e.pos.Tgood", max_nelems=1024)  # electrons "+" kick
        self.chan_Ugood_kep = cda.VChan("cxhw:2.inj.kick.e.pos.Ugood", max_nelems=1024)
        self.chan_Ttemp_kep = cda.VChan("cxhw:2.inj.kick.e.pos.Ttemp", max_nelems=1024)
        self.chan_Utemp_kep = cda.VChan("cxhw:2.inj.kick.e.pos.Utemp", max_nelems=1024)
        self.chan_n_interp_kep = cda.DChan("cxhw:2.inj.kick.e.pos.n_interp")
        self.chan_delta_arr_kep = cda.VChan("cxhw:2.inj.kick.e.pos.delta_t_array", max_nelems=200)

        self.dict_good_chans = {'cxhw:18.adc200_kkr1.line1p': self.chan_Ugood_ppp,
                                'cxhw:18.adc200_kkr1.line2p': self.chan_Ugood_ppn,
                                'cxhw:18.adc200_kkr2.line1p': self.chan_Ugood_kpp,
                                'cxhw:18.adc200_kkr2.line2p': self.chan_Ugood_kpn,
                                'cxhw:18.adc200_kkr1.line1e': self.chan_Ugood_pep,
                                'cxhw:18.adc200_kkr1.line2e': self.chan_Ugood_pen,
                                'cxhw:18.adc200_kkr2.line1e': self.chan_Ugood_kep,
                                'cxhw:18.adc200_kkr2.line2e': self.chan_Ugood_ken}

        self.dict_temp_chans = {'cxhw:18.adc200_kkr1.line1p': self.chan_Utemp_ppp,
                                'cxhw:18.adc200_kkr1.line2p': self.chan_Utemp_ppn,
                                'cxhw:18.adc200_kkr2.line1p': self.chan_Utemp_kpp,
                                'cxhw:18.adc200_kkr2.line2p': self.chan_Utemp_kpn,
                                'cxhw:18.adc200_kkr1.line1e': self.chan_Utemp_pep,
                                'cxhw:18.adc200_kkr1.line2e': self.chan_Utemp_pen,
                                'cxhw:18.adc200_kkr2.line1e': self.chan_Utemp_kep,
                                'cxhw:18.adc200_kkr2.line2e': self.chan_Utemp_ken}

        self.dict_delta_arr = {'cxhw:18.adc200_kkr1.line1p': self.chan_delta_arr_ppp,
                               'cxhw:18.adc200_kkr1.line2p': self.chan_delta_arr_ppn,
                               'cxhw:18.adc200_kkr2.line1p': self.chan_delta_arr_kpp,
                               'cxhw:18.adc200_kkr2.line2p': self.chan_delta_arr_kpn,
                               'cxhw:18.adc200_kkr1.line1e': self.chan_delta_arr_pep,
                               'cxhw:18.adc200_kkr1.line2e': self.chan_delta_arr_pen,
                               'cxhw:18.adc200_kkr2.line1e': self.chan_delta_arr_kep,
                               'cxhw:18.adc200_kkr2.line2e': self.chan_delta_arr_ken}

    def adc200_kkr_default(self):
        for adc in self.adcs:
            adc.adc_set_def()

    def kkr_sel(self, chan):
        self.ic_mode = chan.val[0]
        self.chan_sel_all.setValue(self.active_tab[self.ic_mode])

    def data_proc(self, chan):
        self.chans_check()
        name = chan.name + self.ic_mode
        if len(self.dict_good_chans[name].val):
            self.dict_temp_chans[name].setValue(chan.val)
            self.expanding_data(self.chan_Tgood_ppn.val[0:76], self.dict_good_chans[name].val[305:381],
                                chan.val[305:381])
            self.correlation(name, self.chan_Tgood_ppn.val[0:76], chan.val[305:381])

    def expanding_data(self, t_data_good, u_data_good, u_data):
        tck = interpolate.splrep(t_data_good, u_data_good, s=0)
        tck1 = interpolate.splrep(t_data_good, u_data, s=0)
        self.ki_time = np.arange(0.0, 375.0, 0.25)
        self.ki_amp_g = interpolate.splev(self.ki_time, tck, der=0)
        self.ki_amp_c = interpolate.splev(self.ki_time, tck1, der=0)

    def correlation(self, name, t_data_good, u_data):
        corr = np.correlate(self.ki_amp_c, self.ki_amp_g, 'same')
        corr1 = np.correlate(self.ki_amp_c, self.ki_amp_g, 'full')
        delta_t = (corr.argmax() - (len(corr) / 2)) * self.STEP
        delta_t1 = (corr1.argmax() - (len(corr1) / 2)) * self.STEP
        # print(delta_t, delta_t1)
        if abs(delta_t) < 20:
            gaussfit = lambda p, x: p[0] * np.exp(-(((x - p[1]) / p[2]) ** 2) / 2) + p[3]  # signal peak and ampl
            errfunc = lambda p, x, y: gaussfit(p, x) - u_data
            p = [0.4, 150, 90, 0]
            p1, success = optimize.leastsq(errfunc, p[:], args=(t_data_good, u_data))

            '''gaussfit = lambda p2, x: p2[0] * np.exp(-(((x - p2[1]) / p2[2]) ** 2) / 2) + p2[3]
            errfunc1 = lambda p2, x, y: gaussfit(p2, x) - u_data_good
            p2 = [0.4, 150, 90, 0]
            p3, success = optimize.leastsq(errfunc1, p2[:], args=(t_data_good, u_data_good))'''

            # if abs(p1[0]) < 0.55:
            #    self.chan_abs_a_good_ppn.setValue(round((p3[0] - p[0]), 6))
            self.sigma_proc(delta_t, name)

    def daemon_cmd(self, chan):
        print('daemon_cmd')
        cmd = chan.val
        if cmd:
            cdict = json.loads(cmd)
            if cdict['cmd'] == 'save':
                self.cmd_chan.setValue(json.dumps({'cmd': 'ready'}))
            if cdict['cmd'] == 'stg_dflt':
                self.adc200_kkr_default()
                self.cmd_chan.setValue(json.dumps({'cmd': 'ready'}))

    def chans_check(self):
        check_p = self.chan_Ugood_ppn.val
        check_e = self.chan_Ugood_pen.val
        if not len(self.cmd_chan.val):
            self.cmd_chan.setValue(json.dumps({'cmd': 'ready'}))
            self.res_chan.setValue(json.dumps({'res': 'good', 'last_cmd': 'start', 'time': 'who knows?'}))

        if not (len(check_e) and len(check_p)):
            print("chans_check")
            list_GC = self.list_GC
            self.chan_Tgood_ppn.setValue(self.T)
            self.chan_n_interp_ppn.setValue(10)

            # loading for electons
            saved_data = np.loadtxt(DIR + "/good_chan_electron", skiprows=1)
            for i in range(4, 8):
                list_GC[i].setValue(saved_data[i-4])

            # loading for positons
            saved_data = np.loadtxt(DIR + "/good_chan_positron", skiprows=1)
            for i in range(0, 4):
                list_GC[i].setValue(saved_data[i])

    def sigma_proc(self, delta_t, name):
        delta_t_arr = self.dict_delta_arr[name].val
        if delta_t_arr.__len__() > 99:
            delta_t_arr = np.delete(delta_t_arr, 0)
        delta_t_arr = np.append(delta_t_arr, delta_t)
        sigma1 = np.multiply(delta_t_arr, delta_t_arr)
        sigma = np.sqrt(np.sum(sigma1)/delta_t_arr.__len__())
        self.dict_delta_arr[name].setValue(delta_t_arr)


class KMService(QtService):
    def main(self):
        print('run main')
        self.w = KickerApp()

    def clean(self):
        self.log_str('exiting kicker_monitor')


DIR = os.getcwd() + '/'
km = KMService("kicker_monitor")
