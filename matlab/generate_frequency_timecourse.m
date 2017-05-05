function [freq, edges] = generate_frequency_timecourse(spike_mat, spike_times)
%% freq = generate_frequency_timecourse(spike_times, [options])
%
% spike_times - matlab datetime objects corresponding to the start of each spike to be considered
%
% OPTIONS
%
% start_time - datetime corresponding to the start time of the recording (defaults to the first spike_time)
% end_time - datetime corresponding to the end time of the recording (defaults to the last spike_time)
% bin_size - size of time bins to use when calculating frequency (in seconds: default 300)
%
% OUTPUT
%
% freq - 
% edges - 

edges = start_time:seconds(bin_size):end_time;
freq = zeros(size(edges));
spike_times = sort(spike_times);
curr_spike_ind = 1;
for i = 1:length(edges)
    while spike_times(curr_spike_ind) < edges(i)
        freq(i) = freq(i) + 1;
        if spike_times(curr_spike_ind) < length(spike_times)
            curr_spike_ind = curr_spike_ind + 1;
        else
            break;
        end
    end
end
