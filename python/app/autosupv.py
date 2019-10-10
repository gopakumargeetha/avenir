#!/usr/bin/python

# avenir-python: Machine Learning
# Author: Pranab Ghosh
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License. You may
# obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0 
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.

# Package imports
import os
import sys
import matplotlib.pyplot as plt
from random import randint
from hyperopt import tpe, hp, fmin, Trials
sys.path.append(os.path.abspath("../supv"))
sys.path.append(os.path.abspath("../lib"))
from util import *
from mlutil import *
from rf import *
from svm import *
from gbt import *

def clfEvaluator(args):
	clf = classifiers[args["model"]]
	config = clf.getConfig()
	modelParam = args["param"]
	for paName, paValue in modelParam.items:
		clf.setConfigParam(paName, str(paValue))
		
	return clf.trainValidate()

if __name__ == "__main__":
	# config file for each classifier
	assert len(sys.argv) > 2, "missing classifier name and config files"
	maxEvals = int(sys.argv[1])
	classifiers = dict()
	for i in range(2, len(sys.argv)):
		items = sys.argv[i].split("=")
		clfName = items[0]
		clfConfigFile = items[1]
		if clfName == "rf":
			clf = RandomForest(clfConfigFile)
		elif clfName == "gbt":
			clf = GradientBoostedTrees(clfConfigFile)
		elif clfName == "svm":
			clf = SupportVectorMachine(clfConfigFile)
		else:
			raise valueError("unsupported classifier")
		classifiers[clfName] = clf	

		# create space
		params = list()
		for clName, clf in classifiers.items:
			# search space parameters
			config = clf.getConfig()
			searchParams = config.getStringConfig("train.search.params")[0].split(",")
			assert searchParams, "missing search parameter list"
			searchParamDetals = list()
			for searchParam in searchParams:
				paramItems = searchParam.split(":")
				extSearchParamName = str(paramItems[0])

				#get rid name component search
				paramNameItems = paramItems[0].split(".")
				del paramNameItems[1]
				searchParamName = ".".join(paramNameItems)
				searchParamType = paramItems[1]
				searchParam = (extSearchParamName, searchParamName, searchParamType)
				searchParamDetals.apend(searchParam)

			# param space
			param = dict()
			param["model"] = clName
			modelParam = dict()
			for extSearchParamName, searchParamName, searchParamType in searchParamDetals:
				searchParamValues = config.getStringConfig(extSearchParamName)[0].split(",")	
				if (searchParamType == "string"):
					modelParam[searchParamName] = hp.choice(searchParamName,searchParamValues)
				elif (searchParamType == "int"):
					assert len(searchParamValues) == 2, "only 2 values needed for parameter range space"
					iSearchParamValues = list(map(lambda v: int(v), searchParamValues))	
					modelParam[searchParamName] = hp.choice(searchParamName,range(iSearchParamValues[0], iSearchParamValues[1]))
				elif (searchParamType == "float"):
					assert len(searchParamValues) == 2, "only 2 values needed for parameter range space"
					fSearchParamValues = list(map(lambda v: float(v), searchParamValues))	
					modelParam[searchParamName] = hp.uniform(searchParamName, fSearchParamValues[0],fSearchParamValues[1])
				else:
					raise ValueError("invalid paramter type")
			param["param"] = modelParam
			params.append(param)


		# optimize
		space = hp.choice("classifier", params)
		trials = Trials()
		best = fmin(clfEvaluator,space, algo=tpe.suggest, trials=trials,max_evals=maxEvals)
		print best

		