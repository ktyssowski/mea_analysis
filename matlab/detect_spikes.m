%% Set Params
format shortEng

filename = '/media/sam/hdd1/maestro_recordings/001/001_170114_1536(000).raw'
well = 'B2'
electrode = '32'
detection_threshold = 0.75e5
sampling_frequency = 12.5e3
samples_before_spike = 11
samples_after_spike = 27
time_before_spike = samples_before_spike/sampling_frequency
time_after_spike = samples_after_spike/sampling_frequency
samples_per_spike = samples_before_spike + samples_after_spike + 1
minimum_spike_separation = samples_after_spike

%% Load Data
axis_file = AxisFile(filename);
data = axis_file.DataSets.LoadData(well, electrode, [100, 500])

%% Compute Nonlinear Energy
waveform = double(data{~isempty(data)}.Data);
nonlinear_energy = neo(waveform);

figure
plot(nonlinear_energy)
hold on
plot(xlim, [detection_threshold, detection_threshold])
hold off

%% Detect spikes
% locations detected in nonlinear energy must be shifted by one sample to account for 
%  a shift that occurs during nonlinear_energy detection
locs = peakseek(nonlinear_energy, minimum_spike_separation, detection_threshold) + 1; 
num_spikes = length(locs)
spikes = zeros([length(locs), samples_per_spike]);

for i = 1:num_spikes
    spikes(i, :) = waveform(locs(i)-samples_before_spike: locs(i)+samples_after_spike);
end

figure
for i = 1:num_spikes
    plot(spikes(i, :))
    hold on
end
