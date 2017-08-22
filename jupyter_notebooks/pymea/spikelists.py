import pandas as pd
import numpy as np
import itertools as it

electrode_map = {
    '1': ['18', '28', '38', '48', '58', '68', '78', '88',
          '17', '27', '37', '47', '57', '67', '77', '87',
          '16', '26', '36', '46', '56', '66', '76', '86',
          '15', '25', '35', '45', '55', '65', '75', '85',
          '14', '24', '34', '44', '54', '64', '74', '84',
          '13', '23', '33', '43', '53', '63', '73', '83',
          '12', '22', '32', '42', '52', '62', '72', '82',
          '11', '21', '31', '41', '51', '61', '71', '81'
    ],
    '12':['18', '28', '38', '48', '58', '68', '78', '88',
          '17', '27', '37', '47', '57', '67', '77', '87',
          '16', '26', '36', '46', '56', '66', '76', '86',
          '15', '25', '35', '45', '55', '65', '75', '85',
          '14', '24', '34', '44', '54', '64', '74', '84',
          '13', '23', '33', '43', '53', '63', '73', '83',
          '12', '22', '32', '42', '52', '62', '72', '82',
          '11', '21', '31', '41', '51', '61', '71', '81'
    ],
    '48':[
          '14', '24', '34', '44',
          '13', '23', '33', '43',
          '12', '22', '32', '42',
          '11', '21', '31', '41'
    ]
}

plate_well_map = {
    '1': ['A1'],
    '12': [
        'A1', 'A2', 'A3', 'A4',
        'B1', 'B2', 'B3', 'B4',
        'C1', 'C2', 'C3', 'C4'
    ],
    '48': [
        'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8',
        'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8',
        'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8',
        'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8',
        'E1', 'E2', 'E3', 'E4', 'E5', 'E6', 'E7', 'E8',
        'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8'
    ]
}

plot_dims_map = {
    '1': (1, 1),
    '12': (3, 4),
    '48': (6, 8),
    '96': (8, 12)
}

def get_spikes_as_impulses(spike_times, time_resolution=0.001, spike_amplitudes=None, tmin=None, tmax=None):
    """
    Generates an array of unit impulses for the spikes occuring at times 'spike_times'
    """
    if tmax is None:
        tmax = spike_times.max()
    if tmin is None:
        tmin = spike_times.min()
    time_vector = np.arange(tmin, tmax + time_resolution, time_resolution)
    spike_vector = np.zeros_like(time_vector)
    spike_locations = np.searchsorted(time_vector, spike_times) - 1

    if spike_amplitudes is None:
        for i in spike_locations:
            spike_vector[i] += 1
    elif len(spike_amplitudes) == len(spike_locations):
        for i, a in zip(spike_locations, spike_amplitudes):
            spike_vector[i] += a
    else:
        print "spike_times and spike_amplitudes must be of equal length"
        raise Exception('Invalid spike_amplitudes')

    return (spike_vector, time_vector)

def get_spike_rate(spike_times, bin_size=60.0, time_resolution=0.001):
    # If only one spike time is listed then there is not a coherent way to compute spike rate
    if len(spike_times) < 2:
        return (np.asarray([]), np.asarray([]))
    impulse_vector, time_vector = get_spikes_as_impulses(spike_times, time_resolution)
    window_size = np.ceil(bin_size/time_resolution)
    # if the inpulse vector is shorter than the window size, the output of convolution will be misleading
    #  in this case, we just calculate the frequency of spikes over the entire recording as a single timepoint
    if len(impulse_vector) < window_size:
        # Even though these are scalar values, they must be returned as arrays so that they can be concatenated with other spike rate vectors
        return (np.asarray(impulse_vector.sum()/(impulse_vector.size * time_resolution)), np.asarray(time_vector[0]))
    avg_window = np.ones(window_size)/bin_size # Scale to bin size so output is in Hz
    spike_rate = np.convolve(impulse_vector, avg_window, mode='valid')
    time_vector = time_vector[:len(spike_rate)]
    return (spike_rate, time_vector)

def filter_spike_lists_for_electrode(spike_lists, electrode):
    """
    Returns a list of spike_list dataframes that have been queried for the given electrode
    """
    ele_query = lambda spk_lists: get_spike_list_for_electrode(spk_lists, electrode)
    return map(ele_query, spike_lists)

def get_spike_list_for_electrode(spike_list, electrode):
    return spike_list.query('Electrode == @electrode')

def get_spike_histogram(spike_times, bin_size=60.0, tmin=None, tmax=None):
    if tmax is None:
        tmax = spike_times.max()
    if tmin is None:
        tmin = spike_times.min()
    time_bins = np.arange(tmin, tmax + bin_size, bin_size)
    hist, _ = np.histogram(spike_times, bins=time_bins)
    return hist, time_bins[:-1]

def get_electrode_names(plate_type):
    ele_iter = it.product(plate_well_map[plate_type], electrode_map[plate_type])
    return map('_'.join, ele_iter)


