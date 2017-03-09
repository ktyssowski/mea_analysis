function process_spk_file(spk_path, output_path)
    %% process_spk_file(spk_path)

    spk_file = AxisFile(spk_path);
    spk_cell = spk_file.DataSets.LoadData();
    feat_cell = cell(size(spk_cell));
    model_cell = cell(size(spk_cell));
    clust_cell = cell(size(spk_cell));

    for i = 1:numel(spk_cell)
        if ~isempty(spk_cell{i})
            features = get_spike_features(spk_cell{i});
            models = fit_models_to_features(features, 'pca');
            clusters = cellfun(@(m) m.cluster(features.pc_scores), models, 'UniformOutput', false)
            feat_cell{i} = features;
            model_cell{i} = models;
            clust_cell{i} = clusters;
        end
    end

    [spk_dir, spk_name] = fileparts(spk_path);
    output_path = fullfile(spk_dir, [spk_name, '.mat']);
    save(output_path, 'feat_cell', 'model_cell', 'clust_cell');
