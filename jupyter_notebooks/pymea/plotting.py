import pandas as pd
import itertools as it
import seaborn as sns
import numpy as np
from pymea import matlab_compatibility as mc
from matplotlib import pyplot as plt
import random
from datetime import datetime

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

def plot_unit_traces_plus_means(category_dataframe, **plot_kwargs):
    """
    Plots spike frequency unit traces for each neural unit in the provided category dataframe, along with 
    the mean trace (in black)
    """
    for unit in category_dataframe['unit_name'].unique():
        unit_table = category_dataframe.query('unit_name == @unit')
        plt.plot(unit_table['time'], unit_table['spike_freq'], **plot_kwargs)
    
    mean_freq_traces = category_dataframe.groupby(('condition', 'time'))['spike_freq'].mean()
    mean_freq_traces = mean_freq_traces.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    for condition in mean_freq_traces['condition'].unique():
        condition_trace = mean_freq_traces.query('condition == @condition')
        plt.plot(condition_trace['time'], condition_trace['spike frequency'], 'k')

    #plt.yscale('log')
    plt.xlabel('time')
    plt.ylabel('spike frequency')
    plt.title('Spike Frequency Traces')
    plt.legend(mean_freq_traces['condition'].unique()) 

def plot_unit_traces_plus_medians(category_dataframe, yscale = 'linear', **plot_kwargs):
    """
    Plots spike frequency unit traces for each neural unit in the provided category dataframe, along with 
    the mean trace (in black)
    """
    for unit in category_dataframe['unit_name'].unique():
        unit_table = category_dataframe.query('unit_name == @unit')
        plt.plot(unit_table['time'], unit_table['spike_freq'], **plot_kwargs)
    
    mean_freq_traces = category_dataframe.groupby(('condition', 'time'))['spike_freq'].median()
    mean_freq_traces = mean_freq_traces.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    for condition in mean_freq_traces['condition'].unique():
        condition_trace = mean_freq_traces.query('condition == @condition')
        plt.plot(condition_trace['time'], condition_trace['spike frequency'], 'k')

    plt.yscale(yscale)
    plt.xlabel('time')
    plt.ylabel('spike frequency')
    plt.title('Spike Frequency Traces')
    plt.legend(mean_freq_traces['condition'].unique()) 
    
def plot_unit_points_plus_means(category_dataframe, title, divide_fn, **plot_kwargs):
    """
    Plots spike frequency points for each neural unit in the provided category dataframe, in each section returned by 
    divide_fn. Mean of all units of the same category for each section is also shown.
    """
    color_map = plt.cm.get_cmap('viridis', category_dataframe['condition'].unique().size)
    color_index = 0
    for cond in category_dataframe['condition'].unique():
        cond_table = category_dataframe.query('condition == @cond')
        cond_table = cond_table.reset_index()
        # Get spks/pulse for each neuron in each time period
        unit_table = cond_table.groupby(('unit_name', lambda x: divide_fn(cond_table, x, 'time')))['spike_freq'].mean() 
        unit_table = unit_table.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
         # Get average spks/pulse for all neurons in each time period
        mean_table = unit_table.groupby('level_1')['spike frequency'].mean()
        mean_table = mean_table.reset_index() # Convert the multiindexed series back to a dataframe
        
        plt.plot(unit_table['level_1'].astype('int')*3, unit_table['spike frequency'], 'o', color = color_map(color_index), markerfacecolor = 'none', alpha = 0.25, label = '_nolegend_')
        plt.plot(mean_table['level_1'].astype('int')*3, mean_table['spike frequency'], 'o', color = color_map(color_index))
        color_index += 1 # Move to next color for next condition
        
    plt.axhline(y=1, xmin=0, xmax=1, hold=None, color='black')
    plt.legend(category_dataframe['condition'].unique())
    plt.xlabel('hours since start of 1st recording')
    plt.ylabel('spikes/pulse')
    plt.title(title)


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
    
def plot_median_frequency_traces(category_dataframe, yscale = 'linear', **kwargs):
    """
    Plots the mean frequency trace for each condition in category_dataframe
    """
    mean_freq_traces = category_dataframe.groupby(('condition', 'time'))['spike_freq'].median()
    mean_freq_traces = mean_freq_traces.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    for condition in mean_freq_traces['condition'].unique():
        condition_trace = mean_freq_traces.query('condition == @condition')
        plt.plot(condition_trace['time'], condition_trace['spike frequency'])

    plt.yscale(yscale)
    plt.xlabel('time')
    plt.ylabel('spike frequency')
    plt.title('Median Spike Frequency Traces')
    plt.legend(mean_freq_traces['condition'].unique())
    
def plot_median_unit_frequency_traces(category_dataframe, rec_starts, rec_ends, num_rec, yscale = 'linear', **kwargs):
    """
    Plots the frequency trace of the unit with the median avg spike freq for each condition in category_dataframe
    """
    overall_mean_freq = category_dataframe.groupby(('unit_name', 'condition'))['spike_freq'].mean()
    overall_mean_freq = overall_mean_freq.rename('spike_freq').reset_index() # Convert the multiindexed series back to a dataframe
    for condition in overall_mean_freq['condition'].unique():
        condition_trace = overall_mean_freq.query('condition == @condition')
        n = len(condition_trace['spike_freq'])
        if n%2 == 0:
            sorted_freq = sorted(condition_trace['spike_freq'])
            median_freq = sorted_freq[n//2 - 1]
        else:
            median_freq = np.median(condition_trace['spike_freq'])
        median_unit = condition_trace[condition_trace.spike_freq == median_freq]['unit_name']
        median_unit.reset_index(drop=True, inplace = True)
        median_unit = median_unit.iloc[0]
        median_trace = category_dataframe.query('unit_name == @median_unit')
        plot_unit_means_per_rec(median_trace, rec_starts, rec_ends, num_rec)
        
    plt.yscale(yscale)
    plt.xlabel('time')
    plt.ylabel('spike frequency')
    plt.title('Median Unit Spike Frequency Traces')
    plt.legend(overall_mean_freq['condition'].unique())

def plot_unit_means_per_rec(category_dataframe, rec_starts, rec_ends, num_rec, yscale = 'linear', **plot_kwargs):
        mean_unit_freq = pd.DataFrame()
        for index in range(0,num_rec):
            start1 = rec_starts[index]
            end1 = rec_ends[index]
            rec_table = category_dataframe.query('time >= @start1 and time <= @end1')
            rec_mean_unit_freq = rec_table.groupby('unit_name')['spike_freq'].mean()
            num_units = rec_mean_unit_freq.count()
            start_dt = datetime.strptime(start1, "%Y-%m-%d %H:%M:%S").date()
            start_times = pd.Series([start1]*num_units, index = rec_mean_unit_freq.index)
            rec_data = pd.DataFrame({"mean_freq": rec_mean_unit_freq, "start_time": start_times})
            del rec_data.index.name
            rec_data.reset_index()
            rec_data['unit_name'] = rec_mean_unit_freq.index
            mean_unit_freq = pd.concat([mean_unit_freq, rec_data])
        
        for unit in mean_unit_freq['unit_name'].unique():
            date_table = mean_unit_freq.query('unit_name == @unit')
            plt.plot_date(date_table['start_time'], date_table['mean_freq'], '-o')
        
        plt.yscale(yscale)
        plt.xlabel('time')
        plt.ylabel('mean spike frequency')
        plt.title('Mean Spike Frequency Per Recording')
        
def plot_medians_per_rec(category_dataframe, rec_starts, rec_ends, num_rec, yscale='linear', **plot_kwargs):
        median_unit_freq = pd.DataFrame()
        for index in range(0,num_rec):
            start1 = rec_starts[index]
            end1 = rec_ends[index]
            rec_table = category_dataframe.query('time >= @start1 and time <= @end1')
            rec_median_unit_freq = rec_table.groupby('condition')['spike_freq'].median()
            num_units = rec_median_unit_freq.count()
            start_dt = datetime.strptime(start1, "%Y-%m-%d %H:%M:%S").date()
            start_times = pd.Series([start1]*num_units, index = rec_median_unit_freq.index)
            rec_data = pd.DataFrame({"median_freq": rec_median_unit_freq, "start_time": start_times})
            del rec_data.index.name
            rec_data.reset_index()
            rec_data['condition'] = rec_median_unit_freq.index
            median_unit_freq = pd.concat([median_unit_freq, rec_data])
        
        for cond in median_unit_freq['condition'].unique():
            date_table = median_unit_freq.query('condition == @cond')
            plt.plot_date(date_table['start_time'], date_table['median_freq'], '-o')
        
        plt.yscale(yscale)
        plt.xlabel('time')
        plt.ylabel('median spike frequency')
        plt.title('Median Spike Frequency Per Recording')
        plt.legend(median_unit_freq['condition'].unique())
    
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

def construct_categorized_dataframe_pulse(data_table, filter_dict, get_power, get_width):
    """
    Takes the data from the matlab csv generated by preprocessing and applies filters to column names
    allowing for the categorization of data

    data_table - pandas DataFrame - should be populated from the .csv file generated by the 
        "generate_frequency_table.m" matlab script
    filter_dict - dictionary of the form {'condition_name': condition_filter}, where 
        condition_name is a string used to identify an experimental condition, and condition filter
        is a function that returns True for the unit_names corresponding to the desired condition
    get_power - function that returns the power of optical stimulation by mapping the unit name to the 
        well map
    get_width - function that returns the width of each pulse of optical stimulation by mapping the unit 
        name to the well map
    """
    time_vector = data_table['time'].map(mc.datetime_str_to_datetime)
    unit_table = data_table.drop('time', axis=1)
    condition_dicts = (
        {
            'time': time_vector,
            'condition': condition_name,
            'pulse_power': get_power(condition_column.name),
            'pulse_width': get_width(condition_column.name),
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


    plt.ylabel('Fold Induction of Spike Frequency (Hz)')
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

def foldInductionPlusMean_ctrl(cat_table, baseline_table, stim_table, condition, title, var=2.5, minHz = 0.01):
    '''
    This function plots baseline-normalized plots for a given condition that include both all of the channels passing a filters and all the mean of those channels--use for unstim samples
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
        if varOfBaseline < var and meanOfBaseline > minHz: 
            plt.plot(unit['time'], unit['spike_freq']/meanOfBaseline, color=(random.random(), random.random(), random.random(), .4))
            c_filter = c_filter.append(unit, ignore_index=True)
            b_filter = b_filter.append(unit_b, ignore_index=True)
        else:
            continue


    plt.ylabel('Fold Induction of Spike Frequency (Hz)')
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
        foldInductionPlusMean_ctrl(cat_table, baseline_table, stim_table, condition, title, var=2.5, minHz=0.01)


def count_active_neurons(cat_table, threshold, return_value):
    """Count and plot the number of neurons firing above a threshold at each time point"""
    above_threshold = cat_table.query('spike_freq > @threshold')
    time_grouped_counts = above_threshold.groupby(('time'))['unit_name'].count()
    time_grouped_counts = time_grouped_counts.rename('count').reset_index() # Convert the multiindexed series back to a dataframe
    
    plt.plot(time_grouped_counts['time'], time_grouped_counts['count'])
    plt.xlabel('time')
    plt.ylabel('Number of active units')
    plt.title('Active units')
    if return_value:
        return time_grouped_counts
    
def compare_active_per_recording(cat_table, threshold, rec_starts, rec_ends):
    """For each recording session, find the number of new neurons and the 
    number of neurons that have stopped firing"""
    above_threshold = cat_table.query('spike_freq > @threshold')
    num_rec = len(rec_starts)
    only_1 = [0]*(num_rec-1);
    only_2 = [0]*(num_rec-1);
    for index in range(0,num_rec-1):
        start1 = rec_starts[index]
        end1 = rec_ends[index]
        start2 = rec_starts[index+1]
        end2 = rec_ends[index+1]
        group_1 = above_threshold.query('time >= @start1 and time <= @end1')
        group_2 = above_threshold.query('time >= @start2 and time <= @end2')
        units_1 = group_1['unit_name'].unique()
        units_2 = group_2['unit_name'].unique()
        both = list(set(units_1) | set(units_2))
        only_1[index] = len(both) - len(units_2) #Count the number of units in group1 but not group2
        only_2[index] = len(both) - len(units_1) 
   
    rec_starts_series = pd.Series(rec_starts)
    recs = rec_starts_series.map(mc.remapped_str_to_datetime)
    plt.plot_date(recs[1:15], only_2, '-', label = "new")
    plt.plot_date(recs[1:15], only_1, '-', label = "died")
    plt.legend()
    plt.xlabel('Recording session')
    plt.ylabel('Number of units')
    plt.title('Neuron turnover')
    
def compare_active_per_sec(cat_table, threshold):
    """For each recording session, find the number of new neurons and the 
    number of neurons that have stopped firing"""
    above_threshold = cat_table.query('spike_freq > @threshold').reset_index()
    secs = above_threshold['time']
    num_sec = len(secs)
    only_1 = [0]*(num_sec-1);
    only_2 = [0]*(num_sec-1);
    for index in range(0,num_sec-1):
        start1 = secs.iloc[index]
        start2 = secs.iloc[index+1]
        group_1 = above_threshold.query('time == @start1')
        group_2 = above_threshold.query('time == @start2')
        units_1 = group_1['unit_name'].unique()
        units_2 = group_2['unit_name'].unique()
        both = list(set(units_1) | set(units_2))
        only_1[index] = len(both) - len(units_2) #Count the number of units in group1 but not group2
        only_2[index] = len(both) - len(units_1) 
   
    plt.plot_date(secs.iloc[0:num_sec-1], only_2, '-', label = "new")
    plt.plot_date(secs.iloc[0:num_sec-1], only_1, '-', label = "died")
    plt.legend()
    plt.xlabel('Recording session')
    plt.ylabel('Number of units')
    plt.title('Neuron turnover')