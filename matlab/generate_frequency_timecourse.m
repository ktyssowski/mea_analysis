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
parser.addParameter('bin_size', 60, @isnumeric);
parser.parse(spike_times, varargin{:});

start_time = parser.Results.start_time;
end_time = parser.Results.end_time;
bin_size = parser.Results.bin_size;

[freq, edges] = compute_freq_bins(spike_times, start_time, end_time, bin_size);

function [freq, edges] = compute_freq_bins(spike_times, start_time, end_time, bin_size)
    edges = [0:bin_size:seconds(end_time - start_time)]';
    spike_times = seconds(spike_times - start_time);
    spike_accumulator = bsxfun(@le, spike_times, edges);
    spike_counts = sum(spike_accumulator, 2);
    freq = diff(spike_counts);
    edges = edges(2:end); % edges represent the trailing edge, and the first edge here is the start of the recording
