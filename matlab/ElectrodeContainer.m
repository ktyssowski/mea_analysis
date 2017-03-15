classdef ElectrodeContainer < handle
    
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
        function obj = ElectrodeContainer(spikes, spike_times, well, electrode, varargin)
            %% NeuralUnit(spikes, spike_times, well, electrode, varargin)
            %
            %   Given a list of
            parser = inputParser();
            parser.addRequired('spikes', @isnumeric);
            parser.addRequired('spike_times', @isnumeric);
            parser.addRequired('well');
            parser.addRequired('electrode');
            parser.addParameter('valid', true);
            parser.addParameter('class_no', 0);
            parser.addParameter('features', false);
            parser.addParameter('models', false);
            parser.addParemeter('n_clusters', 1)
            
            parser.parse(spikes, well, electrode, varargin{:});
            obj.spikes = parser.Results.spikes;
            obj.spike_times = parser.Results.spike_times;
            obj.well = parser.Results.well;
            obj.electrode = parser.Results.electrode;
            obj.class_no = parser.Results.class_no;
            obj.valid_class = parser.Reults.valid;
            obj.features = parser.Results.features;
            obj.models = parser.Results.models;
            obj.n_clusters = parser.Results.n_clusters;
        end
    end
end
