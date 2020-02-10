#!/usr/bin/env python3

from PyQt5.QtWidgets import QApplication
import sys

import numpy as np
import os
from scipy import optimize
from scipy import interpolate
from aux.service_daemon import QtService
import pycx4.qcda as cda
import json
from kicker_monitor.aux_mod.inf_work_mode import InfWorkMode


class KickerDaem(object):
    def __init__(self):
        super(KickerDaem, self).__init__()

        self.cmd_chan = cda.StrChan("cxhw:2.kickADCproc.inj.cmd", on_update=1, max_nelems=1024)
        self.res_chan = cda.StrChan("cxhw:2.kickADCproc.inj.res", on_update=1, max_nelems=1024)

        self.inj = InfWorkMode("inj", self.data_proc, os.getcwd())

        self.n_interp = 20
        self.STEP = 5.6 / self.n_interp  # = 0.28, I need 0.25 for start

        self.time_stamp = 0

        self.ki_time = np.zeros((75 * self.n_interp,), dtype=np.double)
        self.ki_amp_g = np.zeros((75 * self.n_interp,), dtype=np.double)  # g = good
        self.ki_amp_c = np.zeros((75 * self.n_interp,), dtype=np.double)  # c = compare

        self.cmd_chan.valueMeasured.connect(self.daemon_cmd)
        print("prog_start")

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
        # print(chan.val)
        cmd = chan.val
        if cmd:
            cdict = json.loads(cmd)
            if cdict['cmd'] == 'save_inj':
                self.inj.load_new_good_vals()
                self.cmd_chan.setValue(json.dumps({'cmd': 'ready'}))
            elif cdict['cmd'] == 'save_ext':
                self.cmd_chan.setValue(json.dumps({'cmd': 'ready'}))
            if cdict['cmd'] == 'stg_dflt_inj':
                self.inj.adc200_kkr_default()
                self.cmd_chan.setValue(json.dumps({'cmd': 'ready'}))
            elif cdict['cmd'] == 'stg_dflt_ext':
                self.cmd_chan.setValue(json.dumps({'cmd': 'ready'}))


class KMService(QtService):
    def main(self):
        print('run main')
        self.w = KickerDaem()

    def clean(self):
        self.log_str('exiting kicker_monitor')

# if __name__ == "__main__":
#     app = QApplication(['kicker_monitor'])
#     w = KickerDaem()
#     sys.exit(app.exec_())


km = KMService("infl_monitor")
