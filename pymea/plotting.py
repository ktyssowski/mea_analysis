import pandas as pd
import itertools as it
import seaborn as sns
import numpy as np
from pymea import matlab_compatibility as mc
from matplotlib import pyplot as plt
import random


def plot_units_from_spike_table(spike_table):
    time_vector = spike_table['time'].map(mc.datetime_str_to_datetime)
    unit_table = spike_table.copy()
    del unit_table['time']
    num_units = len(unit_table.columns)
    #plt.figure(figsize=(10, 0.1 * num_units))
    for i, unit_name in enumerate(unit_table.columns):
        #plt.subplot(num_units, 1, i + 1)
        plt.figure()
        plot_unit(time_vector, unit_table[unit_name])
        plt.xlabel(unit_name)

def smooth(A, kernel_size=5, mode='same'):
    """
    Computes the moving average of A using a kernel_size kernel.
    """
    kernel = np.ones(kernel_size)/kernel_size
    return np.convolve(A, kernel, mode=mode)

def plot_unit(time, unit):
    plt.plot(time, unit)

def plot_unit_traces(category_dataframe, **plot_kwargs):
    """
    Plots spike frequency unit traces for each neural unit in the provided category dataframe
    """
    for unit in category_dataframe['unit_name'].unique():
        unit_table = category_dataframe.query('unit_name == @unit')
        plt.plot(unit_table['time'], unit_table['spike_freq'], **plot_kwargs)

def average_timecourse_plot(category_dataframe, **kwargs):
    """
    Generates an average timecourse with error bars for each category in category_dataframe
    see construct_categorized_dataframe for details on generateing the category_dataframe
    """
    sns.pointplot(x='time', y='spike_freq', hue='condition', data=category_dataframe, **kwargs)

def avg_timecourse_plot_2(category_dataframe, **kwargs):
    mean_freqs = category_dataframe.groupby(('condition', 'time'))['spike_freq'].mean()
    std_freqs = category_dataframe.groupby(('condition', 'time'))['spike_freq'].std()
    plt.errorbar()

def plot_unit_frequency_distributions(category_dataframe, **kwargs):
    """
    Plots the distribution of mean frequencies for units in each condition
    """
    mean_freqs_by_condition = category_dataframe.groupby(('condition', 'unit_name'))['spike_freq'].mean()
    mean_freqs_by_condition = mean_freqs_by_condition.rename('mean_freq').reset_index()
    for condition in mean_freqs_by_condition['condition']:
        sns.distplot(mean_freqs_by_condition.query('condition == @condition')['mean_freq'].map(np.log), bins=100)

def plot_mean_frequency_traces(category_dataframe, **kwargs):
    """
    Plots the mean frequency trace for each condition in category_dataframe
    """
    mean_freq_traces = category_dataframe.groupby(('condition', 'time'))['spike_freq'].mean()
    mean_freq_traces = mean_freq_traces.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    for condition in mean_freq_traces['condition'].unique():
        condition_trace = mean_freq_traces.query('condition == @condition')
        plt.plot(condition_trace['time'], condition_trace['spike frequency'])

    plt.xlabel('time')
    plt.ylabel('spike frequency')
    plt.title('Mean Spike Frequency Traces')
    plt.legend(mean_freq_traces['condition'].unique())

def construct_categorized_dataframe(data_table, filter_dict):
    """
    Takes the data from the matlab csv generated by preprocessing and applies filters to column names
    allowing for the categorization of data

    data_table - pandas DataFrame - should be populated from the .csv file generated by the 
        "generate_frequency_table.m" matlab script
    filter_dict - dictionary of the form {'condition_name': condition_filter}, where 
        condition_name is a string used to identify an experimental condition, and condition filter
        is a function that returns True for the unit_names corresponding to the desired condition
    """
    time_vector = data_table['time'].map(mc.datetime_str_to_datetime)
    unit_table = data_table.drop('time', axis=1)
    condition_dicts = (
        {
            'time': time_vector,
            'condition': condition_name,
            'spike_freq': condition_column,
            'unit_name': condition_column.name
        } for condition_name, condition_filter in filter_dict.iteritems()
            for condition_column in filter_unit_columns(condition_filter, unit_table)
    )
    condition_tables = it.imap(pd.DataFrame, condition_dicts)
    return pd.concat(condition_tables)

def filter_unit_columns(predicate, unit_table):
    """
    Generates columns from unit_table whose names satisfy the condition specified in predicate

    predicate - function that returns true for desired unit names
    unit_table - data_mat containing firing rates over time from each unit, with the time column ommited
    """
    unit_column_names = filter(predicate, unit_table.columns)
    for column_name in unit_column_names:
        yield unit_table[column_name]

def smooth_categorized_dataframe_unit_traces(category_dataframe, kernel_size=5):
    cat_df_copy = category_dataframe.copy()
    for unit_name in cat_df_copy['unit_name'].unique():
        unit_table = cat_df_copy.query('unit_name == @unit_name')
        smooth_trace = smooth(unit_table['spike_freq'], kernel_size=kernel_size, mode='same')
        cat_df_copy.loc[cat_df_copy['unit_name'] == unit_name, 'spike_freq'] = smooth_trace

    return cat_df_copy


def makeTables(b_start, b_stop, s_start, e_start, cat_table):
    '''
    Makes tables of the baseline portion, stimulated portion and the end portion (i.e. the part of the time course that you deem to have adapted) from the table of the whole time course
    '''

    baseline_table = cat_table.query('time < "%s"'%b_stop).query('time > "%s"'%b_start)
    stim_table = cat_table.query('time > "%s"'%s_start)
    end_table = cat_table.query('time > "%s"'%e_start)
    return(baseline_table, stim_table, end_table)



def foldInductionPlusMean_stim(cat_table, baseline_table, stim_table, condition, title, var=2.5, minHz = 0.01):
    '''
    This function plots baseline-normalized plots for a given condition that include both all of the channels passing a filters and all the mean of those channels--use for stimulated samples b/c 
    filters out things that don't change with stim
    '''
    c = cat_table.query('condition == "%s"'%condition)
    b = baseline_table.query('condition == "%s"'%condition)
    s = stim_table.query('condition == "%s"'%condition)
    c_filter = pd.DataFrame()
    b_filter = pd.DataFrame()


    for unit_name in c['unit_name'].unique():
        unit = c.query('unit_name == @unit_name')
        unit_b = b.query('unit_name == @unit_name')
        unit_s = s.query('unit_name == @unit_name')
        meanOfBaseline = np.mean(unit_b['spike_freq'])
        varOfBaseline = (max(unit_b['spike_freq'])-min(unit_b['spike_freq']))/meanOfBaseline
        meanAfterDrug = np.mean(unit_s[0:60]['spike_freq'])
        if meanOfBaseline < meanAfterDrug and varOfBaseline < var and meanOfBaseline > minHz: 
            plt.plot(unit['time'], unit['spike_freq']/meanOfBaseline, color=(random.random(), random.random(), random.random(), .4))
            c_filter = c_filter.append(unit, ignore_index=True)
            b_filter = b_filter.append(unit_b, ignore_index=True)
        else:
            continue


    plt.ylabel('Fold Inudction of Spike Frequency (Hz)')
    plt.ylim(0,10)
    plt.axhline(y=1, xmin=0, xmax=1, hold=None, color='black')
    mean_freq_traces = c_filter.groupby(('condition', 'time'))['spike_freq'].mean()
    mean_freq_traces = mean_freq_traces.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    mean_freq_traces_b = b_filter.groupby(('condition', 'time'))['spike_freq'].mean()
    mean_freq_traces_b = mean_freq_traces_b.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe

    plt.title(title)
    meanOfMean = np.mean(mean_freq_traces_b['spike frequency'])
    plt.plot(mean_freq_traces['time'], mean_freq_traces['spike frequency']/meanOfMean, color=(0,0,0))

    plt.show()

def foldInductionPlusMean_ctrl(cat_table, baseline_table, condition, title, var=2.5, minHz = 0.01):
    '''
    This function plots baseline-normalized plots for a given condition that include both all of the channels passing a filters and all the mean of those channels--use for unstim samples
    '''
    c = cat_table.query('condition == "%s"'%condition)
    b = baseline_table.query('condition == "%s"'%condition)
    c_filter = pd.DataFrame()
    b_filter = pd.DataFrame()


    for unit_name in c['unit_name'].unique():
        unit = c.query('unit_name == @unit_name')
        unit_b = b.query('unit_name == @unit_name')
        unit_s = s.query('unit_name == @unit_name')
        meanOfBaseline = np.mean(unit_b['spike_freq'])
        varOfBaseline = (max(unit_b['spike_freq'])-min(unit_b['spike_freq']))/meanOfBaseline
        if varOfBaseline < var and meanOfBaseline > minHz: 
            plt.plot(unit['time'], unit['spike_freq']/meanOfBaseline, color=(random.random(), random.random(), random.random(), .4))
            c_filter = c_filter.append(unit, ignore_index=True)
            b_filter = b_filter.append(unit_b, ignore_index=True)
        else:
            continue


    plt.ylabel('Fold Inudction of Spike Frequency (Hz)')
    plt.ylim(0,10)
    plt.axhline(y=1, xmin=0, xmax=1, hold=None, color='black')
    mean_freq_traces = c_filter.groupby(('condition', 'time'))['spike_freq'].mean()
    mean_freq_traces = mean_freq_traces.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    mean_freq_traces_b = b_filter.groupby(('condition', 'time'))['spike_freq'].mean()
    mean_freq_traces_b = mean_freq_traces_b.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe

    plt.title(title)
    meanOfMean = np.mean(mean_freq_traces_b['spike frequency'])
    plt.plot(mean_freq_traces['time'], mean_freq_traces['spike frequency']/meanOfMean, color=(0,0,0))

    plt.show()

def foldInductionPlusMean(cat_table, baseline_table, stim_table, condition, title, var=2.5, minHz = 0.01, ind_filter = True):
    '''
    Combine stim and ctrl fxns
    '''
    
    if ind_filter:
        foldInductionPlusMean_stim(cat_table, baseline_table, stim_table, condition, title, var=2.5, minHz=0.01)
    else:
        foldInductionPlusMean_ctrl(cat_table, baseline_table, condition, title, var=2.5, minHz=0.01)


