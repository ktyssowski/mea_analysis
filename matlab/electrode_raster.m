function electrode_raster(start, stop, stim_start)
timeframe = [start, stop];
stim_times = stim_start:milliseconds(500):(stim_start+hours(1));
[mat_filename, mat_dirname] = uigetfile('*.mat', 'Select matfile to load')
mat_path = fullfile(mat_dirname, mat_filename); % Open matfile of your choice
data_struct = load(mat_path, 'electrode_containers');
electrode_containers = data_struct.electrode_containers;
chosen = 0;
while chosen == 0
    electrode = input('Enter well as [row, column, elec_col, elec_row]:'); %Ask user for electrode
    curr_container = electrode_containers(electrode(1), electrode(2), electrode(3), electrode(4));
    all_times = curr_container.spike_times;
    if ~isempty(all_times)% && all_times(1) >= start && all_times(end) <= stop
        chosen = 1;
    else
        print('No data on this electrode for this time period. Please choose again.');
    end
end
stim_window = stim_times(isbetween(stim_times, timeframe(1), timeframe(2)));

% Get the spike times from each unit, do not bin, and store in a cell array with
% one cell for each unit. Also plot raster.
unit_cells = cell(curr_container.n_clusters,1);
curr_unit = 1;
for iClust = 1:curr_container.n_clusters
    unit_spike_times = all_times( ...
        curr_container.class_no{curr_container.n_clusters} == iClust ...
        );
    spks_in_window = unit_spike_times(isbetween(unit_spike_times, timeframe(1), timeframe(2)));
    unit_cells{curr_unit} = spks_in_window;
    figure(); hold on;
    row_values = curr_unit*ones(1,length(spks_in_window));
    plot(spks_in_window, row_values, '.');
    plot([stim_window], [curr_unit*ones(1,length(stim_window))], '*');
    curr_unit = curr_unit + 1;
end

ylabel('Unit');
xlabel('Time');
title('Spike Raster');