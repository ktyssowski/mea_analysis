classdef NeuralUnit < handle

properties
    well
    electrode
    spikes
    class_no
    valid_class
    spike_times
    features
end

methods 
    obj = NeuralUnit(spikes, spike_times, well, electrode, varargin)
    %% NeuralUnit(spikes, spike_times, well, electrode, varargin)
    %
    %   Given a list of 
        parser = InputParser();
        parser.addRequired('spikes', @isnumeric)
        parser.addRequired('spike_times', @isnumeric)
        parser.addRequired('well')
        parser.addRequired('electrode')
        parser.addParameter('valid', true)
        parser.addParameter('class_no', 0)
        parser.addParameter('features', false)

        parser.parse(spikes, well, electrode, varargin{:});
        obj.spikes = parser.Results.spikes;
        obj.spike_times = parser.Results.spike_times;
        obj.well = parser.Results.well;
        obj.electrode = parser.Results.electrode;
        obj.class_no = parser.Results.class_no;
        obj.valid_class = parser.Reults.valid;
        obj.features = parser.Results.features;
    end
end
