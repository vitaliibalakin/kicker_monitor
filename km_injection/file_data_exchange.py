#!/usr/bin/env python3

import numpy as np
import datetime


class FileDataExchange:
    def __init__(self, directory, data_receiver):
        super(FileDataExchange, self).__init__()
        self.dir = directory
        self.data_receiver = data_receiver

    def save_file(self, data_chans, label, source):
        data = []
        for essence in data_chans:
            data.append(essence.chan_data.val)
        time_stamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if source == "e":
            filename = self.dir + "/good_chan_electron"
        elif source == "p":
            filename = self.dir + "/good_chan_positron"
        else:
            filename = "WTF"
        np.savetxt(filename, np.stack(data, axis=0), header=str(time_stamp))

        for chan in data_chans:
            self.data_receiver(chan.chan_data.val, chan.source, chan.inf_type, 'eq')
        label.setText(time_stamp)

    def load_file(self, source, label):
        inf_types = ["pre_pos", "pre_neg", "kick_pos", "kick_neg"]
        if source == "e":
            filename = self.dir + "/good_chan_electron"
        elif source == "p":
            filename = self.dir + "/good_chan_positron"
        else:
            filename = "WTF"
        data = np.loadtxt(filename, skiprows=1)
        for i in range(len(inf_types)):
            self.data_receiver(data[i], source, inf_types[i], 'eq')
        time_stamp = open(filename)
        label.setText(time_stamp.readline())
        time_stamp.close()
