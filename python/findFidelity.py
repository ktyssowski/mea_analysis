#!/usr/bin/env python

import sys
import csv
import matplotlib.pyplot as plt 
import numpy as np
import argparse

dictElectrodes = {"A1_11":1, "A1_12":2,"A1_13":3, "A1_14":4, "A1_15":5, "A1_16":6, "A1_17":7, "A1_18":8, "A1_21":9, "A1_22":10, "A1_23":11, "A1_24":12, "A1_25":13, "A1_26":14, "A1_27":15, "A1_28":16, "A1_31":17, "A1_32":18, "A1_33":19, "A1_34":20, "A1_35":21, "A1_36":22, "A1_37":23, "A1_38":24, "A1_41":25, "A1_42":26, "A1_43":27, "A1_44":28, "A1_45":29, "A1_46":30, "A1_47":31, "A1_48":32, "A1_51":33, "A1_52":34, "A1_53":35, "A1_54":36, "A1_55":37, "A1_56":38, "A1_57":39, "A1_58":40, "A1_61":41, "A1_62":42, "A1_63":43, "A1_64":44, "A1_65":45, "A1_66":46, "A1_67":47, "A1_68":48, "A1_71":49, "A1_72":50, "A1_73":51, "A1_74":52, "A1_75":53, "A1_76":54, "A1_77":55, "A1_78":56, "A1_81":57, "A1_82":58, "A1_83":59, "A1_84":60, "A1_85":61, "A1_86":62, "A1_87":63, "A1_88":64}


def readRightData(file, exptLen, x):
# Creates an array of the number of spikes per preset period (if x = 1, period is 1", if x = 100, period is 100ms etc.)
	lastTime = 0
	timeElectrodes =  {}
	a = np.zeros((exptLen * x, 64), dtype = np.float16) #create an empty array of the right size
	for line in csv.reader(file, csv.excel):
		if line[0] == 'Investigator': #ignore the header
			continue
		else:
			wantedLine = line[2:]
			electrode = dictElectrodes[wantedLine[1]]
			time = int(float(wantedLine[0]) * x)
			if time > (exptLen * x): #stop at the right time
				break
			if time == lastTime: #creates a dictionary of the number of spikes for each electrode in the period of interest
				if electrode in timeElectrodes.keys():
					timeElectrodes[electrode] += 1
				else:
					timeElectrodes[electrode] = 1
			else:
				for key in timeElectrodes.keys():
					a[lastTime, key -1] = timeElectrodes[key] #updates the array
				i = 1
				timeElectrodes = {electrode : i}
				lastTime = time
				lastI = i

	np.savetxt('test.txt', a, fmt='%.4f')
	return a



def setupParameters(blockSize, blockNumber, x):
#Creates a list of the times (in ms) when the blocks change--only works if all blocks are
#same length!
	blockSize = int(blockSize) * x
	blockNumber = int(blockNumber)
	variables = []
	k = 0
	while k <  blockNumber + 1:
		value = 0 + (blockSize * k)
		variables.append(value)
		k += 1
	return variables



def findLightStart(data, period, x, variables):
# With the period given, finds the time when the light is most likely to be flashing
# i.e. the times lining up with the period with the most spikes--returns a dictionary of blocks and start times
	lightStart = {}
	for i in range(0, len(variables)):
		if variables[i] == 0:
			continue
		else:
			e = 0
			block = data[variables[i-1]:variables[i]]
			totalSpikes = np.sum(block, axis = 1) #sums the spikes in all the channels for each time window
			sumList = []
			while e < (x*period):
				sumList.append(sum(totalSpikes[e:len(totalSpikes):(x*period)])) #for all periods of the length given, sums together the number of spikes
				#at the beginning of those periods (i.e. when the light should be on)--essentially gives a list showing how much spiking is at the beginning of the
				#period in all possible arrangements
				e+=1
			indexM = sumList.index(max(sumList)) # find the way to arrage the periods so that they have a lot of spikes at the beginning
			lightStart[i] = indexM
	return lightStart


def findFidelity(data, lightStart, x, period, variables):
	#using the function above to infer when the light is on, finds spike fidelity
	spikingElectrodes = 0
	for column in data.T:
		if sum(column) != 0:
			spikingElectrodes += 1 #shows how many electrodes are actually spiking at any time
	for i in range(0, len(variables)):
		if variables[i] == 0:
			continue
		else:
			block = data[variables[i-1]:variables[i]]
			spikeOpportunities = (block.shape[0] - lightStart[i])/ (period * x) * spikingElectrodes # number of times light is on * number of spiking electrodes
			singlesPerBlock = 0
			for r in range(lightStart[i], (block.shape[0]), int((period * x))): #counts only the spikes in the time period at the beginning of the relevant period
				singlesPerElectrode = 0
				for e in block[r,]:
					if e != 0: #make sure to count only one spike even if there is a doublet (or more)
						singlesPerElectrode += 1
				singlesPerBlock += singlesPerElectrode
			fidelity = float(singlesPerBlock)/spikeOpportunities
			print "Block " + str(i)+ " fidelity: " + str(fidelity)

#Parse arguments
argp = argparse.ArgumentParser(prog = "findFidelity.py", description = "Takes the .csv file containing spike times and aplitudes and calculates spike fidelities for each defined block of time. Blocks should all be the same length.")
argp.add_argument("-f", dest = "freq", type = float, metavar = "0.5", default = 0.5, help = "Sets expected frequency of light pulses, same for every block")
argp.add_argument("-w", dest = "x", type = int, metavar = "10", default = 10, help = "Sets the size of the window that will be used (should be seconds/x i.e. if 1, window is 1s, if 1000 it is 1 ms)")
argp.add_argument("-l", dest = "blockSize", type = int, metavar = "120", required = True, help = "Indicates the length of the block in the experiment in seconds")
argp.add_argument("-n", dest = "blockNumber", type = int, metavar = "10", required = True, help = "Indicates the number of blocks in the experiment")









if __name__ == "__main__":

	args = argp.parse_args()

	exptLen = args.blockSize * args.blockNumber

	period = 1/float(args.freq)

	data = readRightData(sys.stdin, exptLen, args.x)
	variables = setupParameters(args.blockSize, args.blockNumber, args.x)
	findFidelity(data, findLightStart(data, period, args.x, variables), period, args.x, variables)



