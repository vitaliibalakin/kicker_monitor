#!/usr/bin/env python3

import pycx4.pycda as cda


class ADC:
    def __init__(self, data_receiver, name, n_elems=200):
        super(ADC, self).__init__()
        self.name = name
        self.data_receiver = data_receiver

        self.chan_line_pos = cda.VChan("cxhw:18." + name + ".line1", max_nelems=n_elems)
        self.chan_line_neg = cda.VChan("cxhw:18." + name + ".line2", max_nelems=n_elems)
        self.chan_adc200_ptsofs = cda.DChan("cxhw:18." + name + ".ptsofs")
        self.chan_adc200_numpts = cda.DChan("cxhw:18." + name + ".numpts")
        self.chan_adc200_timing = cda.DChan("cxhw:18." + name + ".timing")
        self.chan_adc200_frq_div = cda.DChan("cxhw:18." + name + ".frqdiv")
        self.chan_range_pos = cda.DChan("cxhw:18." + name + ".range1")
        self.chan_range_neg = cda.DChan("cxhw:18." + name + ".range2")

        self.chan_line_pos.valueMeasured.connect(self.data_proc)
        self.chan_line_neg.valueMeasured.connect(self.data_proc)

    def data_proc(self, chan):
        self.data_receiver(chan.val, self.name + "." + chan.name.split(".")[-1])

    def adc_set_def(self):
        self.chan_adc200_ptsofs.setValue(0)
        self.chan_adc200_numpts.setValue(200)
        self.chan_adc200_timing.setValue(1)
        self.chan_adc200_frq_div.setValue(0)
        self.chan_range_pos.setValue(1)
        self.chan_range_neg.setValue(1)
