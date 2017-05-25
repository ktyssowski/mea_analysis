# mea_analysis
Matlab and Python code for analyzing and visualizing mea data

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
echo 'export PYTHONPATH="/path/to/mea_analysis/pymea:$PYTHONPATH"' >> ~/.bashrc
```
Once you've done that, you should be able to import the pymea module into python after opening a new terminal.

Installing the Matlab code
--------------------------
All of the matlab dependencies required by this package are included with the repo. All you need to do is add them to your path. The easiest way to do this is to use the buttons on the matlab console. Open matlab, and select the "set path" option:
![alt text](https://github.com/sdrendall/mea_analysis/blob/master/tutorial_pictures/click_set_path.png?raw=true "Select Set Path")
Choose the "Add with Subfolders" option:
![alt text](https://github.com/sdrendall/mea_analysis/blob/master/tutorial_pictures/click_add_with_subfolders.png?raw=true "select Add With Subfolders")
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
