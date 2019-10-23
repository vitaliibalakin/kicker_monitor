#!/usr/bin/env python3

import pycx4.qcda as cda
import numpy as np


class InfDef:
    def __init__(self, source, inf_type):
        super(InfDef, self).__init__()
        self.source = source
        self.inf_type = inf_type
        self.cur_val = np.ndarray([])

        # make linspace
        self.good_t_arr = np.zeros((76,), dtype=np.double)  # time array
        for i in range(0, 76):
            self.good_t_arr[i] = 5.6 * i

        # self.chan_time_good = cda.VChan("cxhw:2." + source + "." + inf_type + ".Tgood", max_nelems=1024)
        # self.chan_time_temp = cda.VChan("cxhw:2." + source + "." + inf_type + ".Ttemp", max_nelems=1024)
        self.chan_volt_good = cda.VChan("cxhw:2." + source + "." + inf_type + ".Ugood", max_nelems=1024)
        self.chan_volt_temp = cda.VChan("cxhw:2." + source + "." + inf_type + ".Utemp", max_nelems=1024)
        self.chan_n_interp = cda.DChan("cxhw:2." + source + "." + inf_type + ".n_interp")
        self.chan_delta_arr = cda.VChan("cxhw:2." + source + "." + inf_type + ".delta_t_array", max_nelems=200)

    def get_good_volt_val(self):
        pass
