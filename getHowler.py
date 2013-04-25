import zipfile
import sys, os
import shutil
import urllib
from pymel.core import *
from pymel.util import *

def getScriptsPath():
    for p in util.getEnv("MAYA_SCRIPT_PATH").split(":"):
        if "maya/scripts" in p and "Shared" in p:
            return p

def getPluginsPath():
  for p in util.getEnv("MAYA_PLUG_IN_PATH").split(":"):
	    if "maya/plug-ins" in p and "Shared" in p:
	        return p
		        
scriptsPath = getScriptsPath()
pluginsPath = getPluginsPath()
howlerUrl = "http://www.colinstanton.com/stantco/wp-content/uploads/2013/04/howlerPackage.zip"
howlerDir = "%s/data/" % workspace.path
if not os.path.exists(howlerDir)
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

shutil.copy(cmdPath,pluginsPath)
shutil.copy(httplib2Path,scriptsPath)
shutil.copy(oauth2Path,scriptsPath)
shutil.copy(posterPath,scriptsPath)

loadPlugin("howlerCmd.py")
unloadPlugin("howlerCmd.py")
loadPlugin("howlerCmd.py")
