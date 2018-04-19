%%% Kate Letai
%%% 03-08-18

function [] = isi_hist(baseline_stop, condition)
%% isi_hist(baseline_stop)
%
% Calculates Inter-Spike Intervals for each neuron, and plots as
% histogram. Compares baseline and stimulated conditions. Change
% check_cond.m before running this function to filter the desired
% condition.
%
% baseline_stop - datetime when drug is added
%
% condition - string for the condition being portrayed

[mat_filename, mat_dirname] = uigetfile('*.mat', 'Select matfile to load');
mat_path = fullfile(mat_dirname, mat_filename); % Open matfile of your choice
data_struct = load(mat_path, 'electrode_containers');
electrode_containers = data_struct.electrode_containers;

% only work with the containers that actually have data
containers_with_data = electrode_containers([electrode_containers(:).contains_data]);

start = datetime(2017, 01, 01, 12, 00, 00); %arbitrary start time earlier than any of my experiments
stop = datetime(3000, 01, 01, 01, 01, 01); %arbitrary stop time later than my experiments

baseline_diff_all = [];
stim_diff_all = [];
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
            stim_spikes = unit_spike_times(isbetween(unit_spike_times, baseline_stop, stop));
            baseline_spikes = sort(baseline_spikes);
            stim_spikes = sort(stim_spikes);
            % Calculate the difference between consecutive values
            baseline_diff = diff(baseline_spikes);
            stim_diff = diff(stim_spikes);
            baseline_diff_all = [baseline_diff_all, baseline_diff];
            stim_diff_all = [stim_diff_all, stim_diff];
            if isempty(key) || key ~= 0
                figure(1);
                ax2=subplot(1,2,2);
                h1=histogram(stim_diff, 'Normalization', 'probability');
                title([curr_units(iClust) 'Stim ISI - ' condition]);
                ax1=subplot(1,2,1);
                if ~isempty(baseline_diff)
                    histogram(baseline_diff, 'Normalization', 'probability');
                    title([curr_units(iClust) 'Baseline ISI - ' condition]);
                    linkaxes([ax1,ax2],'xy');
                end
              
                key = input('Press "0-Enter" to exit. Press "Enter" to continue.');
            end
        end
    end
end
figure(2);
ax4=subplot(1,2,2);
h2=histogram(stim_diff_all, 'BinLimits', [seconds(0), minutes(10)], 'BinWidth', milliseconds(10), 'Normalization', 'probability');
title(['Stim ISI - All Units - ' condition]);
ax3=subplot(1,2,1);
histogram(baseline_diff_all, 'BinLimits', [seconds(0), minutes(10)], 'BinWidth', milliseconds(10), 'Normalization', 'probability');
title(['Baseline ISI - All Units - ' condition]);
linkaxes([ax3,ax4],'xy');
