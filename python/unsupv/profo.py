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
from datetime import datetime
from dateutil.parser import parse
import pandas as pd
import numpy as np
from fbprophet import Prophet
sys.path.append(os.path.abspath("../lib"))
from util import *
from mlutil import *


# gradient boosting classification
class ProphetForcaster(object):
	def __init__(self, configFile, changepoints, holidays):
		defValues = {}
		defValues["common.mode"] = ("training", None)
		defValues["common.model.directory"] = ("model", None)
		defValues["common.model.file"] = (None, None)
		defValues["common.verbose"] = (False, None)
		defValues["train.data.file"] = (None, "missing training data file")
		defValues["train.data.fields"] = (None, "missing training data field ordinals")
		defValues["train.data.exist.dateformat"] = (None, None)
		defValues["train.data.new.dateformat"] = (None, None)
		defValues["train.growth"] = ("linear" , None)
		defValues["train.changepoints"] = (None , None)
		defValues["train.num.changepoints"] = (25 , None)
		defValues["train.changepoint.range"] = (0.8 , None)
		defValues["train.yearly.seasonality"] = ("auto" , None)
		defValues["train.weekly.seasonality"] = ("auto" , None)
		defValues["train.daily.seasonality"] = ("auto" , None)
		defValues["train.holidays"] = (None , None)
		defValues["train.seasonality.mode"] = ("additive" , None)
		defValues["train.seasonality.prior.scale"] = (10.0 , None)
		defValues["train.holidays.prior.scale"] = (10.0 , None)
		defValues["train.changepoint.prior.scale"] = (0.05 , None)
		defValues["train.mcmc.samples"] = (0 , None)
		defValues["train.interval.width"] = (0.80 , None)
		defValues["train.uncertainty.samples"] = (1000 , None)
		defValues["forecast.window"] = (None, "missing forecast window size")
		defValues["forecast.unit"] = (None, "missing forecast window type")
		defValues["forecast.include.history"] = (False, None)

		self.config = Configuration(configFile, defValues)
		self.verbose = self.config.getBooleanConfig("common.verbose")[0]
		self.changepoints = changepoints
		self.holidays = holidays
		self.model = None

	# train model	
	def train(self):
		#build model
		self.buildModel()
		
		dataFile = self.config.getStringConfig("train.data.file")[0]
		fieldIndices = self.config.getStringConfig("train.data.fields")[0]
		if fieldIndices:
			fieldIndices = strToIntArray(fieldIndices, ",")
		#data = np.loadtxt(dataFile, delimiter=",", usecols=fieldIndices)

		#conver to extpected df and fit model
		exFormat = self.config.getStringConfig("train.data.exist.dateformat")[0]
		neededFormat = self.config.getStringConfig("train.data.new.dateformat")[0]
		if exFormat:
			pass

		df = pd.read_csv(dataFile, header=None, usecols=fieldIndices, names=["ds", "y"])
		df["ds"] = pd.to_datetime(df["ds"],format=neededFormat) 
		df.sel_index("ds", inplace=True)

		self.model.fit(df)

		modelSave = self.config.getBooleanConfig("train.model.save")[0]
		if modelSave:
			self.saveModel()

	# forecast
	def forecast(self):
		self.getModel()
		window = self.config.getIntConfig("forecast.window")[0]
		unit = self.config.getStringConfig("forecast.unit")[0]
		history = self.config.getBooleanConfig("forecast.include.history")[0]
		future = self.model.make_future_dataframe(window, freq=unit, include_history=history)
		forecast = self.model.predict(future)
		return forecast		

	# get model file path
	def getModelFilePath(self):
		modelDirectory = self.config.getStringConfig("common.model.directory")[0]
		modelFile = self.config.getStringConfig("common.model.file")[0]
		if modelFile is None:
			raise ValueError("missing model file name")
		modelFilePath = modelDirectory + "/" + modelFile
		return modelFilePath
	
	# save model
	def saveModel(self):
		modelSave = self.config.getBooleanConfig("train.model.save")[0]
		if modelSave:
			print "...saving model"
			modelFilePath = self.getModelFilePath()
			joblib.dump(self.model, modelFilePath) 
	
	# gets model
	def getModel(self):
		useSavedModel = self.config.getBooleanConfig("forecast.use.saved.model")[0]
		if self.model is None:
			if useSavedModel:
				# load saved model
				print "...loading model"
				modelFilePath = self.getModelFilePath()
				self.model = joblib.load(modelFilePath)
			else:
				# train model
				self.train()

	# builds model object
	def buildModel(self):
		growth = self.config.getStringConfig("train.growth")[0]
		changepoints = self.changepoints
		numChangepoints = self.config.getIntConfig("train.num.changepoints")[0]
		changepointRange = self.config.getFloatConfig("train.changepoint.range")[0]
		yearlySeasonality = typedValue(self.config.getStringConfig("train.yearly.seasonality")[0])
		weeklySeasonality = typedValue(self.config.getStringConfig("train.weekly.seasonality")[0])
		dailySeasonality = typedValue(self.config.getStringConfig("train.daily.seasonality")[0])
		holidays = self.holidays
		seasonalityMode = self.config.getStringConfig("train.seasonality.mode")[0]
		seasonalityPriorScale = self.config.getFloatConfig("train.seasonality.prior.scale")[0]
		holidaysPriorScale = self.config.getFloatConfig("train.holidays.prior.scale")[0]
		changepointPriorScale = self.config.getFloatConfig("train.changepoint.prior.scale")[0]
		mcmcSamples = self.config.getIntConfig("train.mcmc.samples")[0]
		intervalWidth = self.config.getFloatConfig("train.interval.width")[0]
		UncertaintySamples = self.config.getIntConfig("train.uncertainty.samples")[0]

		self.model = Prophet(growth=growth, changepoints=changepoints, n_changepoints=numChangepoints,\
			changepoint_range=changepointRange, yearly_seasonality=yearlySeasonality, weekly_seasonality=weeklySeasonality,\
			daily_seasonality=dailySeasonality, holidays=holidays, seasonality_mode=seasonalityMode,\
 			seasonality_prior_scale=seasonalityPriorScale, holidays_prior_scale=holidaysPriorScale,\
			changepoint_prior_scale=changepointPriorScale,mcmc_samples=mcmcSamples,interval_width=intervalWidth,\
			Uncertainty_samples=UncertaintySamples)



