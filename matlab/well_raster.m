function well_raster(start, stop, stim_times)
[mat_filename, mat_dirname] = uigetfile('*.mat', 'Select matfile to load')
mat_path = fullfile(mat_dirname, mat_filename); % Open matfile of your choice
data_struct = load(mat_path, 'electrode_containers');
electrode_containers = data_struct.electrode_containers;
electrode = input('Enter well as [row, column, elec_col, elec_row]:'); %Ask user for electrode

% Get the spike times from each electrode, do not bin, and store in a cell array with
% one cell for each electrode
electrode_num = 4*(electrode(3)-1) + electrode(4);
all_times = electrode_containers(electrode(1), electrode(2), electrode(3), electrode(4)).spike_times;
if ~isempty(all_times)
    time_window = all_times(isbetween(all_times, timeframe(1), timeframe(2)));
    figure(50); hist = histogram(time_window, nbins);
    electrode_cells{electrode_num} = hist.Values;
else
    electrode_cells{electrode_num} = zeros(1,nbins);
end

mat_data = load( ...
    mat_path, ...
    'electrode_containers', ...
    'final_spike_time', ...
    'recording_start_time', ...
    'stim_times' ...
);

bin_size = parser.Results.bin_size;
electrode_containers = mat_data.electrode_containers;
final_spike_time = mat_data.final_spike_time;
recording_start_time = mat_data.recording_start_time;

% only work with the containers that actually have data
containers_with_data = electrode_containers([electrode_containers(:).contains_data]);
num_units = sum([containers_with_data(:).n_clusters]);
num_bins = floor((final_spike_time - recording_start_time)/seconds(bin_size));

frequency_mat = zeros([num_bins, num_units]);

curr_unit = 1;
unit_names = {};
for curr_container = containers_with_data(:)'
    for iClust = 1:curr_container.n_clusters
        unit_spike_times = curr_container.spike_times( ...
            curr_container.class_no{curr_container.n_clusters} == iClust ...
        );
        curr_unit = curr_unit + 1;
    end
end

for unit = 
figure();
imagesc(electrode_mat); hold on;
plot([millistim, millistim], [0 17]);
%imagesc(bin_edges, [1:16], electrode_mat);
ylabel('Electrode');
xlabel('Time');
%xticks();
%xticklabels(time_labels);
title('Spike Heatmap');