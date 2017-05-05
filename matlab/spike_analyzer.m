function varargout = spike_analyzer(varargin)
% SPIKE_ANALYZER MATLAB code for spike_analyzer.fig
%      SPIKE_ANALYZER, by itself, creates a new SPIKE_ANALYZER or raises the existing
%      singleton*.
%
%      H = SPIKE_ANALYZER returns the handle to a new SPIKE_ANALYZER or the handle to
%      the existing singleton*.
%
%      SPIKE_ANALYZER('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in SPIKE_ANALYZER.M with the given input arguments.
%
%      SPIKE_ANALYZER('Property','Value',...) creates a new SPIKE_ANALYZER or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before spike_analyzer_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to spike_analyzer_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help spike_analyzer

% Last Modified by GUIDE v2.5 21-Mar-2017 15:46:12

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @spike_analyzer_OpeningFcn, ...
                   'gui_OutputFcn',  @spike_analyzer_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before spike_analyzer is made visible.
function spike_analyzer_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to spike_analyzer (see VARARGIN)

% Choose default command line output for spike_analyzer
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes spike_analyzer wait for user response (see UIRESUME)
% uiwait(handles.figure1);
handles.plot_spike_means = false;
handles = load_data(handles);
handles = analysis_loop(handles);


% --- Outputs from this function are returned to the command line.
function varargout = spike_analyzer_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;

%% -------------- DATA IO -------------- %%

function handles = load_data(handles)
%% handles = load_data(handles)
%
%  Loads electrode_containers from a mat file and initializes the current container as the first
    [mat_filename, mat_dirname] = uigetfile('*.mat', 'Select matfile to load')
    handles.mat_path = fullfile(mat_dirname, mat_filename)
    [spike_filenames, spike_dirname] = uigetfile('*.spk', 'Select spkfile(s) to load', 'MultiSelect', 'on');
    full_spike_path = @(spike_filename) fullfile(spike_dirname, spike_filename);
    spike_paths = cellfun(full_spike_path, spike_filenames, 'UniformOutput', false)
    if iscell(spike_paths)
        handles.spike_paths = spike_paths;
    else
        handles.spike_paths = {spike_paths};
    end
    handles.axis_loader = AxisLoader(handles.spike_paths);
    data_struct = load(handles.mat_path, 'electrode_containers');
    handles.electrode_containers = data_struct.electrode_containers;
    handles.curr_index = 1;
    handles = load_curr_container(handles);
    if ~handles.curr_container.contains_data
        disp_skip_msg(handles);
        handles = next_electrode(handles);
    end

function handles = load_curr_container(handles)
    electrode_container = handles.electrode_containers(handles.curr_index)
    spk_data = handles.axis_loader.load_data_set_from_index(electrode_container.spike_index)
    spikes = horzcat(spk_data(:).GetVoltageVector())';
    handles.curr_container = electrode_container.create_spike_container(spikes);
    n_spikes = handles.curr_container.get_number_of_spikes();
    n_sample_spikes = 1000; %% TODO set as param
    if n_spikes > n_sample_spikes 
        handles.sample_spikes = datasample(1:n_spikes, n_sample_spikes, 'Replace', false);
    else
        handles.sample_spikes = 1:n_spikes;
    end

function handles = update_curr_container(handles)
    handles.electrode_containers(handles.curr_index) = handles.curr_container.get_electrode_container();

function save_data(handles)
%% save_data(handles)
%
%
    electrode_containers = handles.electrode_containers;
    save(handles.mat_path, 'electrode_containers', '-v7.3');

%% --------------- DISPLAY ----------------%%

function handles = refresh_display(handles)
%% refresh_display(handles)
%
% 
    axes(handles.main_axes)
    handles = plot_features(handles);
    axes(handles.secondary_axes)
    if handles.plot_spike_means
        handles = plot_spike_means(handles)
    else
        handles = plot_spikes(handles);
    end
    handles = refresh_colors(handles);

function handles = plot_features(handles)
%% plot_features(container)
%
% Creates a 3d scatter plot of the data in pc space
    handles.curr_container
    features = handles.curr_container.features.pc_scores(handles.sample_spikes, :); 
    handles.scatter_handle = scatter3(features(:, 1), features(:, 2), features(:, 3), 'filled');
    labels = arrayfun(@num2str, 1:handles.curr_container.n_clusters, 'UniformOutput', false);
    legend(labels)

function handles = plot_spikes(handles)
%% plot_spikes(container)
%
%
    handles.spike_handles = cell(size(handles.sample_spikes));
    for i = 1:length(handles.sample_spikes)
        spike_no = handles.sample_spikes(i);
        handles.spike_handles{i} = plot(handles.curr_container.spikes(spike_no, :));
        hold on
    end
    hold off

function handles = plot_spike_means(handles)
    handles.spike_mean_handles = cell(size(handles.curr_container.n_clusters, 1));
    for iCluster = 1:handles.curr_container.n_clusters
        cluster_spikes = handles.curr_container.class_no{handles.curr_container.n_clusters} == iCluster;
        mean_spike = mean(handles.curr_container.spikes(cluster_spikes, :), 1);
        handles.spike_mean_handles{iCluster} = plot(mean_spike, 'LineWidth', 2);
        hold on
    end
    hold off

function handles = refresh_colors(handles)
%% handles = refresh_colors(handles)
%
%
    n_samples = size(handles.sample_spikes, 1);
    colors = lines(handles.curr_container.n_clusters);
    c_data = zeros(n_samples, 3);
    sample_classes = handles.curr_container.class_no{handles.curr_container.n_clusters}(handles.sample_spikes);
    no_class_color = [0.7, 0.7, 0.7];
    for i = 1:handles.curr_container.n_clusters
        if ~handles.curr_container.valid_class(i)
            colors(i, :) = no_class_color;
        end
    end

    for i = 1:length(sample_classes)
        c_data(i, :) = colors(sample_classes(i), :);
    end

    if handles.plot_spike_means
        for i = 1:handles.curr_container.n_clusters
            handles.spike_mean_handles{i}.Color = colors(i, :);
        end
    else
        for i = 1:length(sample_classes)
            handles.spike_handles{i}.Color = colors(sample_classes(i), :);
        end
    end

    handles.scatter_handle.CData = c_data;

%% ----------------- MISC ---------------- %%

function disp_skip_msg(handles)
    disp([
        'skipping electrode ', ...
        get_well_string( ... 
            handles.electrode_containers(handles.curr_index).spike_index(1), ...
            handles.electrode_containers(handles.curr_index).spike_index(2) ...
        ), ...
        '-', ...
        get_electrode_string( ...
            handles.electrode_containers(handles.curr_index).spike_index(3), ...
            handles.electrode_containers(handles.curr_index).spike_index(4) ...
        ) ...
    ]);


%% -------------- MAIN LOOP -------------- %%

function command = get_command(handles)
%% command = get_command(handles)
%
%  Retrieves the next command from the input prompt
    axes(handles.main_axes);
    [~, ~, command] = ginput(1);

function handles = set_n_clust(handles)
%% handles = set_n_clust(handles)
%
%  Queries the user for the number of clusters to use
    max_clusters = length(handles.curr_container.cluster_model);
    response = inputdlg(['Input the number of clusters (Max:', num2str(max_clusters), ' )']);
    if isempty(response) || isempty(response{1})
        return % return without doing anything if no input is given
    end
    n_clust = uint8(response{1}) - 48;
    if n_clust > 0 && n_clust <= max_clusters
        handles.curr_container.n_clusters = n_clust;
        handles.curr_container.valid_class = true(n_clust, 1);
    else
        disp(['Number of clusters must be between 0 and ', num2str(max_clusters), '!'])
    end

function print_details(handles)
    %% TODO
    disp(handles.curr_container)

function handles = flag_clusters(handles)
    handles.curr_container.valid_class = flag_popup(handles);

function rotate_display(handles)
    axes(handles.main_axes)
    rotate3d()
    pause
    rotate3d()

function handles = next_electrode(handles)
    if handles.curr_index < numel(handles.electrode_containers)
        handles.curr_index = handles.curr_index + 1;
    else
        disp('Wrapping back to first electrode!')
        handles.curr_index = 1;
    end
    if handles.electrode_containers(handles.curr_index).contains_data
        handles = load_curr_container(handles);
    else
        % this will overflow if all of the electrodes are empty
        % fuck the police
        disp_skip_msg(handles);
        handles = next_electrode(handles);
    end

function handles = prev_electrode(handles)
    if handles.curr_index > 1
        handles.curr_index = handles.curr_index - 1;
    else
        disp('Wrapping to last electrode!')
        handles.curr_index = numel(handles.electrode_containers);
    end
    if handles.electrode_containers(handles.curr_index).contains_data
        handles = load_curr_container(handles);
    else
        % this will overflow if all of the electrodes are empty
        % fuck the police
        disp_skip_msg(handles);
        handles = prev_electrode(handles);
    end

function [handles, keep_looping] = prompt_exit(handles)
    %% TODO

function handles = analysis_loop(handles)
    keep_looping = true;
    handles = refresh_display(handles);
    while keep_looping
        command = get_command(handles);
        switch command
            case 'c'
                handles = set_n_clust(handles);
                if handles.plot_spike_means
                    axes(handles.secondary_axes)
                    handles = plot_spike_means(handles);
                end
                handles = refresh_colors(handles);
            case 'd'
                print_details(handles);
            case 'f'
                handles = flag_clusters(handles);
                handles = refresh_colors(handles);
            case 'r'
                rotate_display(handles);
            case 'v'
                handles.plot_spike_means = true;
                axes(handles.secondary_axes);
                handles = plot_spike_means(handles);
                handles = refresh_colors(handles);
            case 't'
                handles.plot_spike_means = false;
                axes(handles.secondary_axes);
                handles = plot_spikes(handles);
                handles = refresh_colors(handles);
            case 'x'
                handles = update_curr_container(handles);
                handles = next_electrode(handles);
                handles = refresh_display(handles);
            case 'z'
                handles = update_curr_container(handles);
                handles = prev_electrode(handles);
                handles = refresh_display(handles);
            case 's'
                handles = update_curr_container(handles);
                save_data(handles)
            case ';'
                [handles, keep_looping] = prompt_exit(handles);
            otherwise
                disp(['Command: "', command, '" not recognized!'])
        end
    end
