import pandas as pd
import seaborn as sns
import numpy as np
from os import path, getcwd
from argparse import ArgumentParser
from matplotlib import pyplot as plt

def configure_parser():
    parser = ArgumentParser(
        description='Generates joint plots of time vs amplitude for MEA data'
    )
    parser.add_argument('spike_lists', nargs='+', type=path.expanduser,
        help='Paths to csv formatted spike_list files.'
    )
    parser.add_argument('-o', '--output_prefix', default=path.join(getcwd(), 'spike_freq_plot'),
        help='Prefix to output path for each plot. Default = ./join_freq_plot'
    )
    parser.add_argument('-b', '--bin_width', default=30, type=int, 
        help='bin width for output, in seconds'
    )
    parser.add_argument('-t', '--end_time', type=int, default=-1,
        help='Final time point to record spiking from')

    return parser

def main():
    parser = configure_parser()
    args = parser.parse_args()

    spike_list = pd.concat(map(pd.read_csv, args.spike_lists))
    spike_list = spike_list[spike_list['Time (s)'] == spike_list['Time (s)']]
    # Filter out neurons after recording
    #if args.end_time > -1:
        #spike_list = spike_list[spike_list['Time (s)'] < args.end_time]
    electrodes = list(set(spike_list['Electrode']))
    electrodes.sort()

    for electrode in electrodes:
        e_list = spike_list.query('Electrode == @electrode')
        if len(e_list) >= 1:
            try:
                bin_max = e_list['Time (s)'].max() + args.bin_width
                bins = np.arange(0, bin_max, args.bin_width)
                plt.hist(e_list['Time (s)'], bins=bins)
                output_path = args.output_prefix + '_{}.png'.format(electrode)
                plt.savefig(output_path)
                plt.close()
            except:
                print "failed to plot electrode %s :(" % electrode

    bin_max = spike_list['Time (s)'].max() + args.bin_width
    bins = np.arange(0, bin_max, args.bin_width)
    plt.hist(spike_list['Time (s)'], bins=bins)
    output_path = args.output_prefix + '_array_average.png'
    plt.savefig(output_path)
    plt.close()

if __name__ == '__main__':
    main()
