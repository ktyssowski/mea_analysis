classdef SpikeContainer < ElectrodeContainer
    properties
        spikes
    end

    methods
        function obj = SpikeContainer(spikes, varargin)
            %%  obj = SpikeContainer(spikes, varargin)
            %
            % spikes - n x d containing spike waveforms, where n is the number of spikes, 
            %  and d is the dimensionality of each spike

            %% Call superclass constructor
            obj = obj@ElectrodeContainer(varargin{:})

            %%
            parser = inputParser();
            parser.addRequired('spikes', @isnumeric)
            parser.parse(spikes);
            obj.spikes = parser.Results.spikes;
        end

        function n_spikes = get_number_of_spikes(obj)
            n_spikes = size(obj.spikes, 1);
        end
        
        function electrode_container = get_electrode_container(obj)
            electrode_container = ElectrodeContainer( ...
                obj.spike_index, ...
                obj.spike_times, ...
                'contains_data', obj.contains_data, ...
                'valid', obj.valid_class, ...
                'class_no', obj.class_no, ...
                'features', obj.features, ...
                'cluster_model', obj.cluster_model, ...
                'n_clusters', obj.n_clusters ...
            );
        end

        function avg_waveforms = get_average_waveforms(obj)
            avg_waveforms = zeros([obj.n_clusters, size(obj.spikes, 2)])
            for i = 1:obj.n_clusters
                avg_waveforms(i, :) = mean(obj.spikes(obj.class_no == i, :), 1);
            end
        end
    end
end
