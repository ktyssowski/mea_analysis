function process_spk_files_parallel(spk_paths, output_path)
    %% process_spk_file(spk_paths, output_path)
    %
    % processes one or more 

    if ~exist('output_path', 'var')
        [spk_dir, spk_name] = fileparts(spk_paths{1});
        output_path = fullfile(spk_dir, [spk_name, '.mat']);
        disp(['Output path not specified! Saving to ', output_path])
    end

    axis_loader = AxisLoader(spk_paths);
    output_file = matfile(output_path, 'Writable', true);
    cell_shape = axis_loader.get_cell_shape(); % The cell shape is dependent on the size of the plate
    all_channels = axis_loader.channels;    
    % This is how you have to preallocate object arrays in matlab
    temp_electrode_containers(1, cell_shape(1)*cell_shape(2)*cell_shape(3)*cell_shape(4)) = ElectrodeContainer();
    electrode_containers( ...
        cell_shape(1), ...
        cell_shape(2), ...
        cell_shape(3), ...
        cell_shape(4) ...
    ) = ElectrodeContainer();
    % We also need to store the timing of the last spike so that we can draw the x axis while plotting
    final_spike_time = datetime('1945-02-13 00:00:00');

    % Load all datasets before parfor loop
    %datasets = load_axis_datasets(spk_paths);%axis_loader.file_objs{1}.DataSets;
    
    % Get the number of channels
    num_chan = axis_loader.num_channels;
    % Create empty datetime array to store max times from each electrode
    last_spike_on_electrode_time = NaT(1,num_chan);%datetime([],[],[],[],[],[]);
    parfor i = 1:num_chan
        axis_loader_p = AxisLoader(spk_paths);
        channel = all_channels(i);
        spike_index = [ ... 
            channel.WellRow, ...
            channel.WellColumn, ...
            channel.ElectrodeColumn, ...
            channel.ElectrodeRow ...
        ];
        spike_data = axis_loader_p.load_data_set(channel);
       % disp(['Num Spikes: ', num2str(length(spike_data))])
        if length(spike_data) > 20 % Feature Extraction requires at least three spikes
            features = get_spike_features(spike_data); % generate spike features (we only use pca now)
            models = fit_models_to_features(features, 'pca'); % fit models (gmm) to pca
            n_clusters = estimate_n_clusters(models);
            clusters = cellfun(@(m) m.cluster(features.pc_scores), models, 'UniformOutput', false); % calculate cluster numbers
            spike_times = get_spike_times_from_spike_array(spike_data);
            spike_mat = get_spike_mat_from_spike_array(spike_data);
            % lambda fcn for computing mean waveforms functionally
            fn_get_mean_wfs = @(n) get_average_waveforms(spike_mat, n, clusters{n});
            mean_waveforms = arrayfun(fn_get_mean_wfs, 1:numel(clusters), 'UniformOutput', false);
            temp_electrode_containers(i) = ElectrodeContainer( ...
                spike_index, ...
                spike_times, ...
                'features', features, ...
                'cluster_model', models, ...
                'class_no', clusters, ...
                'contains_data', true, ...
                'valid', true(size(clusters)), ...
                'n_clusters', n_clusters, ...
                'mean_waveforms', mean_waveforms ...
            );
            % Get the final spike time on current electrode
            last_spike_on_electrode_time(i) = max(spike_times);  
        else
            temp_electrode_containers(i) = ElectrodeContainer( ...
                spike_index, ...
                'contains_data', false, ...
                'valid', false ...
            );
        end
    end
    
    % Update final spike time
    final_spike_time = max([final_spike_time, last_spike_on_electrode_time]);
    
    % Reshape temp_electrode_containers
    for i = 1:num_chan
        this_chan = all_channels(i);
        electrode_containers(...
            this_chan.WellRow, ...
            this_chan.WellColumn, ...
            this_chan.ElectrodeColumn, ...
            this_chan.ElectrodeRow...
            ) = temp_electrode_containers(i);
    end
    
    % Write data to the output file
    output_file.electrode_containers = electrode_containers;
    output_file.final_spike_time = final_spike_time;
    output_file.recording_start_time = axis_loader.recording_start_time;
    
function datasets = load_axis_datasets(filepaths)
    datasets = cell(size(filepaths));
    for i = 1:numel(filepaths)
        datasets{i} = AxisFile(filepaths{i}).DataSets.LoadData();
    end

function mean_waveforms = get_average_waveforms(spikes, n_clusters, class_numbers)
    mean_waveforms = zeros([n_clusters, size(spikes, 2)]);
    for i = 1:n_clusters
        mean_waveforms(i, :) = mean(spikes(class_numbers == i, :), 1);
    end

function n_clusters = estimate_n_clusters(models)
    % has to be done this way since matlab is an nasty betch w/o list comprehensions 0_0
    n_clusters = 1;
    for i = 1:numel(models)
        if models{n_clusters}.BIC < models{i}.BIC
            n_clusters = i;
        end
    end

function spike_data = load_electrode_data(num_files, datasets, spike_index)
%%% loads spike data for a single electrode from all files and
%%% concatenates the spikes
    temp = cell(1,num_files);
    for j = 1:num_files
        temp{j} = datasets{j}{spike_index(1), spike_index(2), ...
            spike_index(3), spike_index(4)};
    end
    [spike_data] =  [temp{:}];