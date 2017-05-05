function spike_mat = get_spike_mat_from_spike_array(spike_data)
%% spike_mat = get_spike_mat_from_spike_array(spike_data)
%
% spike_mat - an n x d matrix containing the spike waveforms. where n is the number of spikes
%  and d is the dimensionality of the waveforms
spike_mat = horzcat(spike_data(:).GetVoltageVector())';
