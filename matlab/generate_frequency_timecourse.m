function [freq, edges] = generate_frequency_timecourse(spike_times, varargin)
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
% freq - array containing frequency counts of the number of spikes that occur in each time bin  
% edges - datetime array corresponding to the trailing edge of each histogram bin
%
% note: this is essentially a remake of the hist function that works on matlab datetime arrays

isdatetime = @(t) isa(t, 'datetime');

parser = inputParser();
parser.addRequired('spike_times', isdatetime);
parser.addParameter('start_time', min(spike_times), isdatetime);
parser.addParameter('end_time', max(spike_times), isdatetime);
parser.addParameter('bin_size', 300, @isnumeric);
parser.parse(spike_times, varargin{:});

start_time = parser.Results.start_time;
end_time = parser.Results.end_time;
bin_size = parser.Results.bin_size;

edges = [start_time:seconds(bin_size):end_time]';
freq = zeros(size(edges));
spike_times = sort(spike_times);
curr_spike_ind = 1;
for i = 1:length(edges)
    while spike_times(curr_spike_ind) < edges(i)
        freq(i) = freq(i) + 1;
        if curr_spike_ind < length(spike_times)
            curr_spike_ind = curr_spike_ind + 1;
        else
            break;
        end
    end
end
