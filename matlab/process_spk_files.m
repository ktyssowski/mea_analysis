function process_spk_file(spk_paths, output_path)
    %% process_spk_file(spk_paths, output_path)
    %
    % processes one or more 

    spk_datasets = load_axis_datasets(spk_paths)
    spk_cell = cellfun(@horzcat, spk_datasets{:}, 'UniformOutput', false);
    size(spk_cell)
    feat_cell = cell(size(spk_cell));
    model_cell = cell(size(spk_cell));
    clust_cell = cell(size(spk_cell));

    for i = 1:numel(spk_cell)
        disp(['Num Spikes: ', num2str(length(spk_cell{i}))])
        if length(spk_cell{i}) > 20 % Feature Extraction requires at least three spikes
            features = get_spike_features(spk_cell{i});
            models = fit_models_to_features(features, 'pca');
            clusters = cellfun(@(m) m.cluster(features.pc_scores), models, 'UniformOutput', false);
            feat_cell{i} = features;
            model_cell{i} = models;
            clust_cell{i} = clusters;
        end
    end

    container_cells = cellfun(@cells_to_container, spk_cell, feat_cell, model_cell, clust_cell, 'UniformOutput', false);
    electrode_containers = reshape([container_cells{:}], size(container_cells))

    if ~exist('output_path', 'var')
        [spk_dir, spk_name] = fileparts(spk_paths{1});
        output_path = fullfile(spk_dir, [spk_name, '.mat']);
        disp(['Output path not specified! Saving to ', output_path])
    end
    save(output_path, 'electrode_containers', '-v7.3');

function datasets = load_axis_datasets(filepaths)
    datasets = cell(size(filepaths));
    for i = 1:numel(filepaths)
        datasets{i} = AxisFile(filepaths{i}).DataSets.LoadData();
    end

function container = cells_to_container(spikes, feat_struct, model, cluster_array)
    if length(spikes) > 20 % This is the minimum number of spikes that are processed in main
        spike_mat = horzcat(spikes(:).GetVoltageVector())';
        spike_times = spike_times_to_datetime( ...
            spikes(1).Source.Header.FileStartTime, ...
            [spikes(:).Start] ...
        );
        valid = true(size(cluster_array));
        contains_data = true;
    else
        spike_mat = [];
        spike_times = [];
        valid = false;
        contains_data = false;
    end

    container = ElectrodeContainer( ...
        spike_mat,                  ...
        spike_times,                ...
        'valid', valid,             ...
        'class_no', cluster_array,  ...
        'features', feat_struct,    ...
        'cluster_model', model,     ...
        'contains_data', contains_data ...
    );

function dts = spike_times_to_datetime(fst, spike_starts)
    %% dts = spike_times_to_datetime(file_start_time, spike_starts)
    %
    % 
    for i = 1:length(spike_starts)
        dts(i) = datetime( ...
            fst.Year, ...
            fst.Month, ...
            fst.Day, ...
            fst.Hour, ...
            fst.Minute, ...
            fst.Second + spike_starts(i) ...
        );
    end
