#!/Users/pranab/Tools/anaconda/bin/python

# Package imports
import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import sklearn as sk
import matplotlib
import random
import jprops
sys.path.append(os.path.abspath("../lib"))
from util import *
from mlutil import *

class BaseClassifier(object):
	config = None
	def __init__(self, configFile, defValues):
		self.config = Configuration(configFile, defValues)
		
	
	def initConfig(self, configFile, defValues):
		self.config = Configuration(configFile, defValues)
	
	# get config object
	def getConfig(self):
		return self.config
	
	#set config param
	def setConfigParam(self, name, value):
		self.config.setParam(name, value)
	
	#get mode
	def getMode(self):
		return self.config.getStringConfig("common.mode")[0]
		
	#get search parameter
	def getSearchParamStrategy(self):
		return self.config.getStringConfig("train.search.param.strategy")[0]
	
	#auto train	
	def autoTrain(self):
		maxErr = self.config.getFloatConfig("train.auto.max.error")[0]
		maxErrDiff = self.config.getFloatConfig("train.auto.max.error.diff")[0]
		
		#train, validate and serach optimum parameter
		result = self.trainValidateSearch()
		testError = result[1]
			
		#train only with optimum parameter values
		for paramValue in result[0]:
			pName = paramValue[0]
			pValue = paramValue[1]
			print pName + "  " + pValue
			self.setConfigParam(pName, pValue)
		trainError = self.train()
			
		avError = (trainError + testError) / 2
		diffError = testError - trainError
		print "training error %.3f test error: %.3f" %(trainError, testError)
		print "average of test and training error: %.3f test and training error diff: %.3f" %(avError, diffError)  
		if (diffError) > maxErrDiff:
			print "High generalization error. Need larger training data set"
			status = 1
		elif avError > maxErr:
			print "Converged, but with high error rate. Need to increase model complexity"
			status = 2
		else:
			print "succesfully trained"
			status = 0
		return status
			
			
		