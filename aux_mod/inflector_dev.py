#!/usr/bin/env python3

import pycx4.pycda as cda
import numpy as np


class InfDef:
    def __init__(self, source, inf_type):
        super(InfDef, self).__init__()
        self.source = source
        self.inf_type = inf_type
        self.cur_val = np.ndarray([])

        # make linspace
        self.good_t_arr = np.arange(0.0, 200.0, 1) * 5.6

        # self.chan_time_good = cda.VChan("cxhw:2." + source + "." + inf_type + ".Tgood", max_nelems=1024)
        # self.chan_time_temp = cda.VChan("cxhw:2." + source + "." + inf_type + ".Ttemp", max_nelems=1024)
        self.chan_volt_good = cda.VChan("cxhw:2." + source + "." + inf_type + ".Ugood", max_nelems=200)
        self.chan_volt_temp = cda.VChan("cxhw:2." + source + "." + inf_type + ".Utemp", max_nelems=200)
        self.chan_n_interp = cda.DChan("cxhw:2." + source + "." + inf_type + ".n_interp")
        self.chan_delta_arr = cda.VChan("cxhw:2." + source + "." + inf_type + ".delta_t_array", max_nelems=200)

    def load_new_good_vals(self):
        pass
