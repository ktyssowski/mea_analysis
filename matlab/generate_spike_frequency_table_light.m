function generate_spike_frequency_table_light(mat_path, output_path, varargin)
%% generate_spike_frequency_table_light(mat_path, output_path, varargin)
%
% Generates a table of spike frequency for each unit specified in the mat file at mat_path
% see process_spk_files for details on generating this mat file.
% Also generates a table only containing spikes within "window" ms after the time
% of each pulse, and a table of spikes from the "window" ms before each spike.
%
% OPTIONS
%
% bin_size - size of the time bin (in seconds) to use when counting spikes. default = 60 seconds
% window - size of time window (in seconds) to use for detecting light
%    response. default = 0.050 ms
%
% anon fcn to test for files
is_file = @(fp) exist(fp, 'file');

parser = inputParser();
parser.addRequired('mat_path', is_file);
parser.addRequired('output_path');
parser.addParameter('bin_size', 60, @isnumeric);
parser.addParameter('window', 0.050, @isnumeric);
parser.parse(mat_path, output_path, varargin{:});

mat_data = load( ...
    mat_path, ...
    'electrode_containers', ...
    'final_spike_time', ...
    'recording_start_time', ...
    'stim_times' ...
);

bin_size = parser.Results.bin_size;
window = parser.Results.window;
electrode_containers = mat_data.electrode_containers;
final_spike_time = mat_data.final_spike_time;
recording_start_time = mat_data.recording_start_time; %contains start time of each recording
stim_times = mat_data.stim_times;

% only work with the containers that actually have data
containers_with_data = electrode_containers([electrode_containers(:).contains_data]);
num_units = sum([containers_with_data(:).n_clusters]);
num_bins = floor((final_spike_time - min(recording_start_time))/seconds(bin_size));

pre_frequency_mat = zeros([num_bins, num_units]);
light_frequency_mat = zeros([num_bins, num_units]);
frequency_mat = zeros([num_bins, num_units]);

curr_unit = 1;
unit_names = {};
for curr_container = containers_with_data(:)'
    unit_names = [unit_names, curr_container.get_unit_names()];
    for iClust = 1:curr_container.n_clusters
        unit_spike_times = curr_container.spike_times( ...
            curr_container.class_no{curr_container.n_clusters} == iClust ...
            );
        if ~isempty(stim_times)
            [unit_pre_spikes, unit_light_spikes] = light_filter_spikes(unit_spike_times, stim_times, window);
            pre_frequency_mat(:, curr_unit) = generate_frequency_timecourse( ...
                unit_pre_spikes, ...
                'start_time', min(recording_start_time), ...
                'end_time', final_spike_time, ...
                'bin_size', bin_size ...
                );
            light_frequency_mat(:, curr_unit) = generate_frequency_timecourse( ...
                unit_light_spikes, ...
                'start_time', min(recording_start_time), ...
                'end_time', final_spike_time, ...
                'bin_size', bin_size ...
                );
        end
        frequency_mat(:, curr_unit) = generate_frequency_timecourse( ...
            unit_spike_times, ...
            'start_time', min(recording_start_time), ...
            'end_time', final_spike_time, ...
            'bin_size', bin_size ...
        );
        curr_unit = curr_unit + 1;
    end
end

save('backup_arrays.mat', 'pre_frequency_mat', 'light_frequency_mat', 'frequency_mat', 'unit_names', ...
    'recording_start_time', 'bin_size');

% Convert matrices to tables with timing and save as csv
if ~isempty(stim_times)
    pre_spike_table = array2table(pre_frequency_mat, 'VariableNames', unit_names);
    pre_spike_table.time = [min(recording_start_time) + seconds(bin_size):seconds(bin_size):final_spike_time]';
    writetable(pre_spike_table, ['pre_' output_path]);
    light_spike_table = array2table(light_frequency_mat, 'VariableNames', unit_names);
    light_spike_table.time = [min(recording_start_time) + seconds(bin_size):seconds(bin_size):final_spike_time]';
    writetable(light_spike_table, ['light_' output_path]);
end
spike_table = array2table(frequency_mat, 'VariableNames', unit_names);
spike_table.time = [min(recording_start_time) + seconds(bin_size):seconds(bin_size):final_spike_time]';
writetable(spike_table, output_path);

function [pre_light_spikes, filtered_spikes] = light_filter_spikes(unit_spike_times, stim_times, window)
window = seconds(window);
pre_light_spikes = [];
filtered_spikes = [];
for stim_start = stim_times
    pre_pulse_spikes = unit_spike_times(unit_spike_times >= (stim_start - window) & ...
        unit_spike_times < stim_start);
    pulse_spikes = unit_spike_times(unit_spike_times >= stim_start & ...
        unit_spike_times <= (stim_start + window));
    pre_light_spikes = [pre_light_spikes pre_pulse_spikes];
    filtered_spikes = [filtered_spikes pulse_spikes];
end