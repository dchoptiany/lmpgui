# MIT License
# 
# Copyright (c) 2020 Damian Choptiany
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import ac
import acsys
import platform
import os
import configparser

if platform.architecture()[0] == "64bit":
	sysdir = os.path.dirname(__file__)+'/stdlib64'
else:
	sysdir = os.path.dirname(__file__)+'/stdlib'

sys.path.insert(0, sysdir)
os.environ['PATH'] = os.environ['PATH'] + ";."

from lmpgui_lib.sim_info import info

configPath = "apps/python/LmpGUI/settings.ini"
config = configparser.ConfigParser()
config.read(configPath)

appWindow = 0
label_laptime = 0
label_delta = 0
label_speed = 0
label_gear = 0
label_fuel = 0
label_tc = 0
label_abs = 0
label_brakeBias = 0
label_ERScurrent = 0
label_deploy = 0
label_estimatedLaps = 0

texture_checkeredFlag = 0

fuelAmount = 0
fuelAmountStart = 0
totalFuelBurnt = 0

maxRPM = 0
hasERSorKERS = 0

spinner_scale = 0
button_indicators = 0
button_speedInMPH = 0
button_settingsVisible = 0

settingsVisible = 0

scale = 1
scaleUpdate = False
indicatorsON = True
speedInMPH = False

indicatorsCoordinates = [(), (), (), ()]

lastLapCount = -1
lapCount = 0
lapsNotInPitCount = 0
wasInPit = 0

flagType = 0

timerFlag = 0
timer60perSecond = 0
timer10perSecond = 0
timer1perSecond = 0

def loadSettings():
	global config, scale, indicatorsON, speedInMPH

	scale = config.getfloat("LMPGUI", "scale")
	indicatorsON = config.getboolean("LMPGUI", "indicatorsON")
	speedInMPH = config.getboolean("LMPGUI", "speedInMPH")

def saveSettings():
	global config, scale, indicatorsON

	config.set("LMPGUI", "scale", str(scale))
	config.set("LMPGUI", "indicatorsON", str(indicatorsON))
	config.set("LMPGUI", "speedInMPH", str(speedInMPH))

	with open(configPath, "w") as configFile:
	    config.write(configFile)

def calculateEstimatedLaps():
	global totalFuelBurnt, fuelAmountStart, fuelAmount, lapsNotInPitCount
    
	currentLapProgress = ac.getCarState(0, acsys.CS.NormalizedSplinePosition)
	totalDistance = lapsNotInPitCount + currentLapProgress
	fuelPerLap = (totalFuelBurnt + (fuelAmountStart - fuelAmount)) / totalDistance

	return fuelAmount / fuelPerLap

def calculateDeploy():
	currentKERS = info.physics.kersCurrentKJ * 1000
	maxKERS = ac.getCarState(0, acsys.CS.ERSMaxJ)
	return  currentKERS * 100 / maxKERS

def formatTime(milliseconds):
	seconds = int(milliseconds / 1000)
	milliseconds -= seconds * 1000

	minutes = int(seconds / 60)
	seconds -= minutes * 60

	return "{}:{:02d}:{:03d}".format(minutes, seconds, milliseconds)

def formatGear(gear):
	if gear == 0:
		return "R"
	if gear == 1:
		return "N"
	return str(gear - 1)

def formatSwitchFromBool(switchState):
	return "ON" if switchState else "OFF"

def getSpeed():
	global speedInMPH

	return ac.getCarState(0, acsys.CS.SpeedMPH) if speedInMPH else ac.getCarState(0, acsys.CS.SpeedKMH)

def drawRPMLights():
	global scale, maxRPM

	numberOfLights = int(ac.getCarState(0, acsys.CS.RPM) * 12 / maxRPM)

	for i in range(numberOfLights):
		if i < 6:
			ac.glColor4f(0, 1, 0, 1)
		elif i < 9:
			ac.glColor4f(1, 1, 0, 1)
		else:
			ac.glColor4f(1, 0, 0, 1)

		ac.glQuad((15 + i * 38.5) * scale, 13 * scale, 36 * scale, 62 * scale)

def drawFlag():
	global scale, flagType, timerFlag, texture_checkeredFlag

	if flagType == 0: #no flag
		return

	if flagType < 5 and timerFlag < 1:
		if flagType == 1: #blue flag
			ac.glColor4f(0, 0, 1, 1)
		elif flagType == 2: #yellow flag
			ac.glColor4f(1, 1, 0, 1)
		elif flagType == 3: #black flag
			ac.glColor4f(0, 0, 0, 1)
		elif flagType == 4: #white flag
			ac.glColor4f(1, 1, 1, 1)

		ac.glQuad(-20 * scale, 0, 20 * scale, 383 * scale)
		ac.glQuad(503 * scale, 0, 20 * scale, 383 * scale)
	elif flagType == 5: #checkered flag
		ac.glColor4f(1, 1, 1, 1)
		ac.glQuadTextured(-20 * scale, 0, 20 * scale, 383 * scale, texture_checkeredFlag)
		ac.glQuadTextured(503 * scale, 0, 20 * scale, 383 * scale, texture_checkeredFlag)
	elif flagType == 6: #penalty flag
		if timerFlag < 1:
			ac.glColor4f(0, 0, 0, 1)
			ac.glQuad(-20 * scale, 0, 20 * scale, 383 * scale)
			ac.glColor4f(1, 1, 1, 1)
			ac.glQuad(503 * scale, 0, 20 * scale, 383 * scale)
		else:
			ac.glColor4f(1, 1, 1, 1)
			ac.glQuad(0, 0, 20 * scale, 383 * scale)
			ac.glColor4f(0, 0, 0, 1)
			ac.glQuad(503 * scale, 0, 20 * scale, 383 * scale)

def drawTyresIndicators():
	global scale, indicatorsCoordinates, indicatorsON

	if not indicatorsON:
		return

	wheelSlip = info.physics.wheelSlip

	for wheelIndex in range(4):
		x, y = indicatorsCoordinates[wheelIndex]

		if wheelSlip[wheelIndex] < 1:
			continue
		elif wheelSlip[wheelIndex] < 20: #tyre spin
			if wheelSlip[wheelIndex] < 2:
				numberOfLights = 1
			elif wheelSlip[wheelIndex] < 3:
				numberOfLights = 2
			else:
				numberOfLights = 3

			ac.glColor4f(0, 0, 1, 1)

			if wheelIndex % 2 == 0: #left wheels
				for n in range(numberOfLights):
					ac.glQuad(x + n * 75 * scale, y, 75 * scale, 15 * scale)
			else: #right wheels
				for n in range(numberOfLights):
					ac.glQuad(503 * scale - (n + 1) * 75 * scale, y, 75 * scale, 15 * scale)

		else: #tyre lock
			ac.glColor4f(1, 0, 0, 1)
			ac.glQuad(x, y, 225 * scale, 15 * scale)

def updateScale():
	global appWindow, label_laptime, label_delta, label_speed, label_gear, label_fuel, label_tc, label_abs
	global label_brakeBias, label_ERScurrent, label_deploy, label_estimatedLaps
	global spinner_scale, scale, scaleUpdate, button_settingsVisible, button_speedInMPH, button_indicators, indicatorsCoordinates

	if not scaleUpdate:
		return

	scaleUpdate = False

	ac.setSize(appWindow, 503 * scale, 383 * scale)
	
	ac.setPosition(label_laptime, 239 * scale, 86 * scale)
	ac.setFontSize(label_laptime, 40 * scale)

	ac.setPosition(label_delta, 239 * scale, 155 * scale)
	ac.setFontSize(label_delta, 40 * scale)

	ac.setPosition(label_speed, 69 * scale, 220 * scale)
	ac.setFontSize(label_speed, 40 * scale)

	ac.setPosition(label_gear, 318 * scale, 226 * scale)
	ac.setFontSize(label_gear, 90 * scale)

	ac.setPosition(label_fuel, 195 * scale, 220 * scale)
	ac.setFontSize(label_fuel, 40 * scale)

	ac.setPosition(label_abs, 438 * scale, 302 * scale)
	ac.setFontSize(label_abs, 40 * scale)

	ac.setPosition(label_brakeBias, 438 * scale, 220 * scale)
	ac.setFontSize(label_brakeBias, 40 * scale)

	ac.setPosition(label_tc, 69 * scale, 302 * scale)
	ac.setFontSize(label_tc, 40 * scale)

	ac.setPosition(label_ERScurrent, 478 * scale, 86 * scale)
	ac.setFontSize(label_ERScurrent, 40 * scale)

	ac.setPosition(label_deploy, 478 * scale, 155 * scale)
	ac.setFontSize(label_deploy, 40 * scale)

	ac.setPosition(label_estimatedLaps, 195 * scale, 302 * scale)
	ac.setFontSize(label_estimatedLaps, 40 * scale)

	ac.setPosition(spinner_scale, 0, 383 * scale)
	ac.setFontSize(spinner_scale, 20 * scale)
	ac.setSize(spinner_scale, 201 * scale, 40 * scale)

	ac.setPosition(button_indicators, 302 * scale, 383 * scale)
	ac.setFontSize(button_indicators, 20 * scale)
	ac.setSize(button_indicators, 201 * scale, 40 * scale)

	ac.setPosition(button_speedInMPH, 201 * scale, 383 * scale)
	ac.setFontSize(button_speedInMPH, 20 * scale)
	ac.setSize(button_speedInMPH, 101 * scale, 40 * scale)

	ac.setSize(button_settingsVisible, 503 * scale, 383 * scale)

	indicatorsCoordinates = [(0, -15 * scale), (278 * scale, -15 * scale), (0, 383 * scale), (278 * scale, 383 * scale)]

def acMain(ac_version):
	global appWindow, label_laptime, label_delta, label_speed, label_gear, label_fuel, label_tc, label_abs
	global label_brakeBias, label_ERScurrent, label_deploy, label_estimatedLaps, texture_checkeredFlag
	global spinner_scale, scale, scaleUpdate, button_settingsVisible, button_speedInMPH, button_indicators, settingsVisible

	ac.initFont(0, "Ubuntu", 0, 1)

	appWindow = ac.newApp("LMP GUI")
	ac.setTitle(appWindow, "")
	ac.setIconPosition(appWindow, -7000, -3000)
	ac.drawBorder(appWindow, 0)
	ac.setBackgroundTexture(appWindow, "apps/python/LmpGUI/images/gui.png")

	label_laptime = ac.addLabel(appWindow, "00:00:000")
	ac.setCustomFont(label_laptime, "Ubuntu", 0, 1)
	ac.setFontColor(label_laptime, 0.2, 0.63, 0.2, 1)
	ac.setFontAlignment(label_laptime, "right")

	label_delta = ac.addLabel(appWindow, "0.000")
	ac.setCustomFont(label_delta, "Ubuntu", 0, 1)
	ac.setFontColor(label_delta, 0.78, 0.78, 0.78, 1)
	ac.setFontAlignment(label_delta, "right")

	label_speed = ac.addLabel(appWindow, "0")
	ac.setCustomFont(label_speed, "Ubuntu", 0, 1)
	ac.setFontColor(label_speed, 0.78, 0.78, 0.78, 1)
	ac.setFontAlignment(label_speed, "center")

	label_gear = ac.addLabel(appWindow, "N")
	ac.setCustomFont(label_gear, "Ubuntu", 0, 1)
	ac.setFontColor(label_gear, 0.82, 0.78, 0, 1)
	ac.setFontAlignment(label_gear, "center")

	label_fuel = ac.addLabel(appWindow, "0.0")
	ac.setCustomFont(label_fuel, "Ubuntu", 0, 1)
	ac.setFontColor(label_fuel, 0.82, 0.78, 0, 1)
	ac.setFontAlignment(label_fuel, "center")

	label_tc = ac.addLabel(appWindow, "-")
	ac.setCustomFont(label_tc, "Ubuntu", 0, 1)
	ac.setFontColor(label_tc, 0.78, 0.78, 0.78, 1)
	ac.setFontAlignment(label_tc, "center")

	label_abs = ac.addLabel(appWindow, "-")
	ac.setCustomFont(label_abs, "Ubuntu", 0, 1)
	ac.setFontColor(label_abs, 0.23, 0.31, 0.69, 1)
	ac.setFontAlignment(label_abs, "center")

	label_brakeBias = ac.addLabel(appWindow, "0")
	ac.setCustomFont(label_brakeBias, "Ubuntu", 0, 1)
	ac.setFontColor(label_brakeBias, 0.23, 0.31, 0.69, 1)
	ac.setFontAlignment(label_brakeBias, "center")

	label_ERScurrent = ac.addLabel(appWindow, "-")
	ac.setCustomFont(label_ERScurrent, "Ubuntu", 0, 1)
	ac.setFontColor(label_ERScurrent, 0.05, 0.62, 0.65, 1)
	ac.setFontAlignment(label_ERScurrent, "right")

	label_deploy = ac.addLabel(appWindow, "-")
	ac.setCustomFont(label_deploy, "Ubuntu", 0, 1)
	ac.setFontColor(label_deploy, 0.05, 0.62, 0.65, 1)
	ac.setFontAlignment(label_deploy, "right")

	label_estimatedLaps = ac.addLabel(appWindow, "-")
	ac.setCustomFont(label_estimatedLaps, "Ubuntu", 0, 1)
	ac.setFontColor(label_estimatedLaps, 0.82, 0.78, 0, 1)
	ac.setFontAlignment(label_estimatedLaps, "center")

	spinner_scale = ac.addSpinner(appWindow, "")
	ac.setRange(spinner_scale, 10, 250)
	ac.setStep(spinner_scale, 10)
	ac.addOnValueChangeListener(spinner_scale, onSpinnerScaleValueChanged)
	ac.setVisible(spinner_scale, 0)

	button_settingsVisible = ac.addButton(appWindow, "")
	ac.setPosition(button_settingsVisible, 0, 0)
	ac.setBackgroundOpacity(button_settingsVisible, 0)
	ac.addOnClickedListener(button_settingsVisible, onSettingsVisibleButtonClicked)
	ac.drawBorder(button_settingsVisible, 0)

	button_indicators = ac.addButton(appWindow, "Wheel indicators: {}".format(formatSwitchFromBool(indicatorsON)))
	ac.addOnClickedListener(button_indicators, onIndicatorsButtonClicked)
	ac.setVisible(button_indicators, 0)

	button_speedInMPH = ac.addButton(appWindow, "MPH: {}".format(formatSwitchFromBool(speedInMPH)))
	ac.addOnClickedListener(button_speedInMPH, onSpeedInMPHButtonClicked)
	ac.setVisible(button_speedInMPH, 0)

	loadSettings()
	ac.setValue(spinner_scale, scale * 100)

	texture_checkeredFlag = ac.newTexture("apps/python/LmpGUI/images/checkeredFlag.png")

	ac.addRenderCallback(appWindow, onFormRender)

	scaleUpdate = True

	return "LMP GUI"

def onSettingsVisibleButtonClicked(*args):
	global spinner_scale, button_indicators, settingsVisible
	settingsVisible = not settingsVisible
	ac.setVisible(spinner_scale, settingsVisible)
	ac.setVisible(button_indicators, settingsVisible)
	ac.setVisible(button_speedInMPH, settingsVisible)

def onIndicatorsButtonClicked(*args):
	global button_indicators, indicatorsON
	indicatorsON = not indicatorsON
	ac.setText(button_indicators, "Wheel indicators: {}".format(formatSwitchFromBool(indicatorsON)))

def onSpinnerScaleValueChanged(*args):
	global scale, scaleUpdate
	scale = ac.getValue(spinner_scale) / 100
	scaleUpdate = True

def onSpeedInMPHButtonClicked(*args):
	global button_speedInMPH, speedInMPH
	speedInMPH = not speedInMPH
	ac.setText(button_speedInMPH, "MPH: {}".format(formatSwitchFromBool(speedInMPH)))

def onFormRender(deltaT):
	drawRPMLights()
	drawFlag()
	drawTyresIndicators()
	updateScale()

def acUpdate(deltaT):
	global label_laptime, label_delta, label_speed, label_gear, label_fuel, label_tc, label_abs, label_brakeBias, label_ERScurrent, label_deploy, label_estimatedLaps
	global fuelAmount, fuelAmountStart, totalFuelBurnt, maxRPM, hasERSorKERS, lapCount, lastLapCount, lapsNotInPitCount, wasInPit, flagType
	global timerFlag, timer60perSecond, timer10perSecond, timer1perSecond

	timerFlag += deltaT
	timer60perSecond += deltaT
	timer10perSecond += deltaT
	timer1perSecond += deltaT

	if timer60perSecond > 0.0167:
		timer60perSecond = 0
		
		lapTime = ac.getCarState(0, acsys.CS.LapTime)
		lapCount = ac.getCarState(0, acsys.CS.LapCount)
		delta = ac.getCarState(0, acsys.CS.PerformanceMeter)
		speed = getSpeed()
		gear = ac.getCarState(0, acsys.CS.Gear)
		fuelAmount = info.physics.fuel

		if(lapTime > 5000 or lapCount == 0):
			ac.setText(label_laptime, formatTime(lapTime))
			
		deltaString = "{:.3f}".format(delta)
		
		if delta == 0:
			ac.setFontColor(label_delta, 0.78, 0.78, 0.78, 1)
		elif delta > 0:
			ac.setFontColor(label_delta, 1, 0, 0, 1)
			deltaString = "+" + deltaString
		else:
			ac.setFontColor(label_delta, 0.2, 0.63, 0.2, 1)
	
		if hasERSorKERS:
			ERSValue = info.physics.kersCharge * 100
			ac.setText(label_ERScurrent, str(int(ERSValue)))

			deployValue = calculateDeploy()
			ac.setText(label_deploy, str(int(deployValue)))

		ac.setText(label_delta, deltaString)
		ac.setText(label_speed, str(int(speed)))
		ac.setText(label_gear, formatGear(gear))

	if timer10perSecond > 0.167:
		timer10perSecond = 0
		
		tcValue = info.physics.tc
		absValue = info.physics.abs
		brakeBias = info.physics.brakeBias * 100

		ac.setText(label_tc, formatSwitchFromBool(tcValue))
		ac.setText(label_abs, formatSwitchFromBool(absValue))

		flagType = info.graphics.flag

		ac.setText(label_brakeBias, "{:.1f}".format(brakeBias))
		ac.setText(label_fuel, "{:.1f}".format(fuelAmount))

	if timerFlag > 2:
		timerFlag = 0

	if timer1perSecond > 1:
		timer1perSecond = 0
		
		hasERS = info.static.hasERS
		hasKERS = info.static.hasKERS
		if hasERS or hasKERS:
			hasERSorKERS = 1

		maxRPM = info.static.maxRpm
		
		if info.graphics.isInPit:
			wasInPit = 1

		if lastLapCount != lapCount:
			lastLapCount = lapCount
			if lapCount > 0 and not wasInPit:
				fuelBurnt = fuelAmountStart - fuelAmount
				totalFuelBurnt += fuelBurnt
				lapsNotInPitCount += 1

			fuelAmountStart = fuelAmount
			wasInPit = 0
		
		estimatedLaps = calculateEstimatedLaps()

		if lapCount > 0 and estimatedLaps > 0:
			ac.setText(label_estimatedLaps, "{:.1f}".format(estimatedLaps))

def acShutdown():
	saveSettings()
