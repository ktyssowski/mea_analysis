classdef ElectrodeContainer < handle
    
    properties
        well
        electrode
        spikes
        class_no
        valid_class
        spike_times
        features
        cluster_model
        n_clusters
    end
    
    methods
        function obj = ElectrodeContainer(spikes, spike_times, varargin)
            %% NeuralUnit(spikes, spike_times, varargin)
            %
            %   Given a list of
            parser = inputParser();
            parser.addRequired('spikes', @isnumeric);
            parser.addRequired('spike_times', @isnumeric);
            parser.addParameter('valid', true);
            parser.addParameter('class_no', 0);
            parser.addParameter('features', false);
            parser.addParameter('cluster_model', false);
            parser.addParameter('n_clusters', 1)
            
            parser.parse(spikes, spike_times, varargin{:});
            obj.spikes = parser.Results.spikes;
            obj.spike_times = parser.Results.spike_times;
            obj.class_no = parser.Results.class_no;
            obj.valid_class = parser.Results.valid;
            obj.features = parser.Results.features;
            obj.cluster_model = parser.Results.cluster_model;
            obj.n_clusters = parser.Results.n_clusters;
        end
    end
end
