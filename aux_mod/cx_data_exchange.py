#!/usr/bin/env python3

import pycx4.qcda as cda


class CXDataExchange:
    def __init__(self, data_receiver, chan_name, source, inf_type, n_elems=1024):
        super(CXDataExchange, self).__init__()
        self.data_receiver = data_receiver
        self.source = source
        self.inf_type = inf_type
        self.chan_data = cda.VChan(chan_name, max_nelems=n_elems)

        self.chan_data.valueMeasured.connect(self.data_proc)

    def data_proc(self, chan):
        # print(chan.name, self.source, self.inf_type)
        self.data_receiver(chan.val, self.source, self.inf_type)
