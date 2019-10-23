#!/usr/bin/env python3

from PyQt5.QtWidgets import QApplication
import sys

import numpy as np
from scipy import optimize
from scipy import interpolate
# from aux.service_daemon import QtService
import os
import pycx4.qcda as cda
import json
from kicker_monitor.aux.adc import ADC
from kicker_monitor.aux.inflector_dev import InfDef


class KickerDaem(object):
    def __init__(self):
        super(KickerDaem, self).__init__()

        self.adcs = [ADC(self.data_receiver, "adc200_kkr1"), ADC(self.data_receiver, "adc200_kkr2")]
        self.inflectors = {"p": {"adc200_kkr1.line1": InfDef("inj", "prekick.p.pos"),
                                 "adc200_kkr1.line2": InfDef("inj", "prekick.p.neg"),
                                 "adc200_kkr2.line1": InfDef("inj", "kick.p.pos"),
                                 "adc200_kkr2.line2": InfDef("inj", "kick.p.neg")},
                           "e": {"adc200_kkr1.line1": InfDef("inj", "prekick.e.pos"),
                                 "adc200_kkr1.line2": InfDef("inj", "prekick.e.neg"),
                                 "adc200_kkr2.line1": InfDef("inj", "kick.e.pos"),
                                 "adc200_kkr2.line2": InfDef("inj", "kick.e.neg")}}

        self.chan_ic_mode = cda.StrChan("cxhw:0.k500.modet", max_nelems=4)
        self.chan_sel_all = cda.DChan("cxhw:18.kkr_sel_all.0")
        self.cmd_chan = cda.StrChan("cxhw:2.kickADCproc.inj.cmd", on_update=1, max_nelems=1024)
        self.res_chan = cda.StrChan("cxhw:2.kickADCproc.inj.res", on_update=1, max_nelems=1024)

        self.u_data_good = np.zeros((76,), dtype=np.double)
        self.u_data = np.zeros((76,), dtype=np.double)
        self.t_data_good = np.zeros((76,), dtype=np.double)
        self.fit_data = np.zeros((76,), dtype=np.double)

        self.n_interp = 20
        self.STEP = 0.25  # 5.6 / self.n_interp = 0.28, I need 0.25 for start

        self.ic_mode = ''
        self.time_stamp = 0

        self.ki_time = np.zeros((75 * self.n_interp,), dtype=np.double)
        self.ki_amp_g = np.zeros((75 * self.n_interp,), dtype=np.double)  # g = good
        self.ki_amp_c = np.zeros((75 * self.n_interp,), dtype=np.double)  # c = compare

        self.active_tab = {'p': 1, 'e': 0}

        self.cmd_chan.valueMeasured.connect(self.daemon_cmd)
        self.chan_ic_mode.valueChanged.connect(self.kkr_sel)
        print("prog_start")

    def data_receiver(self, val, i_type):
        self.inflectors[self.ic_mode][i_type].chan_volt_temp.setValue(val)
        self.inflectors[self.ic_mode][i_type].cur_val = val
        good_val = self.inflectors[self.ic_mode][i_type].chan_volt_good.val
        if len(good_val):
            self.data_proc(self.inflectors[self.ic_mode][i_type])
        else:
            if self.ic_mode == "e":
                filename = os.getcwd() + "/km_injection" + "/good_chan_electron"
            elif self.ic_mode == "p":
                filename = os.getcwd() + "/km_injection" + "/good_chan_positron"
            else:
                filename = "WTF"
            data = np.loadtxt(filename, skiprows=1)
            i = 0
            for key, infl in self.inflectors[self.ic_mode].items():
                infl.chan_volt_good.setValue(data[i])
                i += 1

    def adc200_kkr_default(self):
        for adc in self.adcs:
            adc.adc_set_def()

    def kkr_sel(self, chan):
        self.ic_mode = chan.val[0]
        self.chan_sel_all.setValue(self.active_tab[self.ic_mode])

    def data_proc(self, infl):
        self.expanding_data(infl.good_t_arr, infl.chan_volt_good.val[305:381], infl.cur_val[305:381])
        self.correlation(infl.chan_delta_arr, infl.good_t_arr, infl.cur_val[305:381])

    def expanding_data(self, t_data_good, u_data_good, u_data):
        tck = interpolate.splrep(t_data_good, u_data_good, s=0)
        tck1 = interpolate.splrep(t_data_good, u_data, s=0)
        self.ki_time = np.arange(0.0, 375.0, self.STEP)
        self.ki_amp_g = interpolate.splev(self.ki_time, tck, der=0)
        self.ki_amp_c = interpolate.splev(self.ki_time, tck1, der=0)

    def correlation(self, chan_dt_arr, time, u_data):
        corr = np.correlate(self.ki_amp_c, self.ki_amp_g, 'same')
        delta_t = (corr.argmax() - (len(corr) / 2)) * self.STEP
        # corr1 = np.correlate(self.ki_amp_c, self.ki_amp_g, 'full')
        # delta_t1 = (corr1.argmax() - (len(corr1) / 2)) * self.STEP
        if abs(delta_t) < 20:
            # gaussfit = lambda p, x: p[0] * np.exp(-(((x - p[1]) / p[2]) ** 2) / 2) + p[3]  # signal peak and ampl
            # errfunc = lambda p, x, y: gaussfit(p, x) - u_data
            # p = [0.4, 150, 90, 0]
            # p1, success = optimize.leastsq(errfunc, p[:], args=(time, u_data))
            delta_t_arr = chan_dt_arr.val
            if len(delta_t_arr) > 99:
                delta_t_arr = np.delete(delta_t_arr, 0)
            delta_t_arr = np.append(delta_t_arr, delta_t)
            chan_dt_arr.setValue(delta_t_arr)

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
        if not len(self.cmd_chan.val):
            self.cmd_chan.setValue(json.dumps({'cmd': 'ready'}))
            self.res_chan.setValue(json.dumps({'res': 'good', 'last_cmd': 'start', 'time': 'who knows?'}))


# class KMService(QtService):
#     def main(self):
#         print('run main')
#         self.w = KickerDaem()
#
#     def clean(self):
#         self.log_str('exiting kicker_monitor')

if __name__ == "__main__":
    app = QApplication(['kicker_monitor'])
    w = KickerDaem()
    sys.exit(app.exec_())


# km = KMService("kicker_monitor")
