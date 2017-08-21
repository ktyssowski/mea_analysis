%%% Kate Letai
%%% 07-31-17 
%%% Makes heatmap of spikes vs time for one well in order to determine
%%% timing of the light pulses.
function spike_heatmap(nbins, start, stop)
[mat_filename, mat_dirname] = uigetfile('*.mat', 'Select matfile to load')
mat_path = fullfile(mat_dirname, mat_filename); % Open matfile of your choice
data_struct = load(mat_path, 'electrode_containers');
electrode_containers = data_struct.electrode_containers;
well = input('Enter well as [row, column]:'); %Ask user for well
timeframe = [start, stop];
milli_dur = milliseconds(stop-start);
time_labels = datestr(start + milliseconds(0:10:milli_dur));

% Get the spike times from each electrode, bin in 10ms bins, and store in a cell array with
% one cell for each electrode
electrode_cells = cell(16,1);
for electrode_row = 1:4
    for electrode_column = 1:4
        electrode_num = 4*(electrode_column-1) + electrode_row;
        all_times = electrode_containers(well(1), well(2), electrode_column, electrode_row).spike_times;
        if ~isempty(all_times)
            time_window = all_times(isbetween(all_times, timeframe(1), timeframe(2)));
            figure(50); hist = histogram(time_window, nbins);
            electrode_cells{electrode_num} = hist.Values;
        else
            electrode_cells{electrode_num} = zeros(1,nbins);
        end
    end
end

bin_edges = hist.BinEdges;
electrode_mat = cell2mat(electrode_cells);
figure();
imagesc(electrode_mat);
%imagesc(bin_edges, [1:16], electrode_mat);
ylabel('Electrode');
xlabel('Time');
%xticks();
%xticklabels(time_labels);
title('Spike Heatmap');
        
