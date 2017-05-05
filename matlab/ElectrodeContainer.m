classdef ElectrodeContainer < handle
    properties
        well
        electrode
        spike_index
        spike_times
        class_no
        valid_class
        features
        cluster_model
        n_clusters
        contains_data
        mean_waveforms
    end
    
    methods
        function obj = ElectrodeContainer(varargin)
            %% ElectrodeContainer([spike_index], varargin)
            %
            %   Container for data associated with an electrode
            % TODO add params here
            parser = inputParser();
            parser.addOptional('spike_index', [], @isnumeric);
            parser.addOptional('spike_times', []);
            parser.addParameter('contains_data', true);
            parser.addParameter('valid', true);
            parser.addParameter('class_no', 0);
            parser.addParameter('features', false);
            parser.addParameter('cluster_model', false);
            parser.addParameter('n_clusters', 1);
            parser.addParameter('mean_waveforms', []);
            
            parser.parse(varargin{:});
            obj.spike_index = parser.Results.spike_index;
            obj.spike_times = parser.Results.spike_times;
            obj.contains_data = parser.Results.contains_data;
            obj.class_no = parser.Results.class_no;
            obj.valid_class = parser.Results.valid;
            obj.features = parser.Results.features;
            obj.cluster_model = parser.Results.cluster_model;
            obj.n_clusters = parser.Results.n_clusters;
            obj.mean_waveforms = parser.Results.mean_waveforms;
        end

        function spk_container = create_spike_container(obj, spikes)
            spk_container = SpikeContainer( ...
                spikes, ...
                obj.spike_index, ...
                obj.spike_times, ...
                'contains_data', obj.contains_data, ...
                'valid', obj.valid_class, ...
                'class_no', obj.class_no, ...
                'features', obj.features, ...
                'cluster_model', obj.cluster_model, ...
                'n_clusters', obj.n_clusters, ...
                'mean_waveforms', obj.mean_waveforms ...
            );
        end
    end
end
