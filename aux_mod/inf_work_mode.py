#!/usr/bin/env python3

import pycx4.pycda as cda
import numpy as np
import os
from kicker_monitor.aux_mod.adc import ADC
from kicker_monitor.aux_mod.inflector_dev import InfDef
from kicker_monitor.aux_mod.config_parser import load_config


class InfWorkMode:
    def __init__(self, cycle_part, conf_name, data_proc, dir_d):
        super(InfWorkMode, self).__init__()
        self.dir = dir_d + '/km_'
        self.ic_mode = ''
        self.active_tab = {'p': 1, 'e': 0}

        self.data_proc = data_proc
        self.cycle_part = cycle_part
        adc_list, p_names, e_names = load_config(conf_name)
        self.adcs = [ADC(self.data_receiver, name) for name in adc_list]
        self.inflectors = {"p": {key: InfDef(cycle_part, val) for key, val in p_names.items()},
                           "e": {key: InfDef(cycle_part, val) for key, val in e_names.items()}}

        self.chan_ic_mode = cda.StrChan("cxhw:0.k500.modet", max_nelems=4)
        self.chan_sel_all = cda.DChan("cxhw:18.kkr_sel_all.0")

        self.chan_ic_mode.valueChanged.connect(self.kkr_sel)

    def kkr_sel(self, chan):
        self.ic_mode = chan.val[0]
        self.chan_sel_all.setValue(self.active_tab[self.ic_mode])

    def data_receiver(self, val, i_type):
        self.inflectors[self.ic_mode][i_type].chan_volt_temp.setValue(val)
        self.inflectors[self.ic_mode][i_type].cur_val = val
        good_val = self.inflectors[self.ic_mode][i_type].chan_volt_good.val
        if len(good_val):
            self.data_proc(self.inflectors[self.ic_mode][i_type])
        else:
            self.load_new_good_vals()

    def adc200_kkr_default(self):
        for adc in self.adcs:
            adc.adc_set_def()

    def load_new_good_vals(self):
        if self.ic_mode == "e":
            filename = self.dir + self.cycle_part + "/good_chan_electron"
        elif self.ic_mode == "p":
            filename = self.dir + self.cycle_part + "/good_chan_positron"
        else:
            print("WTF")
        try:
            data = np.loadtxt(filename, skiprows=1)
            i = 0
            for key, infl in self.inflectors[self.ic_mode].items():
                infl.chan_volt_good.setValue(data[i])
                i += 1
        except Exception as exc:
            print(exc, 'mode is not uploaded yet')
