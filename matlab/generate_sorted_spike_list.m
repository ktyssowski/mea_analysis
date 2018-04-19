function [] = generate_sorted_spike_list(mat_path, csv_output_path)
%% generate_sorted_spike_list(mat_path)
%
% mat_path - path to sorted matfile
%
% generates .csv file similar containing spike times and unit labels
% (sorted at each electrode).

% open sorted matfile
mat_data = load( ...
    mat_path, ...
    'electrode_containers' ...
);
electrode_containers = mat_data.electrode_containers;

% only work with the containers that actually have data
containers_with_data = electrode_containers([electrode_containers(:).contains_data]);

spikes = [];
units = [];
amplitude = [];

% iterate through electrodes
for curr_container = containers_with_data(:)'
    unit_names = curr_container.get_unit_names();
    spike_times = curr_container.spike_times;
    unit_assignments = curr_container.class_no{curr_container.n_clusters};
    unit_labels = unit_names(unit_assignments);
    spikes = [spikes; spike_times'];
    if size(unit_labels,1) > 1
        unit_labels = unit_labels';
    end
    units = [units; unit_labels'];
    curr_amp = curr_container.features.peak_height;
    amplitude = [amplitude; curr_amp];
end

sorted_spike_table = table(spikes, units, amplitude, 'VariableNames', {'Time', 'Electrode', 'Amplitude'});
writetable(sorted_spike_table, csv_output_path);

