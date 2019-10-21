#!/usr/bin/env python3

import pycx4.qcda as cda


class InfDef:
    def __init__(self, data_receiver, work_mode, inf_type):
        super(InfDef, self).__init__()
        self.data_receiver = data_receiver

        self.chan_time_good = cda.VChan("cxhw:2." + work_mode + "." + inf_type + ".Tgood", max_nelems=1024)
        self.chan_volt_good = cda.VChan("cxhw:2." + work_mode + "." + inf_type + ".Ugood", max_nelems=1024)
        self.chan_time_temp = cda.VChan("cxhw:2." + work_mode + "." + inf_type + ".Ttemp", max_nelems=1024)
        self.chan_volt_temp = cda.VChan("cxhw:2." + work_mode + "." + inf_type + ".Utemp", max_nelems=1024)
        self.chan_n_interp = cda.DChan("cxhw:2." + work_mode + "." + inf_type + ".n_interp")
        self.chan_delta_arr = cda.VChan("cxhw:2." + work_mode + "." + inf_type + ".delta_t_array", max_nelems=200)

    def data_proc(self, chan):
        self.data_receiver(chan.val)
