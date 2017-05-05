import pandas
import numpy
import json
import seaborn as sns
from pymea import spikelists as sl
from matplotlib import pyplot as plt
from os import path
from argparse import ArgumentParser

def configure_parser():
    parser = ArgumentParser(description='Generates lineplots from one or more spike_list.csv files')
    parser.add_argument('-f', '--file', nargs='+', type=path.expanduser,
        help='Path(s) to the spike_list.csv files to analyze')
    parser.add_argument('-t', '--start_time', nargs='*', type=int, default=[],
        help='List of start times ')
    parser.add_argument('-b', '--bin_size', type=float, default=60.0,
        help='Size of time bins to use for spike counting, default = 60 seconds')
    parser.add_argument('-o', '--output_path', type=path.expanduser, default='spike_rate_timeseries.png')
    parser.add_argument('-p', '--plate_type', default='1',
        help='Number of wells in plate that data was taken from. Default = 1. Options = 1, 12, 48, 96')
    parser.add_argument('-r', '--time_resolution', type=float, default=1.0,
        help='Time resolution of output spike rates. Default = 1 second')
    parser.add_argument('-l', '--use_log_scale', action='store_true',
        help='Display output on a log2 scale')

    return parser

def electrode_line_plot(spike_lists, electrode, bin_size, time_resolution, use_log_scale=False):
    """
    Creates a plot of the time-varying spike rate for a specified electrode
    """
    print "Creating plot for %s" % electrode
    electrode_spike_lists = sl.filter_spike_lists_for_electrode(spike_lists, electrode)
    spike_rate, time = get_spike_rate_vector_from_spike_lists(electrode_spike_lists, bin_size, time_resolution)
    if use_log_scale:
        plt.plot(time, numpy.log2(spike_rate), lw=0.5)
    else:
        plt.plot(time, spike_rate, lw=0.5)

def get_spike_rate_vector_from_spike_lists(spike_lists, bin_size, time_resolution):
    """
    Generates spike_rate vectors for each spike_list in spike_lists, then concatenates them
    """
    spike_times = [spike_list['Time (s)'] for spike_list in spike_lists]
    spike_rate_vectors, time_vectors = zip(*map(lambda st: sl.get_spike_rate(st, bin_size, time_resolution), spike_times))

    try:
        spike_rate = numpy.concatenate(spike_rate_vectors)
    except ValueError:
        print "ValueError on concatenate"
        print spike_rate_vectors, time_vectors
        return spike_rate_vectors[0], time_vectors[0]
    
    time = numpy.concatenate(time_vectors)
    print spike_rate.shape, time.shape
    return spike_rate, time

def main():
    # parse command line args
    parser = configure_parser()
    args = parser.parse_args()

    # Check that the start time input is valid
    if len(args.start_time) != 0 and len(args.start_time) != len(args.file):
        print "-t, --start_time parameter must be specified with the same number of elements as -f, --file"
        return

    # load spike_list csvs
    spike_lists = map(pandas.read_csv, args.file)
    
    # offset spike times
    if len(args.start_time) == len(spike_lists):
        for spike_list, offset in zip(spike_lists, args.start_time):
            spike_list['Time (s)'] += offset

    
    wells = sl.plate_well_map.get(args.plate_type, None)
    if wells is None:
        print 'Unrecognized plate type encountered: {}'.format(args.plate_type)
        return

    subplot_size = sl.plot_dims_map[args.plate_type]
    plt.figure(figsize=(45 ,45))
    for i, well in enumerate(wells):
        plt.subplot(subplot_size[0], subplot_size[1], i + 1)
        for ele in sl.electrode_map[args.plate_type]:
            ele_name = '{well}_{electrode}'.format(well=well, electrode=ele)
            electrode_line_plot(spike_lists, ele_name, args.bin_size, args.time_resolution, args.use_log_scale)
            #plt.title(e)

    plt.savefig(args.output_path)

if __name__ == '__main__':
    main()


    # Savin this for later yum yum
    #get_ele_list = lambda sl: sl.get_spike_list_for_electrode(sl, ele_name)
    #electrode_lists = map(get_ele_list, spike_lists)
    #electrode_times = [l['Time (s)'] for l in electrode_lists]
    #ele_hist = lambda st: sl.get_spike_histogram(st, bin_size=args.bin_size)
    #hists, bins = zip(*map(ele_hist, electrode_times))
    #spike_counts = numpy.concatenate(hists)
    #time = numpy.concatenate(bins)
    #plt.plot(time, spike_counts)
