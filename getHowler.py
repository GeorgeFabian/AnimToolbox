import zipfile
import sys, os
import shutil
import urllib
from pymel.core import *
from pymel.util import *

def getScriptsPath():
    for p in util.getEnv("MAYA_SCRIPT_PATH").split(":"):
        if "prefs" in p and "scripts" in p:
            return p

def getPluginsPath():
	for p in util.getEnv("MAYA_PLUG_IN_PATH").split(":"):
	    if "plug-ins" in p and "Shared" in p and not "20" in p:
	        return p
		        
scriptsPath = getScriptsPath()
pluginsPath = getPluginsPath()
print scriptsPath
print pluginsPath
howlerUrl = "http://www.colinstanton.com/stantco/wp-content/uploads/2013/04/howlerPackage.zip"
howlerDir = "%s/data/" % workspace.path
if not os.path.exists(howlerDir):
	os.makedirs(howlerDir)

howlerFileName = "howlerPackage.zip"
howlerPath = "%s%s" % (howlerDir,howlerFileName)
urllib.urlretrieve(howlerUrl,howlerPath)

howlerZip = zipfile.ZipFile(howlerPath)
howlerZip.extractall(howlerDir)

cmdPath = "%s%s" % (howlerDir,"howlerCmd.py")
httplib2Path = "%s%s" % (howlerDir,"httplib2")
oauth2Path = "%s%s" % (howlerDir,"oauth2")
posterPath = "%s%s" % (howlerDir,"poster")

howlerDestinationPath = os.path.join(pluginsPath,"howlerCmd.py")
httplib2DestinationPath = os.path.join(scriptsPath,"httplib2")
oauth2DestinationPath = os.path.join(scriptsPath,"oauth2")
posterDestinationPath = os.path.join(scriptsPath,"poster")

if os.path.exists(howlerDestinationPath):
	os.remove(howlerDestinationPath)
shutil.move(cmdPath,pluginsPath)

if os.path.exists(httplib2DestinationPath):
	shutil.rmtree(httplib2DestinationPath)
shutil.move(httplib2Path,scriptsPath)

if os.path.exists(oauth2DestinationPath):
	shutil.rmtree(oauth2DestinationPath)
shutil.move(oauth2Path,scriptsPath)

if os.path.exists(posterDestinationPath):
	shutil.rmtree(posterDestinationPath)
shutil.move(posterPath,scriptsPath)


## I have no idea why this works...
loadPlugin("howlerCmd.py")
from pymel.core import *
howler() 


