classdef ElectrodeContainer < handle
    properties
        well
        electrode
        spike_index
        class_no
        valid_class
        features
        cluster_model
        n_clusters
        contains_data
    end
    
    methods
        function obj = ElectrodeContainer(varargin)
            %% NeuralUnit([spike_index], varargin)
            %
            %   Container for the 
            parser = inputParser();
            parser.addOptional('spike_index', [], @isnumeric);
            parser.addParameter('contains_data', true);
            parser.addParameter('valid', true);
            parser.addParameter('class_no', 0);
            parser.addParameter('features', false);
            parser.addParameter('cluster_model', false);
            parser.addParameter('n_clusters', 1);
            
            parser.parse(varargin{:});
            obj.spike_index = parser.Results.spike_index;
            obj.contains_data = parser.Results.contains_data;
            obj.class_no = parser.Results.class_no;
            obj.valid_class = parser.Results.valid;
            obj.features = parser.Results.features;
            obj.cluster_model = parser.Results.cluster_model;
            obj.n_clusters = parser.Results.n_clusters;
        end

        function spk_container = create_spike_container(obj, spikes, spike_times)
            spk_container = SpikeContainer( ...
                spikes, ...
                spike_times, ...
                obj.spike_index, ...
                'contains_data', obj.contains_data, ...
                'valid', obj.valid_class, ...
                'class_no', obj.class_no, ...
                'features', obj.features, ...
                'cluster_model', obj.cluster_model, ...
                'n_clusters', obj.n_clusters ...
            );
        end
    end
end
