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
    parser.add_argument('-o', '--output_prefix', default=path.join(getcwd(), 'joint_spike_plot'),
        help='Prefix to output path for each plot. Default = ./join_spike_plot'
    )
    parser.add_argument('-k', '--kind', default='scatter', 
        help='kind of joint plot to create, default = scatter.'
        ' See http://seaborn.pydata.org/generated/seaborn.jointplot.html#seaborn.jointplot'
    )

    return parser

def main():
    parser = configure_parser()
    args = parser.parse_args()

    spike_list = pd.concat(map(pd.read_csv, args.spike_lists))
    electrodes = list(set(spike_list['Electrode']))
    electrodes.sort()

    for electrode in electrodes:
        e_list = spike_list.query('Electrode == @electrode')
        if len(e_list) > 1:
            sns.jointplot('Time (s)', 'Amplitude(mV)', e_list, kind=args.kind)
            output_path = args.output_prefix + '_{}.png'.format(electrode)
            plt.savefig(output_path)
            plt.close()

if __name__ == '__main__':
    main()
