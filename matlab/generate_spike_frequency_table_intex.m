% Kate Letai
% 7/25/18
function generate_spike_frequency_table_intex(mat_path, output_path, varargin)
%%
%
%
%
%
% anon fcn to test for files
is_file = @(fp) exist(fp, 'file');

parser = inputParser();
parser.addRequired('mat_path', is_file);
parser.addRequired('output_path');
parser.addParameter('pulse_width_sec', 0.5, @isnumeric);
parser.addParameter('pulse_space_sec', 5, @isnumeric);
parser.addParameter('num_cond', 16, @isnumeric);
parser.parse(mat_path, output_path, varargin{:});

mat_data = load( ...
    mat_path, ...
    'electrode_containers', ...
    'final_spike_time', ...
    'recording_start_time', ...
    'stim_times' ...
);

pulse_width_sec = parser.Results.pulse_width_sec;
pulse_space_sec = parser.Results.pulse_space_sec;
num_cond = parser.Results.num_cond;
electrode_containers = mat_data.electrode_containers;
stim_times = mat_data.stim_times;
 
% Make new stim_times array including every pulse
pulse_space_dur = seconds(pulse_space_sec);
stim_times_add = (0:num_cond-1)*pulse_space_dur;
stim_times_add = repmat(stim_times_add, 1, length(stim_times));
stim_times_all = repelem(stim_times, num_cond); 
stim_times_all = stim_times_all + stim_times_add;

% Set start and stop of stimulation
stim_start_time = stim_times(1);
stim_stop_time = stim_times_all(end) + seconds(pulse_space_sec);
bin_size = pulse_width_sec;

% only work with the containers that actually have data
containers_with_data = electrode_containers([electrode_containers(:).contains_data]);
num_units = sum([containers_with_data(:).n_clusters]);
num_bins = floor((stim_stop_time - stim_start_time)/seconds(bin_size));

frequency_mat = zeros([num_bins, num_units]);
times_to_first = nan([length(stim_times_all), num_units]);
initial_freqs = nan([length(stim_times_all), num_units]);

curr_unit = 1;
unit_names = {};
for curr_container = containers_with_data(:)'
    unit_names = [unit_names, curr_container.get_unit_names()];
    for iClust = 1:curr_container.n_clusters
        unit_spike_times = curr_container.spike_times( ...
            curr_container.class_no{curr_container.n_clusters} == iClust ...
        );
    unit_spike_times = unit_spike_times((unit_spike_times >= stim_start_time & unit_spike_times <= stim_stop_time));
        frequency_mat(:, curr_unit) = generate_frequency_timecourse( ...
            unit_spike_times, ...
            'start_time', stim_start_time, ...
            'end_time', stim_stop_time, ...
            'bin_size', bin_size ...
        );
    [times_to_first(:, curr_unit), initial_freqs(:, curr_unit)] = calc_first_spikes(unit_spike_times, stim_times_all);
        curr_unit = curr_unit + 1;
    end
end

%save('backup_mat_2.mat', 'frequency_mat', 'unit_names');
% Make sure there are no duplicate units
[unique_units, ia] = unique(unit_names);
if length(unique_units) ~= length(unit_names)
    fm2 = frequency_mat(:, ia);
    frequency_mat = fm2;
    unit_names = unique_units;
end
        
spike_table = array2table(frequency_mat, 'VariableNames', unit_names);
spike_table.time = datestr(((stim_start_time + seconds(bin_size)):seconds(bin_size):stim_stop_time)', 'dd-mmm-yyyy HH:MM:SS.FFF'); % saves trailing edges of bin times
writetable(spike_table, output_path);

% Save stim times if they exist
if isfield(mat_data, 'stim_times')
    stim_table = table(mat_data.stim_times', second(mat_data.stim_times)', 'VariableNames', {'date_time', 'seconds'});
    stim_table.firsts = array2table(times_to_first, 'VariableNames', unit_names);
    stim_table.freqs = array2table(initial_freqs, 'VariableNames', unit_names);
    writetable(stim_table, 'stim_table.csv');
end
