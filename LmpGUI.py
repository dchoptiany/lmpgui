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

if platform.architecture()[0] == "64bit":
	sysdir = os.path.dirname(__file__)+'/stdlib64'
else:
	sysdir = os.path.dirname(__file__)+'/stdlib'

sys.path.insert(0, sysdir)
os.environ['PATH'] = os.environ['PATH'] + ";."

from lmpgui_lib.sim_info import info

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
button_spinnerVisible = 0

spinnerVisible = 0

scale = 1

lastLapCount = -1
lapCount = 0
lapsNotInPitCount = 0
wasInPit = 0

flagType = 0

timerFlag = 0
timer60perSecond = 0
timer10perSecond = 0
timer1perSecond = 0

def loadScale():
	global scale

	try:
		with open("apps/python/LmpGUI/scale.txt", "r") as f:
			scale = float(f.readline())
	except:
		ac.console("Could not open scale.txt. Scale has been set to 1.")

def saveScale():
	global scale

	try:
		with open("apps/python/LmpGUI/scale.txt", "w") as f:
			f.write(str(scale))
	except:
		ac.console("Could not save scale to scale.txt.")

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

	return str(minutes) + ":" + "{:02d}".format(seconds) + ":" + "{:03d}".format(milliseconds)

def formatGear(gear):
	if gear == 0:
		return "R"
	elif gear == 1:
		return "N"
	else:
		return str(gear - 1)

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

	if flagType == 0:
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
	elif flagType == 5:
		ac.glColor4f(1, 1, 1, 1)
		ac.glQuadTextured(-20 * scale, 0, 20 * scale, 383 * scale, texture_checkeredFlag)
		ac.glQuadTextured(503 * scale, 0, 20 * scale, 383 * scale, texture_checkeredFlag)
	elif flagType == 6:
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

def updateScale():
	global appWindow, label_laptime, label_delta, label_speed, label_gear, label_fuel, label_tc, label_abs
	global label_brakeBias, label_ERScurrent, label_deploy, label_estimatedLaps
	global spinner_scale, scale, button_spinnerVisible

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

	ac.setSize(button_spinnerVisible, 503 * scale, 383 * scale)

def acMain(ac_version):
	global appWindow, label_laptime, label_delta, label_speed, label_gear, label_fuel, label_tc, label_abs
	global label_brakeBias, label_ERScurrent, label_deploy, label_estimatedLaps, texture_checkeredFlag
	global spinner_scale, scale, button_spinnerVisible, spinnerVisible

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
	ac.setValue(spinner_scale, scale)
	ac.addOnValueChangeListener(spinner_scale, onValueChange)
	ac.setVisible(spinner_scale, 0)

	button_spinnerVisible = ac.addButton(appWindow, "")
	ac.setPosition(button_spinnerVisible, 0, 0)
	ac.setBackgroundOpacity(button_spinnerVisible, 0)
	ac.addOnClickedListener(button_spinnerVisible, onClicked)
	ac.drawBorder(button_spinnerVisible, 0)

	loadScale()
	ac.setValue(spinner_scale, scale * 100)

	texture_checkeredFlag = ac.newTexture("apps/python/LmpGUI/images/checkeredFlag.png")

	updateScale()

	ac.addRenderCallback(appWindow, onFormRender)

	return "LMP GUI"

def onClicked(*args):
	global spinner_scale, spinnerVisible
	spinnerVisible = not spinnerVisible
	ac.setVisible(spinner_scale, spinnerVisible)

def onValueChange(deltaT):
	global spinner_scale, scale
	scale = ac.getValue(spinner_scale) / 100
	updateScale()

def onFormRender(deltaT):
	drawRPMLights()
	drawFlag()

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
		speed = ac.getCarState(0, acsys.CS.SpeedKMH)
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

		if tcValue:
			ac.setText(label_tc, "ON")
		else:
			ac.setText(label_tc, "OFF")
		
		if absValue:
			ac.setText(label_abs, "ON")
		else:
			ac.setText(label_abs, "OFF")

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
	saveScale()
