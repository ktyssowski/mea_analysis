function spikes_to_neuralunit(spikes)
%% spikes_to_neuralunit(spikes)
%
%

spike_times = spikes(:).Start;
spike_data = horzcat(spikes(:).Data)';
