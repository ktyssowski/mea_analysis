%%% Kate Letai
%%% 03-08-18

function [] = isi_hist(baseline_stop, condition)
%% isi_hist(baseline_stop)
%
% Calculates Inter-Spike Intervals for each neuron, and plots as
% histogram. Compares last hr of baseline, 1st hour of stim, and last hr of stim. Change
% check_cond.m before running this function to filter the desired
% condition.
%
% baseline_stop - datetime when drug is added
%
% condition - string for the condition being portrayed

[mat_filename, mat_dirname] = uigetfile('*.mat', 'Select matfile to load');
mat_path = fullfile(mat_dirname, mat_filename); % Open matfile of your choice
data_struct = load(mat_path, 'electrode_containers', 'final_spike_time');
electrode_containers = data_struct.electrode_containers;
stop = data_struct.final_spike_time;

% only work with the containers that actually have data
containers_with_data = electrode_containers([electrode_containers(:).contains_data]);

%start = datetime(2017, 01, 01, 12, 00, 00); %arbitrary start time earlier than any of my experiments
%stop = datetime(3000, 01, 01, 01, 01, 01); %arbitrary stop time later than my experiments

start = baseline_stop - hours(1);
stim_beg = baseline_stop + hours(1);
stim_end = stop - hours(1);

baseline_diff_all = [];
stim_diff_all_1 = [];
stim_diff_all_2 = [];
key=[];
% iterate through electrodes, and units
for curr_container = containers_with_data(:)'
    curr_units = curr_container.get_unit_names();
    if check_cond(curr_units(1))
        for iClust = 1:curr_container.n_clusters
            unit_spike_times = curr_container.spike_times( ...
                curr_container.class_no{curr_container.n_clusters} == iClust ...
                );
            baseline_spikes = unit_spike_times(isbetween(unit_spike_times, start, baseline_stop));
            stim_spikes_1 = unit_spike_times(isbetween(unit_spike_times, baseline_stop, stim_beg));
            stim_spikes_2 = unit_spike_times(isbetween(unit_spike_times, stim_end, stop));
            baseline_spikes = sort(baseline_spikes);
            stim_spikes_1 = sort(stim_spikes_1);
            stim_spikes_2 = sort(stim_spikes_2);
            % Calculate the difference between consecutive values
            baseline_diff = diff(baseline_spikes);
            stim_diff_1 = diff(stim_spikes_1);
            stim_diff_2 = diff(stim_spikes_2);
            baseline_diff_all = [baseline_diff_all, baseline_diff];
            stim_diff_all_1 = [stim_diff_all_1, stim_diff_1];
            stim_diff_all_2 = [stim_diff_all_2, stim_diff_2];
            if isempty(key) || key ~= 0
                figure(1);
                ax3=subplot(1,3,3);
                h3=histogram(stim_diff_2, 'Normalization', 'probability');
                title([curr_units(iClust) 'End ISI - ' condition]);
                ax2=subplot(1,3,2);
                h2=histogram(stim_diff_1, 'Normalization', 'probability');
                title([curr_units(iClust) 'Stim ISI - ' condition]);
                ax1=subplot(1,3,1);
                if ~isempty(baseline_diff)
                    histogram(baseline_diff, 'Normalization', 'probability');
                    title([curr_units(iClust) 'Baseline ISI - ' condition]);
                    linkaxes([ax1,ax2,ax3],'xy');
                end
              
                key = input('Press "0-Enter" to skip to all units. Press "Enter" to continue.');
            end
        end
    end
end
figure(2);
ax6=subplot(1,3,3);
h6=histogram(stim_diff_all_2, 'BinLimits', [seconds(0), minutes(10)], 'BinWidth', milliseconds(10), 'Normalization', 'probability');
title(['End ISI - All Units - ' condition]);
ax5=subplot(1,3,2);
h5=histogram(stim_diff_all_1, 'BinLimits', [seconds(0), minutes(10)], 'BinWidth', milliseconds(10), 'Normalization', 'probability');
title(['Stim ISI - All Units - ' condition]);
ax4=subplot(1,3,1);
histogram(baseline_diff_all, 'BinLimits', [seconds(0), minutes(10)], 'BinWidth', milliseconds(10), 'Normalization', 'probability');
title(['Baseline ISI - All Units - ' condition]);
linkaxes([ax4,ax5,ax6],'xy');
