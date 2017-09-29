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

def plot_unit_traces_plus_means(category_dataframe, yscale = 'linear', **plot_kwargs):
    """
    Plots spike frequency unit traces for each neural unit in the provided category dataframe, along with 
    the mean trace (in black)
    """
    time_days = (category_dataframe['time']-category_dataframe['time'].iloc[0]).map(lambda x: x.days)
    time_seconds = (category_dataframe['time']-category_dataframe['time'].iloc[0]).map(lambda x: x.seconds)
    time_vector = (time_days + (time_seconds/3600/24)).unique()
    
    for unit in category_dataframe['unit_name'].unique():
        unit_table = category_dataframe.query('unit_name == @unit')
        plt.plot(time_vector, unit_table['spike_freq'], **plot_kwargs)
    
    mean_freq_traces = category_dataframe.groupby(('condition', 'time'))['spike_freq'].mean()
    mean_freq_traces = mean_freq_traces.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    for condition in mean_freq_traces['condition'].unique():
        condition_trace = mean_freq_traces.query('condition == @condition')
        plt.plot(time_vector, condition_trace['spike frequency'], 'k')

    plt.yscale(yscale)
    plt.xlabel('time')
    plt.ylabel('spike frequency')
    plt.title('Spike Frequency Traces')
    plt.legend(mean_freq_traces['condition'].unique()) 

def plot_unit_traces_plus_medians(category_dataframe, yscale = 'linear', **plot_kwargs):
    """
    Plots spike frequency unit traces for each neural unit in the provided category dataframe, along with 
    the mean trace (in black)
    """
    time_days = (category_dataframe['time']-category_dataframe['time'].iloc[0]).map(lambda x: x.days)
    time_seconds = (category_dataframe['time']-category_dataframe['time'].iloc[0]).map(lambda x: x.seconds)
    time_vector = (time_days + (time_seconds/3600/24)).unique()
    
    for unit in category_dataframe['unit_name'].unique():
        unit_table = category_dataframe.query('unit_name == @unit')
        plt.plot(time_vector, unit_table['spike_freq'], **plot_kwargs)
    
    mean_freq_traces = category_dataframe.groupby(('condition', 'time'))['spike_freq'].median()
    mean_freq_traces = mean_freq_traces.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    for condition in mean_freq_traces['condition'].unique():
        condition_trace = mean_freq_traces.query('condition == @condition')
        plt.plot(time_vector, condition_trace['spike frequency'], 'k')

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
    
def plot_median_frequency_traces(category_dataframe, yscale = 'linear', quartiles = True, **kwargs):
    """
    Plots the median frequency trace for each condition in category_dataframe
    """
    median_freq_traces = category_dataframe.groupby(('condition', 'time'))['spike_freq'].median()
    Q1 = category_dataframe.groupby(('condition', 'time'))['spike_freq'].quantile(.25)
    Q3 = category_dataframe.groupby(('condition', 'time'))['spike_freq'].quantile(.75)
    median_freq_traces = median_freq_traces.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    Q1 = Q1.rename('spike frequency').reset_index()
    Q3 = Q3.rename('spike frequency').reset_index()
    
    for condition in median_freq_traces['condition'].unique():
        condition_trace = median_freq_traces.query('condition == @condition')
        ct = plt.plot(condition_trace['time'], condition_trace['spike frequency'])
        if quartiles == True:
            Q1_trace = Q1.query('condition == @condition')
            Q3_trace = Q3.query('condition == @condition')
            plt.plot(Q1_trace['time'], Q1_trace['spike frequency'], '--', color = ct[0].get_color())
            plt.plot(Q3_trace['time'], Q3_trace['spike frequency'], '--', color = ct[0].get_color())

    plt.yscale(yscale)
    plt.xlabel('time')
    plt.ylabel('spike frequency')
    plt.title('Median Spike Frequency Traces')
    plt.legend(median_freq_traces['condition'].unique())
    
def get_median_unit_traces(category_dataframe):
    """
    Finds the unit traces in category_dataframe with the median average firing rate
    """
    overall_mean_freq = category_dataframe.groupby(('unit_name', 'condition'))['spike_freq'].mean()
    overall_mean_freq = overall_mean_freq.rename('spike_freq').reset_index() # Convert the multiindexed series back to a dataframe
    median_traces = pd.DataFrame()
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
        median_traces = pd.concat([median_traces, category_dataframe.query('unit_name == @median_unit')])
    return median_traces
    
def plot_median_unit_frequency_traces(category_dataframe, rec_starts, rec_ends, yscale = 'linear', **kwargs):
    """
    Plots the frequency trace of the unit with the median avg spike freq for each condition in category_dataframe
    """
    median_traces = get_median_unit_traces(category_dataframe)
    for condition in median_traces:
        plot_unit_means_per_rec(median_traces.query('condition == @cond'), rec_starts, rec_ends, num_rec, yscale)
        
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
        
def plot_means_per_rec(category_dataframe, rec_starts, rec_ends, num_rec, yscale = 'linear', **plot_kwargs):
        mean_unit_freq = pd.DataFrame()
        for index in range(0,num_rec):
            start1 = rec_starts[index]
            end1 = rec_ends[index]
            rec_table = category_dataframe.query('time >= @start1 and time <= @end1')
            rec_mean_unit_freq = rec_table.groupby('condition')['spike_freq'].mean()
            num_units = rec_mean_unit_freq.count()
            start_dt = datetime.strptime(start1, "%Y-%m-%d %H:%M:%S").date()
            start_times = pd.Series([start1]*num_units, index = rec_mean_unit_freq.index)
            rec_data = pd.DataFrame({"mean_freq": rec_mean_unit_freq, "start_time": start_times})
            del rec_data.index.name
            rec_data.reset_index()
            rec_data['condition'] = rec_mean_unit_freq.index
            mean_unit_freq = pd.concat([mean_unit_freq, rec_data])
        
        for cond in mean_unit_freq['condition'].unique():
            date_table = mean_unit_freq.query('condition == @cond')
            plt.plot_date(date_table['start_time'], date_table['mean_freq'], '-o')
        
        plt.yscale(yscale)
        plt.xlabel('time')
        plt.ylabel('mean spike frequency')
        plt.title('Mean Spike Frequency Per Recording')
        plt.legend(mean_unit_freq['condition'].unique())
        
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

def construct_categorized_dataframe_pulse(data_table, filter_dict, get_power, get_width, definer):
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

def construct_categorized_dataframe_pulse_time(data_table, filter_dict, get_power, get_width):
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
    datetime_table = data_table
    time_vector = data_table['time'].map(mc.datetime_str_to_datetime)
    datetime_table['time'] = time_vector
    unit_table = data_table.drop('time', axis=1)
    condition_dicts = (
        {
            'time': condition_row['time'],
            'condition': condition_name,
            'pulse_power': get_power(condition_row['time']),
            'pulse_width': get_width(condition_row['time']),
            'spike_freq': condition_row[unit],
            'unit_name': unit
        } for condition_name, condition_filter in filter_dict.iteritems()
            for condition_row in filter_unit_rows(condition_filter, datetime_table)
                for unit in condition_row.columns
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
        
def filter_unit_rows(predicate, data_table):
    """
    Generates rows from unit_table whose times satisfy the condition specified in predicate

    predicate - function that returns true for desired unit names
    data_table - data_mat containing firing rates over time from each unit, with the time column included
    """    
    data_row_times = filter(predicate, data_table['time'])
    for row_time in data_row_times:
        yield data_table[data_table['time'] == row_time]

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



def foldInductionPlusMean_stim(cat_table, baseline_table, stim_table, condition, title, var=2.5, minHz = 0.01, maxHz = 100000, ymax = 10, plotFolds=True):
    '''
    This function plots baseline-normalized plots for a given condition that include both all of the channels passing a filters and all the mean of those channels--use for stimulated samples b/c 
    filters out things that don't change with stim
    '''
    c = cat_table.query('condition == "%s"'%condition)
    b = baseline_table.query('condition == "%s"'%condition)
    s = stim_table.query('condition == "%s"'%condition)
    c_filter = pd.DataFrame()
    b_filter = pd.DataFrame()
    time_days = (cat_table['time']-cat_table['time'].iloc[0]).map(lambda x: x.days)
    time_seconds = (cat_table['time']-cat_table['time'].iloc[0]).map(lambda x: x.seconds)
    time_vector = (time_days + (time_seconds/3600/24)).unique()

    for unit_name in c['unit_name'].unique():
        unit = c.query('unit_name == @unit_name')
        unit_b = b.query('unit_name == @unit_name')
        unit_s = s.query('unit_name == @unit_name')
        meanOfBaseline = np.mean(unit_b['spike_freq'])
        varOfBaseline = (unit_b['spike_freq'].std())/meanOfBaseline
        meanAfterDrug = np.mean(unit_s[0:60]['spike_freq'])
        folds = unit['spike_freq']/meanOfBaseline
        if meanOfBaseline < meanAfterDrug and varOfBaseline < var and meanOfBaseline > minHz and meanOfBaseline < maxHz and not ((folds < 0.001).any()): 
            if plotFolds == True:
                plt.plot(time_vector, folds, color=(random.random(), random.random(), random.random(), .4))
            else:
                plt.plot(time_vector, unit['spike_freq'], color=(random.random(), random.random(), random.random(), .4))
            c_filter = c_filter.append(unit, ignore_index=True)
            b_filter = b_filter.append(unit_b, ignore_index=True)
        else:
            continue


    plt.xlabel('Time (days)')
    plt.ylim(0.00005,ymax)

    mean_freq_traces = c_filter.groupby(('condition', 'time'))['spike_freq'].mean()
    mean_freq_traces = mean_freq_traces.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    mean_freq_traces_b = b_filter.groupby(('condition', 'time'))['spike_freq'].mean()
    mean_freq_traces_b = mean_freq_traces_b.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    
    median_freq_traces = c_filter.groupby(('condition', 'time'))['spike_freq'].median()
    median_freq_traces = median_freq_traces.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    median_freq_traces_b = b_filter.groupby(('condition', 'time'))['spike_freq'].median()
    median_freq_traces_b = median_freq_traces_b.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    
    plt.title(title)
    meanOfMean = np.mean(mean_freq_traces_b['spike frequency'])
    meanOfMedian = np.mean(median_freq_traces_b['spike frequency'])
    if plotFolds == True:
        plt.axhline(y=1, xmin=0, xmax=1, hold=None, color='black')
        plt.plot(time_vector, mean_freq_traces['spike frequency']/meanOfMean, color=(0,0,0))
        plt.plot(time_vector, median_freq_traces['spike frequency']/meanOfMedian, 'r')
        plt.ylabel('Fold Induction of Spike Frequency (Hz)')
    else:
        plt.axhline(y=meanOfMean, xmin=0, xmax=1, hold=None, color='black')
        plt.plot(time_vector, mean_freq_traces['spike frequency'], color=(0,0,0))
        plt.plot(time_vector, median_freq_traces['spike frequency'], 'r')      
        plt.ylabel('Spike Frequency (Hz)')
    plt.yscale('log')

    print(len(c_filter['unit_name'].unique()))
    print(len(c['unit_name'].unique()))
    
    plt.show()

def foldInductionPlusMean_ctrl(cat_table, baseline_table, stim_table, condition, title, var=2.5, minHz = 0.01, maxHz = 100000, ymax = 10, plotFolds=True):
    '''
    This function plots baseline-normalized plots for a given condition that include both all of the channels passing a filters and all the mean of those channels--use for unstim samples
    '''
    c = cat_table.query('condition == "%s"'%condition)
    b = baseline_table.query('condition == "%s"'%condition)
    s = stim_table.query('condition == "%s"'%condition)
    c_filter = pd.DataFrame()
    b_filter = pd.DataFrame()
    time_days = (cat_table['time']-cat_table['time'].iloc[0]).map(lambda x: x.days)
    time_seconds = (cat_table['time']-cat_table['time'].iloc[0]).map(lambda x: x.seconds)
    time_vector = (time_days + (time_seconds/3600/24)).unique()

    for unit_name in c['unit_name'].unique():
        unit = c.query('unit_name == @unit_name')
        unit_b = b.query('unit_name == @unit_name')
        unit_s = s.query('unit_name == @unit_name')
        meanOfBaseline = np.mean(unit_b['spike_freq'])
        varOfBaseline = (unit_b['spike_freq'].std())/meanOfBaseline
        folds = unit['spike_freq']/meanOfBaseline
        if varOfBaseline < var and meanOfBaseline > minHz and meanOfBaseline < maxHz and not ((folds < 0.001).any()): 
            if plotFolds == True:
                plt.plot(time_vector, folds, color=(random.random(), random.random(), random.random(), .4))
            else:
                plt.plot(time_vector, unit['spike_freq'], color=(random.random(), random.random(), random.random(), .4))
            c_filter = c_filter.append(unit, ignore_index=True)
            b_filter = b_filter.append(unit_b, ignore_index=True)
        else:
            continue

    mean_freq_traces = c_filter.groupby(('condition', 'time'))['spike_freq'].mean()
    mean_freq_traces = mean_freq_traces.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    mean_freq_traces_b = b_filter.groupby(('condition', 'time'))['spike_freq'].mean()
    mean_freq_traces_b = mean_freq_traces_b.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    
    median_freq_traces = c_filter.groupby(('condition', 'time'))['spike_freq'].median()
    median_freq_traces = median_freq_traces.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    median_freq_traces_b = b_filter.groupby(('condition', 'time'))['spike_freq'].median()
    median_freq_traces_b = median_freq_traces_b.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    
    plt.xlabel('Time (days)')
    plt.ylim(0.00005,ymax)

    plt.title(title)
    meanOfMean = np.mean(mean_freq_traces_b['spike frequency'])
    meanOfMedian = np.mean(median_freq_traces_b['spike frequency'])
    if plotFolds == True:
        plt.axhline(y=1, xmin=0, xmax=1, hold=None, color='black')
        plt.plot(time_vector, mean_freq_traces['spike frequency']/meanOfMean, color=(0,0,0))
        plt.plot(time_vector, median_freq_traces['spike frequency']/meanOfMedian, 'r')
        plt.ylabel('Fold Induction of Spike Frequency (Hz)')
    else:
        plt.axhline(y=meanOfMean, xmin=0, xmax=1, hold=None, color='black')
        plt.plot(time_vector, mean_freq_traces['spike frequency'], color=(0,0,0))
        plt.plot(time_vector, median_freq_traces['spike frequency'], 'r')
        plt.ylabel('Spike Frequency (Hz)')

    plt.yscale('log')
    
    print(len(c_filter['unit_name'].unique()))
    print(len(c['unit_name'].unique()))
    
    plt.show()

def foldInductionPlusMean(cat_table, baseline_table, stim_table, condition, title, var=2.5, minHz = 0.01, maxHz = 100000, ind_filter = True, ymax = 10, plotFolds = True):
    '''
    Combine stim and ctrl fxns
    '''
    
    if ind_filter:
        foldInductionPlusMean_stim(cat_table, baseline_table, stim_table, condition, title, var, minHz, maxHz, ymax, plotFolds)
    else:
        foldInductionPlusMean_ctrl(cat_table, baseline_table, stim_table, condition, title, var, minHz, maxHz, ymax, plotFolds)


def count_active_neurons(cat_table, threshold, return_value):
    '''
    Count and plot the number of neurons firing above a threshold at each time point
    '''
    above_threshold = cat_table.query('spike_freq > @threshold')
    time_grouped_counts = above_threshold.groupby(('time'))['unit_name'].count()
    time_grouped_counts = time_grouped_counts.rename('count').reset_index() # Convert the multiindexed series back to a dataframe
    
    plt.plot(time_grouped_counts['time'], time_grouped_counts['count'])
    plt.xlabel('time')
    plt.ylabel('Number of active units')
    plt.title('Active units')
    if return_value:
        return time_grouped_counts
    
def compare_active_per_recording(cat_table, threshold, rec_starts, rec_ends, num_rec):
    '''
    For each recording session, find the number of new neurons and the 
    number of neurons that have stopped firing
    '''
    above_threshold = cat_table.query('spike_freq > @threshold')
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
    plt.plot_date(recs[1:num_rec], only_2, '-', label = "new")
    plt.plot_date(recs[1:num_rec], only_1, '-', label = "died")
    plt.legend()
    plt.xlabel('Recording session')
    plt.ylabel('Number of units')
    plt.title('Neuron turnover')
    
def compare_active_per_sec(cat_table, threshold):
    '''For each recording session, find the number of new neurons and the 
    number of neurons that have stopped firing
    '''
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

def unit_mean_freq_hist(category_dataframe, num_bins = 50):
    '''
    Plots histogram showing the distribution of mean firing rate of each unit in category_dataframe
    '''
    unit_freq_mean = category_dataframe.groupby(('unit_name'))['spike_freq'].mean()
    unit_freq_mean = unit_freq_mean.rename('spike frequency').reset_index() # Convert the multiindexed series back to a dataframe
    plt.hist(unit_freq_mean['spike frequency'], bins = num_bins)
    plt.title('Mean Firing Rate per Unit')

def select_neurons(cat_table, min_freq = 0, max_freq = 100000):
    '''
    Returns a version of cat_table only containing units whose mean frequency is between min_freq and max_freq
    '''
    unit_freq_mean = cat_table.groupby(('unit_name'))['spike_freq'].mean()
    unit_freq_mean = unit_freq_mean.rename('spike_freq').reset_index()
    filt = (unit_freq_mean['spike_freq'] > min_freq) & (unit_freq_mean['spike_freq'] < max_freq)
    selected_units = unit_freq_mean.loc[filt,'unit_name']
    return (cat_table.loc[cat_table['unit_name'].isin(selected_units)], selected_units)