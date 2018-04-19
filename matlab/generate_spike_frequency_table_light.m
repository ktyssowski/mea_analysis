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
% stim_space - number of milliseconds between light pulses. default = 500
%
% anon fcn to test for files
is_file = @(fp) exist(fp, 'file');

parser = inputParser();
parser.addRequired('mat_path', is_file);
parser.addRequired('output_path');
parser.addParameter('bin_size', 60, @isnumeric);
parser.addParameter('stim_space', 500, @isnumeric);
parser.addParameter('light', 0);

mat_data = load( ...
    mat_path, ...
    'electrode_containers', ...
    'final_spike_time', ...
    'recording_start_time', ...
    'stim_times' ...
);

parser.addParameter('stim_start', min(mat_data.stim_times));
parser.addParameter('stim_stop', mat_data.final_spike_time);
parser.parse(mat_path, output_path, varargin{:});


bin_size = parser.Results.bin_size;
stim_space = parser.Results.stim_space;
electrode_containers = mat_data.electrode_containers;
final_spike_time = mat_data.final_spike_time;
recording_start_time = mat_data.recording_start_time; %contains start time of each recording
stim_times = mat_data.stim_times;
stim_start = parser.Results.stim_start;
stim_stop = parser.Results.stim_stop;
light = parser.Results.light;

% only work with the containers that actually have data
containers_with_data = electrode_containers([electrode_containers(:).contains_data]);
num_units = sum([containers_with_data(:).n_clusters]);
num_bins = floor((final_spike_time - min(recording_start_time))/seconds(bin_size));

frequency_mat = zeros([num_bins, num_units]);
stim_resp = zeros(num_units,1);
autocorr = zeros(num_units,1);

curr_unit = 1;
unit_names = {};
for curr_container = containers_with_data(:)'
    unit_names = [unit_names, curr_container.get_unit_names()];
    for iClust = 1:curr_container.n_clusters
        unit_spike_times = curr_container.spike_times( ...
            curr_container.class_no{curr_container.n_clusters} == iClust ...
            );
        if ~isempty(stim_times) && light == 1
            [stim_resp(curr_unit), autocorr(curr_unit)] = check_responsive(unit_spike_times, stim_start, stim_stop, stim_space);
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

save('backup_arrays.mat', 'frequency_mat', 'unit_names', 'recording_start_time', 'final_spike_time', ...
    'bin_size', 'stim_resp', 'autocorr', 'output_path');

% Make sure there are no duplicate units
[unique_units, ia] = unique(unit_names);
if length(unique_units) ~= length(unit_names)
    fm2 = frequency_mat(:, ia);
    frequency_mat = fm2;
    unit_names = unique_units;
end

% Convert matrices to tables with timing and save as csv
spike_table = array2table(frequency_mat, 'VariableNames', unit_names);
spike_table.time = [min(recording_start_time) + seconds(bin_size):seconds(bin_size):final_spike_time]';
writetable(spike_table, output_path);
if ~isempty(stim_times) && light == 1
    resp_output_path = insertBefore(output_path, '.csv', '_resp_units');
    resp_table = table(unit_names', stim_resp, autocorr, 'VariableNames', {'unit_name', 'stim_resp', 'autocorr'});
    writetable(resp_table, resp_output_path);
end