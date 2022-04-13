#!/usr/bin/env python3

import sys
import os
import numpy as np
from scipy import optimize
from scipy import interpolate
from cservice import CXService
import pycx4.pycda as cda
import json
from kicker_monitor.aux_mod.inf_work_mode import InfWorkMode


class KickerDaem(object):
    def __init__(self):
        super(KickerDaem, self).__init__()
        self.cmd_chan = cda.StrChan("cxhw:2.kickADCproc.inj.cmd", on_update=1, max_nelems=1024)
        self.res_chan = cda.StrChan("cxhw:2.kickADCproc.inj.res", on_update=1, max_nelems=1024)

        self.inj = InfWorkMode("inj", DIR + '/aux_mod/inj_adc_conf.txt', self.data_proc, DIR)
        self.ext = InfWorkMode("ext", DIR + '/aux_mod/ext_adc_conf.txt', self.data_proc, DIR)
        self.n_interp = 20
        self.STEP = 5.6 / self.n_interp  # = 0.28, I need 0.25 for start
        self.time_stamp = 0

        self.cmd_chan.valueMeasured.connect(self.daemon_cmd)
        print("prog_start")

    def data_proc(self, infl):
        # expanding data before correlation
        try:
            tck = interpolate.splrep(infl.good_t_arr, infl.chan_volt_good.val, s=0)
            tck1 = interpolate.splrep(infl.good_t_arr, infl.cur_val, s=0)
            ki_time = np.arange(0.0, 200.0 * 5.6, self.STEP)
            ki_amp_g = interpolate.splev(ki_time, tck, der=0)
            ki_amp_c = interpolate.splev(ki_time, tck1, der=0)

            # if infl.source == 'ext':
            #     print('good', np.argmax(ki_amp_g))
            #     print('current', np.argmax(ki_amp_c))

            # correlation process
            corr = np.correlate(ki_amp_c, ki_amp_g, 'same')
            delta_t = (np.argmax(corr) - (len(corr) / 2)) * self.STEP
            # print(delta_t, np.argmax(ki_amp_c), np.argmax(ki_amp_g), infl.chan_volt_good.name)
            if abs(delta_t) < 100:
                # gaussfit = lambda p, x: p[0] * np.exp(-(((x - p[1]) / p[2]) ** 2) / 2) + p[3]  # signal peak and ampl
                # errfunc = lambda p, x, y: gaussfit(p, x) - u_data
                # p = [0.4, 150, 90, 0]
                # p1, success = optimize.leastsq(errfunc, p[:], args=(time, u_data))
                delta_t_arr = infl.chan_delta_arr.val
                if len(delta_t_arr) > 99:
                    delta_t_arr = np.delete(delta_t_arr, 0)
                delta_t_arr = np.append(delta_t_arr, delta_t)
                infl.chan_delta_arr.setValue(delta_t_arr)
        except Exception as exc:
            pass

    def daemon_cmd(self, chan):
        cmd = chan.val
        if cmd:
            cdict = json.loads(cmd)
            if cdict['cmd'] == 'save_inj':
                self.inj.load_new_good_vals()
                self.cmd_chan.setValue(json.dumps({'cmd': 'ready'}))
            elif cdict['cmd'] == 'save_ext':
                self.ext.load_new_good_vals()
                self.cmd_chan.setValue(json.dumps({'cmd': 'ready'}))
            if cdict['cmd'] == 'stg_dflt_inj':
                self.inj.adc200_kkr_default()
                self.cmd_chan.setValue(json.dumps({'cmd': 'ready'}))
            elif cdict['cmd'] == 'stg_dflt_ext':
                self.ext.adc200_kkr_default()
                self.cmd_chan.setValue(json.dumps({'cmd': 'ready'}))

DIR = os.getcwd()

# class KMService(CXService):
#     def main(self):
#         print('run main')
#         self.w = KickerDaem()
#
#     def clean(self):
#         self.log_str('exiting kicker_monitor')
#
# km = KMService("infl_monitor")

if __name__ == "__main__":
    w = KickerDaem()
    cda.main_loop()
