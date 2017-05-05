function spike_times = get_spike_times_from_spike_array(spikes)
%% spike_times = get_spike_times_from_spike_array(spikes)
%
% returns a vector of matlab `datetime`s corresponding to the time of each spike in spikes

% Extract the file start times from the spike objects.
%  matlab is the worst so you have to use a loop like this
file_start_times = cell(size(spikes));
for i = 1:numel(spikes)
    file_start_times{i} = spikes(i).Source.Header.FileStartTime;
end

% Calculate the datetimes. Once again, matlab is the worst so the results are returned as a cell array
spike_times = arrayfun( ...
    @spike_time_to_datetime, ...
    [file_start_times{:}], ...
    [spikes(:).Start], ...
    'UniformOutput', false ...
);

% Convert the cell array to a datetime array, like God intended
spike_times = [spike_times{:}];
