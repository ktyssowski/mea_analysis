import itertools as it
import pandas as pd
import seaborn as sns
import numpy as np
from os import path
from argparse import ArgumentParser
from pymea import spikelists as sl
from matplotlib import pyplot as plt


def configure_parser():
    parser = ArgumentParser(description='Plot the change in spike frequency between multiple recordings')
    parser.add_argument('spike_lists', nargs='+', type=path.expanduser,
        help='Paths to the spike_list files to compare. Frequencies will be plotted in the same order'
             ' that the filepaths are received'
    )
    parser.add_argument('-p', '--plate_type', default='1',
        help='Number of wells in plate that data was taken from. Default = 1. Options = 1, 12, 48, 96'
    )
    parser.add_argument('-o', '--output_path', type=path.expanduser, default='firing_rate_changes.pdf',
        help='Path at which to save the output plot'
    )
    parser.add_argument('-t', '--recording_times', type=int, nargs='+', default=None,
        help='Start time (in seconds) for each recording'
    )
    
    return parser


def condense_to_average_firing_rate_df(spike_list_df):
    # The recording length is not saved in the spike list file, so we need to estimate it 
    max_time = spike_list_df['Time (s)'].max() 
    spike_rates = spike_list_df.groupby(['Electrode']).size()/max_time
    return spike_rates.rename('firing rate').reset_index()
    

def main():
    # parse command line input
    parser = configure_parser()
    args = parser.parse_args()

    if args.recording_times is not None and len(args.recording_times) == len(args.spike_lists):
        use_recording_times = True
        xaxis = 'recording time'
    elif len(args.recording_times) != len(args.spike_lists):
        print "The number of recording start times specified must equal the number of spike list files"
        print len(args.recording_times)
        print len(args.spike_lists)
        return
    else:
        use_recording_times = False
        xaxis = 'recording no'
    
    # Load spike data
    spike_lists = map(pd.read_csv, args.spike_lists)
    
    # Calculate spike rates
    spike_rates = map(condense_to_average_firing_rate_df, spike_lists)
    
    # Add recording number to the spike rate dataframes
    for i, srdf in enumerate(spike_rates):
        srdf['recording no'] = i + 1
        if use_recording_times:
            srdf['recording time'] = args.recording_times[i]

    # Add in a well column
    master_spike_rate_df = pd.concat(spike_rates)
    well_electrode_pairs = map(lambda s: s.split('_'), master_spike_rate_df['Electrode'])
    wells, _ = zip(*well_electrode_pairs)
    master_spike_rate_df['Well'] = wells
    master_spike_rate_df['log firing rate'] = np.log2(master_spike_rate_df['firing rate'])


    plt.figure(figsize=(28, 21))
    plot_dims = sl.plot_dims_map[args.plate_type]
    for i, well in enumerate(sl.plate_well_map[args.plate_type]):
        well_df = master_spike_rate_df.query('Well == @well')
        plt.subplot(plot_dims[0], plot_dims[1], i + 1)
        plt.title(well)
        ax = sns.pointplot(
            data=well_df,
            x=xaxis,
            y='log firing rate',
            hue='Electrode',
            scale=0.1
        )
        ax.legend_.remove()

    plt.savefig(args.output_path)


if __name__ == '__main__':
    main()
