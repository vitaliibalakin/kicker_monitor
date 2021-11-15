from scipy import interpolate
import numpy as np

import matplotlib.pyplot as plt

a = np.loadtxt('/home/vbalakin/PycharmProjects/kicker_monitor/km_inj/good_chan_electron', skiprows=1)
test_data = a[0]
test_data_2 = np.roll(a[0], 10)
test_time = np.arange(0.0, 200 * 5.6, 5.6)
ki_time = np.arange(0.0, 200.0 * 5.6, 5.6 / 20)

tck = interpolate.splrep(test_time, test_data, s=0)
tck1 = interpolate.splrep(test_time, test_data_2, s=0)

ki_amp_g = interpolate.splev(ki_time, tck, der=0)
ki_amp_c = interpolate.splev(ki_time, tck1, der=0)

corr = np.correlate(ki_amp_g, ki_amp_c, 'same')
delta_t = (np.argmax(corr) - (len(corr) / 2)) * 5.6 / 20

print(delta_t)

plt.figure()
plt.plot(ki_time, ki_amp_c, ki_time, ki_amp_g)
plt.show()