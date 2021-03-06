import pandas as pd
import itertools as it
import seaborn as sns
import numpy as np
from pymea import matlab_compatibility as mc
from matplotlib import pyplot as plt
from matplotlib import mlab as mlab
import random
from datetime import datetime, timedelta
from pymea import filter_supplement as psupp
import math

def smooth(A, kernel_size=5, mode='same'):
    """
    Computes the moving average of A using a kernel_size kernel.
    """
    kernel = np.ones(kernel_size)/kernel_size
    return np.convolve(A, kernel, mode=mode)
    
def construct_categorized_dataframe(data_table, filter_dict, var_name = 'spike_freq'):
    """
    Takes the data from the matlab csv generated by preprocessing/sorting and applies filters to column names
    allowing for the categorization of data

    data_table - pandas DataFrame - should be populated from the .csv file generated by the 
        "generate_spike_frequency_table.m" matlab script
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
            var_name: condition_column,
            'unit_name': condition_column.name,
            'well': mc.get_well_number(condition_column.name)
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

def get_mean_med_traces(c_filter, data_col, b_filter, FR_gradient):
    """
    Calculates and returns the mean and median spike trace for the units in c_filter.
    
    c_filter - cat_table containing unit traces and conditions
    data_col - column of data in c_filter of which you wish to take the mean/median (usually spike_freq)
    b_filter - same as c_filter, but only containing the period of time during baseline
    FR_gradient - if True, assign color to each unit (for plotting later) corresponding to its FR
    """
    mean_freq_traces = c_filter.groupby(('condition', 'time'))[data_col].mean()
    mean_freq_traces = mean_freq_traces.rename(data_col).reset_index() # Convert the multiindexed series back to a dataframe
    mean_freq_traces_b = b_filter.groupby(('condition', 'time'))[data_col].mean()
    mean_freq_traces_b = mean_freq_traces_b.rename(data_col).reset_index() # Convert the multiindexed series back to a dataframe
    
    median_freq_traces = c_filter.groupby(('condition', 'time'))[data_col].median()
    median_freq_traces = median_freq_traces.rename(data_col).reset_index() # Convert the multiindexed series back to a dataframe
    median_freq_traces_b = b_filter.groupby(('condition', 'time'))[data_col].median()
    median_freq_traces_b = median_freq_traces_b.rename(data_col).reset_index() # Convert the multiindexed series back to a dataframe
    
    if FR_gradient == True:
        b_mean_freq = b_filter.groupby(('unit_name'))['spike_freq'].mean()
        b_mean_freq = b_mean_freq.rename('spike_freq')#.reset_index()
        u_color = (np.log10(b_mean_freq)+3)/3
    else:
        b_mean_freq = b_filter.groupby(('unit_name'))['spike_freq'].mean()
        b_mean_freq = b_mean_freq.rename('spike_freq')#.reset_index()
        u_color = np.random.random_sample()*b_mean_freq
    return(mean_freq_traces, mean_freq_traces_b, median_freq_traces, median_freq_traces_b, u_color)


def make_fold_plot(c_filter, t_start, u_color, FR_gradient, plotFolds, norm_by_median, norm_by_mean, mean_freq_traces_b, median_freq_traces_b, mean_freq_traces, median_freq_traces, y_scale, data_col, data_col_mm, title, ymax):
    """
    Plots fold induction of firing rate of units in c_filter over the course of the experiment.
    """
    plt.xlabel('Time (days)')
    plt.ylim(0.00005,ymax)
    for unit_name in c_filter['unit_name'].unique():
        unit = c_filter.query('unit_name == @unit_name')
        u_time = unit['time']
        time_vector_u = u_time-t_start
        time_vector_u = time_vector_u.map(lambda x: x.total_seconds()/86400.0)
        this_color = u_color[unit_name]
        if FR_gradient == True:
            if plotFolds == True:
                if norm_by_median.empty == False:
                    plt.plot(time_vector_u, np.divide(unit['folds'], norm_by_mean), color=plt.cm.gnuplot2(this_color, .4))
                else:
                    plt.plot(time_vector_u, unit['folds'], color=plt.cm.gnuplot2(this_color, .4))
            else:
                plt.plot(time_vector_u, unit[data_col], color=plt.cm.gnuplot2(this_color, .4))
        else:
            if plotFolds == True:
                if norm_by_median.empty == False:
                    plt.plot(time_vector_u, np.divide(unit['folds'], norm_by_mean), color=(random.random(), random.random(), random.random(), .4))
                else:
                    plt.plot(time_vector_u, unit['folds'], color=(random.random(), random.random(), random.random(), .4))
            else:
                plt.plot(time_vector_u, unit[data_col], color=(random.random(), random.random(), random.random(), .4))
        
    meanOfMean = np.mean(mean_freq_traces_b[data_col_mm])
    meanOfMedian = np.mean(median_freq_traces_b[data_col_mm])
    m_time = mean_freq_traces['time']
    time_vector_m = m_time-t_start
    time_vector_m = time_vector_m.map(lambda x: x.total_seconds()/86400.0)
    if plotFolds == True:
        plt.axhline(y=1, xmin=0, xmax=1, hold=None, color='black')
        if norm_by_mean.empty == False:
            plt.plot(time_vector_m, np.divide(mean_freq_traces[data_col]/meanOfMean,norm_by_mean), color=(0,0,0))
            plt.plot(time_vector_m, np.divide(median_freq_traces[data_col]/meanOfMedian,norm_by_median), 'r')
        else:
            plt.plot(time_vector_m, mean_freq_traces[data_col_mm]/meanOfMean, color=(0,0,0))
            plt.plot(time_vector_m, median_freq_traces[data_col_mm]/meanOfMedian, 'r')
        plt.ylabel('Fold Induction of Spike Frequency (Hz)')
    else:
        plt.axhline(y=meanOfMean, xmin=0, xmax=1, hold=None, color='black')
        plt.plot(time_vector_m, mean_freq_traces[data_col], color=(0,0,0))
        plt.plot(time_vector_m, median_freq_traces[data_col], 'r')      
        plt.ylabel('Spike Frequency (Hz)')
    plt.yscale(y_scale)
    plt.title(title)
    plt.show()
    return(meanOfMean, meanOfMedian, time_vector_m)

def foldInductionPlusMean_stim(cat_table, baseline_table, stim_table, condition, title, var, minHz, maxHz, ymax, plotFolds, foldMin, y_scale, filter_wells, data_col, data_col_mm, plot_group, FR_gradient, norm_by_mean, norm_by_median, plot_wells):
    """
    This function plots baseline-normalized plots for a given condition that include both all of the channels passing filters   and the mean(black)+median(red) of those channels--use for PTX-stimulated samples b/c filters out units that don't increase FR with stim
    """
    c = cat_table.query('condition == "%s"'%condition)
    b = baseline_table.query('condition == "%s"'%condition)
    s = stim_table.query('condition == "%s"'%condition)
    t_start = min(s['time'])
    
    c_filter, b_filter, count_real, count_live, cf = psupp.filter_neurons_homeostasis(c, b, s, ind_filter=True, var=var, minHz=minHz, maxHz=maxHz, foldMin=foldMin, filter_wells=filter_wells, data_col=data_col)
    
    if c_filter.empty:
        print "No valid units for condition",condition
        print('respond to drug: 0')
        print('stay alive: ' + str(count_live))
        print('real: ' + str(count_real))
        print('condition: ' + str(len(c['unit_name'].unique())))
        return

    mean_freq_traces, mean_freq_traces_b, median_freq_traces, median_freq_traces_b, u_color = get_mean_med_traces(c_filter, data_col_mm, b_filter, FR_gradient)
        
    meanOfMean, meanOfMedian, time_vector_m = make_fold_plot(c_filter, t_start, u_color, FR_gradient, plotFolds, norm_by_median, norm_by_mean, mean_freq_traces_b, median_freq_traces_b, mean_freq_traces, median_freq_traces, y_scale, data_col, data_col_mm, title, ymax)
    
    #plot individual well plots
    if plot_wells == True:
        for w in c_filter['well'].unique():
            plt.figure()
            well_c = c_filter.query('well == @w')
            well_b = b_filter.query('well == @w')
            well_mft, well_mftb, well_mdft, well_mdftb, well_color = get_mean_med_traces(well_c, data_col_mm, well_b, FR_gradient)
            well_title = 'Well ' + str(w)
            make_fold_plot(well_c, t_start, well_color, FR_gradient, plotFolds, norm_by_median, norm_by_mean, well_mftb, well_mdftb, well_mft, well_mdft, y_scale, data_col, data_col_mm, well_title, ymax)          

    print('respond to drug: ' + str(len(c_filter['unit_name'].unique())))
    print('stay alive: ' + str(count_live))
    print('real: ' + str(count_real))
    print('condition: ' + str(len(c['unit_name'].unique())))    
    
    return (c_filter['unit_name'].unique(), mean_freq_traces[data_col_mm]/meanOfMean, median_freq_traces[data_col_mm]/meanOfMedian, time_vector_m)


def foldInductionPlusMean_ctrl(cat_table, baseline_table, stim_table, condition, title, var, minHz, maxHz, ymax, plotFolds, foldMin, y_scale, filter_wells, data_col, data_col_mm, plot_group, FR_gradient, norm_by_mean, norm_by_median, plot_wells):
    '''
    This function plots baseline-normalized plots for a given condition that include both all of the channels passing filters and the mean(black)+median(red) of those channels--use for DMSO-stimulated samples
    '''
    c = cat_table.query('condition == "%s"'%condition)
    b = baseline_table.query('condition == "%s"'%condition)
    s = stim_table.query('condition == "%s"'%condition)
    t_start = min(s['time'])

    c_filter, b_filter, count_real, count_live, count_final = psupp.filter_neurons_homeostasis(c, b, s, ind_filter=False, var=var, minHz=minHz, maxHz=maxHz, foldMin=foldMin, filter_wells=False, data_col = data_col)
    
    if c_filter.empty:
        print "No valid units for condition",condition
        print('stay alive: ' + str(count_live))
        print('real: ' + str(count_real))
        print('condition: ' + str(len(c['unit_name'].unique())))
        return (0,0,0)
    
    mean_freq_traces, mean_freq_traces_b, median_freq_traces, median_freq_traces_b, u_color = get_mean_med_traces(c_filter, data_col_mm, b_filter, FR_gradient)
        
    meanOfMean, meanOfMedian, time_vector_m = make_fold_plot(c_filter, t_start, u_color, FR_gradient, plotFolds, norm_by_median, norm_by_mean, mean_freq_traces_b, median_freq_traces_b, mean_freq_traces, median_freq_traces, y_scale, data_col, data_col_mm, title, ymax)
    
    #plot individual well plots
    if plot_wells == True:
        for w in c_filter['well'].unique():
            plt.figure()
            well_c = c_filter.query('well == @w')
            well_b = b_filter.query('well == @w')
            well_mft, well_mftb, well_mdft, well_mdftb, well_color = get_mean_med_traces(well_c, data_col_mm, well_b, FR_gradient)
            well_title = 'Well ' + str(w)
            make_fold_plot(well_c, t_start, well_color, FR_gradient, plotFolds, norm_by_median, norm_by_mean, well_mftb, well_mdftb, well_mft, well_mdft, y_scale, data_col, data_col_mm, well_title, ymax)
    
    print('stay alive: ' + str(count_live))
    print('real: ' + str(count_real))
    print('condition: ' + str(len(c['unit_name'].unique())))
    
    plt.show()

    return (c_filter['unit_name'].unique(), mean_freq_traces[data_col_mm]/meanOfMean, median_freq_traces[data_col_mm]/meanOfMedian, time_vector_m)

def foldInductionPlusMean(cat_table, drug_time, condition, title, var=10, minHz = 0.001, maxHz = 100, ind_filter = True, ymax = 10, plotFolds = True, foldMin = 0.001, y_scale = 'linear', filter_wells = False, data_col ='spike_freq', data_col_mm = 'folds', plot_group = 0, FR_gradient = True, norm_by_mean = pd.Series([]), norm_by_median = pd.Series([]), plot_wells=True):
    '''
    Combine stim and ctrl fxns
    '''
    mean = False
    median = False
    baseline_table = cat_table.query('time < @drug_time')
    stim_table = cat_table.query('time >= @drug_time')
    if ind_filter:
        filtered_units, mean, median, time_vector = foldInductionPlusMean_stim(cat_table, baseline_table, stim_table, condition, title, var, minHz, maxHz, ymax, plotFolds, foldMin, y_scale, filter_wells, data_col, data_col_mm, plot_group, FR_gradient, norm_by_mean, norm_by_median, plot_wells)
    else:
        filtered_units, mean, median, time_vector = foldInductionPlusMean_ctrl(cat_table, baseline_table, stim_table, condition, title, var, minHz, maxHz, ymax, plotFolds, foldMin, y_scale, filter_wells, data_col, data_col_mm, plot_group, FR_gradient, norm_by_mean, norm_by_median, plot_wells)
        
    return filtered_units, mean, median, time_vector
