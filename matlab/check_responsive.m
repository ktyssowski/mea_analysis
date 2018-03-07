%%% Kate Letai
%%% 10-31-17

function [response, ac] = check_responsive(all_times, start, stop, peak)
%% check_responsiveness(all_times, start, stop, peak)
%
% Checks autocorrelation of spikes in all_spikes. If a peak occurs at "peak"
% (the # of milliseconds between stimulations), then a response is
% detected.

dur = milliseconds(stop-start);
in_window = all_times(isbetween(all_times, start, stop));
times = zeros(1,ceil(dur));
milli_times = milliseconds(in_window-start)+1;

for spike = floor(milli_times)
    times(spike) = times(spike)+1;
end

[ac, ~, bounds] = autocorr(times,1000,0,25);
ac = ac(peak+1);
if ac > bounds(1)
    response = 1;
else
    response = 0;
end
