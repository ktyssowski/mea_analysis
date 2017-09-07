# mea_analysis
Matlab and Python code for analyzing and visualizing mea data

1.[Installing](#downloading-and-installing-the-code)
  * [Pymea](#installing-the-pymea-module)
  * [Matlab](#installing-the-matlab-code)
  * [Installing on Orchestra](#installing-the-matlab-code-on-orchestra)
  
2.[Spike Sorting](#spike-sorting)

3.[Data Visualization](#visualizing-cluster-data)
  * [Exporting Matlab Data to CSV Format](#generating-spike-frequency-traces)
  * [Plotting Data With Python](#pymea)

Downloading and Installing the Code
===================================

You can download this code using git. Open a terminal, navigate to a directory of your chosing and run the following command:
```
git clone https://github.com/sdrendall/mea_analysis
```
This will create a `mea_analysis` directory in your current directory that contains the latest version of the code. To update to the most recent version of the codebase, run the following from within the `mea_analysis` directory:
```
git pull origin master
```

Installing the pymea module
---------------------------
Code for generating plots using python, pandas, matplotlib and seaborn is included in the pymea module. Using this module requires several dependencies. I recommend using the [Anaconda](https://www.continuum.io/downloads) python distribution, which includes a curated list of commonly used scientific python packages. If you don't want to use anaconda, you can download the rest of the dependencies with `pip`:
```
pip install matplotlib numpy scipy pandas seaborn
```

Once you have all of the dependencies installed, you have to add the pymea directory to your `PYTHONPATH`. To do this, you can run the following command:
```
export PYTHONPATH="/path/to/mea_analysis/pymea:$PYTHONPATH"
```
This has to be done each time you open up a new terminal. However, you can have the command run automatically by adding it to your `bashrc` like this:
```
echo 'export PYTHONPATH="/path/to/mea_analysis:$PYTHONPATH"' >> ~/.bashrc (use ~/.bash_profile for Mac OSX)
```
Once you've done that, you should be able to import the pymea module into python after opening a new terminal.

Installing the Matlab code
--------------------------
All of the matlab dependencies required by this package are included with the repo. All you need to do is add them to your path. The easiest way to do this is to use the buttons on the matlab console. Open matlab, and select the "set path" option:
![alt text](https://github.com/sdrendall/mea_analysis/blob/master/tutorial_pictures/click_set_path.png?raw=true "Select Set Path")
Choose the "Add with Subfolders" option:
![alt text](https://github.com/sdrendall/mea_analysis/blob/master/tutorial_pictures/click_add_with_sub_folders.png?raw=true "select Add With Subfolders")
Navigate to and select the `matlab` folder within the `mea_analysis` directory:
![alt text](https://github.com/sdrendall/mea_analysis/blob/master/tutorial_pictures/select_matlab_folder.png?raw=true "Select the Matlab Folder")
Click "save" to save the changes to your Matlab path:
![alt text](https://github.com/sdrendall/mea_analysis/blob/master/tutorial_pictures/click_save.png?raw=true "Click Save")
And you're done! You should be able to run the matlab code in this repo if you followed the instructions correctly!

Installing the Matlab code on Orchestra
---------------------------------------
You can follow the above instructions to install the code on Orchestra. However, to view the Matlab GUI, you need to use X11 forwarding on an interactive node. If you're running Linux, you're all set! On a mac, you'll need [XQuartz](https://www.xquartz.org/), if you're running windows, take a moment to reconsider your life's decisions, then download [XMing](https://sourceforge.net/projects/xming/). Next, all you have to do is use the `-X` modifier when initially connecting to Orchestra, then submit an interactive job to the interactive queue:
```
ssh -X sr235@orchestra.med.harvard.edu
```
Once you're logged on...
```
bsub -q interactive -Is bash
matlab
```
You should see the matlab splash followed by the matlab GUI.

Spike Sorting
=============
Spike sorting consists of two stages, an automated preprocessing step involving feature extraction and clustering, and a manual review step where features and clusters are visualized and the number of clusters is specified. The entire process is carried out in Matlab.

Preprocessing
-------------
Preprocessing is carried out by the `process_spk_files.m` matlab function. The function can be called from matlab by specifying a cell array containing the paths to the .spk files in a recording as the first argument, and the desired output .mat file path as the second argument:
```
process_spk_files({'/path/to/spk_file_1.spk', '/path/to/spk_file_2.spk'}, '/path/to/output_file.mat'}
```

It is usually inconvenient to do this from the matlab command line however, so I created a script - `processing_launcher.sh` - that can be used to construct this matlab command, and launch the matlab engine with this command as input. This script simply takes in a bash array of spk files. It can be called like this:
```
/path/to/processing_launcher.sh /path/to/spk_file_1.spk /path/to/spk_file_2.spk
```

or if you have a large number of spike files in a directory, it is convenient to use a `find` command to automatically locate all of the .spk files in a directory like this:
```
/path/to/processing_launcher.sh $(find /path/to/spk_file_directory -name '*.spk')
```

Initiating preprocessing using `processing_launcher.sh` will automatically name the output file after the first .spk file specified as an input, with the '.spk' suffix replaced with '.mat'.

Preprocessing can take a very long time, and a lot of memory for input files containing a large number of spikes, so I recommend running it on orchestra.

How It Works
------------
The spikes on each electrode are clustered based on their first three principal components using Gaussian mixture models. For each electrode, data is attempted to be clustered using up to five clusters. If clustering fails before five clusterings are generated, then clustering is aborted 

Manual Cluster Numbering
------------------------
After preprocessing completes, results can be visualized and the number of clusters can be determined using a matlab GUI: `spike_analyzer.m`. To use the gui, simply enter the command on the matlab command line:
```
spike_analyzer
```

A prompt should appear instructing you to select the .mat file generated by preprocessing. After you have selected the correct .mat file, a second prompt will appear asking you to select all of the .spk files. Hold shift or ctrl to select all of the files simultaneously, then click 'open'. A GUI will appear displaying the waveforms in 3D feature space, as well as the average waveform for each cluster. A list of commands is in the lower left-hand side of the user-interface. To specify the number of clusters, press a number 1-5. Press 'x' to move to the next electrode. Individual traces can be visualized by selecting the 't' option. However, when in trace mode, data must be loaded from .spk files for each electrode, which is very slow. I reccomend staying in average trace mode ('v') and only using individual traces when absolutely necessary.

Visualizing Cluster Data
========================
Clustered data is located in the .mat file output by `process_spk_files.m`. The data contained there can be loaded into matlab with the load command:
```
load /path/to/processing_output_file.mat
```

This will create three variables in your matlab environment. `recording_start_time` is a matlab `datetime` object corresponding to the date and time of the recording start time for the earliest .spk file. `final_spike_time` is a `datetime` object corresponding to the date and time of the final spike in the given .spk files. This is used as a proxy for the recording's end time, since that is not stored in any of Axis' output files. `electrode_containers` is an [num_well_rows, num_well_cols, num_electrode_cols, num_electrode_rows] array of`ElectrodeContainer` objects that store preprocessing data. Each `ElectrodeContainer` stores data for a single maestro electrode. See `ElectrodeContainer.m` or type `help ElectrodeContainer` into the Matlab command prompt for a description of the data contained in each `ElectrodeContainer`.

Generating Spike Frequency Traces
---------------------------------
Although data can be loaded from .mat files and plotted, I have written matlab functions for converting the data into a more manageable form. `generate_spike_frequency_table.m` generates spike frequency timecourses from the data in a given .mat file, and outputs a .csv file containing the frequency timecourses and a time axis. You can use this function like this:
```
generate_spike_frequency_table('/path/to/input_file.mat', '/path/to/output_file.csv')
```
Spike frequencies are output in units of spikes/time bin. An optional `bin_size` parameter can be specified to set the size of time bins in seconds. By default, spikes are binned into 300 second (5 min) time bins. For example, you can set the time bins to be one minute long like this:
```
generate_spike_frequency_table('/path/to/input_file.mat', '/path/to/output_file.csv', 'bin_size', 60)
```

Pymea
-----
I wrote a python module that can be used to quickly create some commonly used plots. A jupyter notebook containing a tutorial for the most useful features is [here](https://github.com/sdrendall/mea_analysis/blob/master/jupyter_notebooks/Pymea%20Tutorial.ipynb). \
\
Here is an index of what's in the module:
### matlab_compatibility.py
`datetime_str_to_datetime` - This converts the strings generated when matlab datetimes are written to a table to python datetime objects\
`well_row_letter_to_number` - Converts the letter corresponding to the Axis well row to the corresponding integer row number. Starts with A = 1\
`get_row_number` - Returns the row_number corresponding to the row_number of the unit specified by unit_name. Useful for filtering rows by condition.\
`get_col_number` - Returns the col_number tuple corresponding to the column of the unit specified by unit_name. Useful for filtering rows/columns by condition.\
`get_row_col_number_tuple` - Returns the (row_number, col_number) tuple corresponding to the row_number and column of the unit specified by unit_name. Useful for filtering rows/columns by condition.\

### plotting.py
`smooth` - Applies a moving average to an array. Useful for smoothing spike frequency traces\
`plot_unit_traces` - Plots spike frequency unit traces for each unit in a provided category dataframe\
`plot_unit_frequency_distributions` - Plots the distribution of mean frequencies for units in each condition in a supplied category dataframe\
`plot_mean_frequency_traces` - Plots the mean frequency trace for each condition in the given category dataframe\
`construct_categorized_dataframe` - Creates a dataframe that includes category information for unit spike timecourses. See [this tutorial](https://github.com/sdrendall/mea_analysis/blob/master/jupyter_notebooks/Pymea%20Tutorial.ipynb), or [this python notebook](https://github.com/sdrendall/mea_analysis/blob/master/jupyter_notebooks/002%20Drug%20Analysis.ipynb) for examples of how you can use this function\
`smooth_categorized_dataframe_unit_traces` - Smooths the spike frequency traces for each unit in the given category dataframe using the `smooth` function\

### spikelists.py
Spikelists includes functions used for plotting data from the spike_list csv files generated by AxIS. I would use the analysis pipeline described above instead of these functions, but they are worth a look if you need to quickly make plots. Look at the help text for the `generate_lineplots.py` script in `mea_analysis/python`.

