import re

def load_config(conf_name):
    conf_file = open(conf_name, "r")
    configuration = conf_file.readlines()
    control_sum = 0

    def load_adc(i_b, data):
        d_str = ''
        d_list = []
        while True:
            d_str += data[i_b][:-1]
            i_b += 1
            if data[i_b] == '[end]\n' or data[i_b] == '[end]':
                d_list = d_str.split(',')
                return i_b, d_list

    def load_names_rel(i_b, data):
        chans_sett = {}
        while True:
            tmp = re.findall(r'(\S+=\S+)', data[i_b])[0].split('=')
            chans_sett[tmp[0]] = tmp[-1]
            i_b += 1
            if data[i_b] == '[end]\n' or data[i_b] == '[end]':
                return i_b, chans_sett

    i = 0
    while i < len(configuration):
        if configuration[i] == '[adc_list]\n':
            i_next, adc_list = load_adc(i + 1, configuration)
            i = i_next
        elif configuration[i] == '[p_names_rel]\n':
            i_next, p_names = load_names_rel(i + 1, configuration)
            i = i_next
        elif configuration[i] == '[e_names_rel]\n':
            i_next, e_names = load_names_rel(i + 1, configuration)
            i = i_next
        i += 1

    return adc_list, p_names, e_names
