#!/usr/bin/env python

import sys
import csv
import matplotlib.pyplot as plt 
import numpy as np
import argparse

dictElectrodes = {"A1_11":1, "A1_12":2,"A1_13":3, "A1_14":4, "A1_15":5, "A1_16":6, "A1_17":7, "A1_18":8, "A1_21":9, "A1_22":10, "A1_23":11, "A1_24":12, "A1_25":13, "A1_26":14, "A1_27":15, "A1_28":16, "A1_31":17, "A1_32":18, "A1_33":19, "A1_34":20, "A1_35":21, "A1_36":22, "A1_37":23, "A1_38":24, "A1_41":25, "A1_42":26, "A1_43":27, "A1_44":28, "A1_45":29, "A1_46":30, "A1_47":31, "A1_48":32, "A1_51":33, "A1_52":34, "A1_53":35, "A1_54":36, "A1_55":37, "A1_56":38, "A1_57":39, "A1_58":40, "A1_61":41, "A1_62":42, "A1_63":43, "A1_64":44, "A1_65":45, "A1_66":46, "A1_67":47, "A1_68":48, "A1_71":49, "A1_72":50, "A1_73":51, "A1_74":52, "A1_75":53, "A1_76":54, "A1_77":55, "A1_78":56, "A1_81":57, "A1_82":58, "A1_83":59, "A1_84":60, "A1_85":61, "A1_86":62, "A1_87":63, "A1_88":64}


def readRightData(file, exptLen, x, lsExcluded, figureName, ampEx):
	'''
	Creates an array of the number of spikes per preset period (if x = 1, period is 1", if x = 100, period is 100ms etc.)
	In: file, length of experiment (total length of file), x to set the window, list of exculuded channels, name for the file, max amplitude
	Out: Array of channels by times showing number of spikes at (channel, time)
	'''
	lastTime = 0
	timeElectrodes =  {}
	a = np.zeros(((exptLen * x), 64), dtype = np.float16) #create an empty array of the right size
	for line in csv.reader(file, csv.excel):
		if line[0] == 'Investigator': #ignore the header
			continue
		else:
			wantedLine = line[2:]
			electrode = dictElectrodes[wantedLine[1]]
			amp = wantedLine[2]
			time = int(float(wantedLine[0]) * x)
			if time > (exptLen * x): #stop at the right time
				break
			if time == lastTime: #creates a dictionary of the number of spikes for each electrode in the period of interest
				if electrode not in lsExcluded and float(amp) < ampEx: #filters out exluded electrodes
					if electrode in timeElectrodes.keys():
						timeElectrodes[electrode] += 1
					else:
						timeElectrodes[electrode] = 1
				else:
					continue
			else:
				for key in timeElectrodes.keys():
					a[lastTime, key-1] = timeElectrodes[key] #updates the array
				if electrode not in lsExcluded and float(amp) < ampEx: #have to make sure we exclude this again
					i = 1
					timeElectrodes = {electrode : i}
					lastTime = time
					lastI = i
				else:
					continue
	if args.printMatrix == "Y":			
		np.savetxt(figureName + '.txt', a, fmt='%.4f')
	return a
	


def setupParameters(x, blockSize = 120, blockNumber = 0, startTime = None, stopTime = None):
	'''	
	Creates a list of the times (in ms) when the blocks change (only works if all blocks are same length!)
	OR sets the start/stop time if only one plot will be made
	In: window size, block size and number OR start and stop times
	Out: List of times when blocks will start and stop
	'''
	if blockNumber >= 1:
		blockSize = blockSize * x
		variables = []
		k = 0
		while k <  blockNumber + 1:
			value = 0 + (blockSize * k)
			variables.append(value)
			k += 1
		return variables
	if startTime >= 0:
		variables = []
		variables.append(startTime * x)
		variables.append(stopTime * x)
		return variables




def makeHeatMap(data, variables, x, blockSize, figureName):
	'''
	Makes a heat map for each block set up in setupParameters
	'''
	for i in range(0, len(variables)):
		if i == 0:
			continue
		else:
			trData = np.transpose(data[variables[i-1]:variables[i]])
			plt.pcolor(trData, cmap = plt.cm.gist_ncar, vmin = 0, vmax = 5)
			plt.colorbar()
			plt.title(str(figureName))
			plt.axis([0, blockSize * x, 0, trData.shape[0]])
			plt.ylabel("Electrode", fontsize = 10)
			plt.xlabel("Time(s/" + str(x) + ")", fontsize = 10)
			plt.savefig(figureName + '_' + str(i) + '.png', dpi = 300)
			plt.clf()


argp = argparse.ArgumentParser(prog = "MEAspikeAmp.py", description = "Takes the .csv file containing spike times and aplitudes and makes heat maps")
argp.add_argument("-w", dest = "x", type = int, metavar = "10", default = 10, help = "Sets the size of the window that will be used (should be seconds/x i.e. if 1, window is 1s, if 1000 it is 1 ms)")
argp.add_argument("-l", dest = "blockSize", type = int, metavar = "120", help = "Indicates the length of the block in the experiment in seconds MUST HAVE THIS AND NUMBER OR START/STOP")
argp.add_argument("-n", dest = "blockNumber", type = int, metavar = "10", help = "Indicates the number of blocks in the experiment MUST HAVE THIS AND SIZE OR START/STOP")
argp.add_argument("-fn", dest = "figureName", type = str, metavar = "figname", help = "Use to name the figures as you want--will output figures that are named with this name and a number for the block number")
argp.add_argument("-p", dest = "printMatrix", type = str, choices = ["Y", "N"], default = "N", help = "If 'Y', will print the matrix used to make the heatmap.")
argp.add_argument("-st", dest = "startTime", type = int, help = "Use to indicate start time if you only want to make a heat map for a portion of the experiment MUST HAVE THIS AND STOP OR BLOCKSIZE/NUMBER")
argp.add_argument("-sp", dest = "stopTime", type = int, help = "Use to indicate start time if you only want to make a heat map for a portion of the experiment MUST HAVE THIS AND START OR BLOCKSIZE/NUMBER")
argp.add_argument("-e", dest = "exptLen", type = int, metavar = "1200", required = True, help = "Sets the length of the experiment in seconds")
argp.add_argument("-ex", dest = "lsExcluded", type = int, nargs = '+', metavar = "52 23 40", default = [], help = "Input a list of excluded channels (using their numbers NOT their A1_# names)")
argp.add_argument("-aex", dest = "ampEx", type = float, metavar = ".2", default = 0.2, help = "Exclude amplitudes over this value")


def main():

	figureName = args.figureName 

	exptLen = args.exptLen

	"""

	if args.blockNumber >= 1:
		exptLen = args.blockSize * args.blockNumber
	if args.startTime >= 0:
		exptLen = args.stopTime - args.startTime + 10
		"""



	data = readRightData(sys.stdin, exptLen, args.x, args.lsExcluded, args.figureName, args.ampEx)

	if args.blockNumber >= 1:
		variables = setupParameters(args.x, blockSize = args.blockSize, blockNumber = args.blockNumber)
		blockSize = args.blockSize
		
	if args.startTime >= 0:
		variables = setupParameters(args.x, startTime = args.startTime, stopTime = args.stopTime)
		blockSize = args.stopTime - args.startTime
		

	print "plotting..."

	makeHeatMap(data, variables, args.x, blockSize, args.figureName)




if __name__ == "__main__":
	args = argp.parse_args()
	main()

	









