# createNode("blendShapeLocatorNode")
# connectAttr(PyNode("locator1").worldPosition,PyNode("blendShapeLocatorNode1").blndLoc)
# connectAttr(PyNode("locator1").scaleX,PyNode("blendShapeLocatorNode1").falloff)
# connectAttr(PyNode("pCubeShape1").outMesh,PyNode("blendShapeLocatorNode1").drvnMesh)
# connectAttr(PyNode("pCubeShape2").outMesh,PyNode("blendShapeLocatorNode1").exprMesh)
# connectAttr(PyNode("pCubeShape2").worldMatrix,PyNode("blendShapeLocatorNode1").exprPosn)
# connectAttr(PyNode("pCubeShape3").outMesh,PyNode("blendShapeLocatorNode1").blendMeshIn)
# connectAttr(PyNode("blendShapeLocatorNode1").blndMeshOut,PyNode("pCubeShape3").inMesh)

# createNode("blendShapeLocatorNode")
# connectAttr(PyNode("locator1").worldPosition,PyNode("blendShapeLocatorNode1").blndLoc)
# connectAttr(PyNode("locator1").scaleX,PyNode("blendShapeLocatorNode1").falloff)
# connectAttr(PyNode("MMM_NeutralShape").outMesh,PyNode("blendShapeLocatorNode1").drvnMesh)
# connectAttr(PyNode("smileShape").outMesh,PyNode("blendShapeLocatorNode1").exprMesh)
# connectAttr(PyNode("MMM_Neutral1Shape").outMesh,PyNode("blendShapeLocatorNode1").blendMeshIn)
# connectAttr(PyNode("blendShapeLocatorNode1").blndMeshOut,PyNode("MMM_Neutral1Shape").inMesh)

import sys
from pymel.core import *
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

class blendShapeUI(OpenMayaMPx.MPxCommand):

	kPluginCmdName = "blendShapeUI"

	def __init__(self):
		OpenMayaMPx.MPxCommand.__init__(self)

	#Set the text of the driven shape textbox to the selected transform node. 
	def loadDriven(*args):
	    driven = ls(sl=True)[0]
	    drivenTxt.setText(driven)

	#Set the text of the expressive shape textbox to be the selected transform node.
	#Also loads any previously created blend shape masks to the list by checking
	# for user created attributes. Needs exception checking, possibly a prefix to
	# help distinguish blend shape masks from other user defined attributes.
	def loadExpressive(*args):
	    expressive = ls(sl=True)[0]
	    expressiveTxt.setText(expressive)
	    expressiveShape = expressive.getShape()
	    
	    blendShapeLocatorList.removeAll()
	    blendShapeLocatorList.append(mappings)

	#Load both driven and expressive mesh.    
	def loadBoth(*args):
	    selection = ls(sl=True)
	    expressive = selection[0]
	    
	    expressiveShape = expressive.getShape()
	    
	    mappings = listAttr(expressiveShape,ud=True)
	    blendShapeLocatorList.removeAll()
	    blendShapeLocatorList.append(mappings)
	    
	    try:
	        expressiveTxt.setText(selection[0])
	        drivenTxt.setText(selection[1])
	    except:
	        warning("Select the blend shape expressives mesh THEN the driven mesh")

	def mirrorBlendShapeLocator(*args):
	    selectedLocatorName = blendShapeLocatorList.getSelectItem()[0]
	    selectedLocator = PyNode(selectedLocatorName)
	    expressiveName = expressiveTxt.getText()
	    expressive = PyNode(expressiveName)
	    newBlendShapeLocator()
	    mirrorLocatorName = expressiveName + "_" + newBlendShapeLocatorTxt.getText() + "_loc"
	    mirrorLocator = PyNode(mirrorLocatorName)

	    tX = getAttr(selectedLocator.translateX)
	    bbX_dist = 2*(getAttr(expressive.boundingBoxCenterX) - tX)

	    setAttr(mirrorLocator.scale, getAttr(selectedLocator.scale))
	    setAttr(mirrorLocator.translate,getAttr(selectedLocator.translate))
	    setAttr(mirrorLocator.translateX, tX + bbX_dist)

	def addLocatorToBlendShape(*args):
	    selectedLocatorName = blendShapeLocatorList.getSelectItem()[0]
	    expressiveName = expressiveTxt.getText()
	    expressive = PyNode(expressiveName)
	    driven = PyNode(drivenTxt.getText())
	    select(expressive)
	    select(driven,add=True)

	    name = selectedLocatorName
	    # locNum = str(int(selectedLocatorName.split("_")[-1]) + 1)
	    # name = selectedLocatorName.split("_")[:-1]
	    # name.append(locNum)
	    # name = "_".join(name)

	    expressiveShape = expressive.getShape()
	    drivenShape = driven.getShape()

	    locator = spaceLocator(n=name)
	    BSLN_1 = PyNode(selectedLocatorName).connections()[0]
	    BSLN_2 = createNode("blendShapeLocatorNode")
	    avgMeshNode = createNode("averageMeshesNode")
	    print avgMeshNode

	    blendshape = PyNode(selectedLocatorName).connections()[0].blendMeshOut.connections()[0]

	    disconnectAttr(BSLN_1.blendMeshOut, blendshape.inMesh)

	    connectAttr(locator.worldPosition,BSLN_2.blndLoc)
	    connectAttr(locator.scaleX,BSLN_2.blendFalloff)
	    connectAttr(drivenShape.outMesh,BSLN_2.drvnMesh)
	    connectAttr(expressiveShape.outMesh,BSLN_2.exprMesh)
	    connectAttr(expressiveShape.worldMatrix,BSLN_2.exprPosn)
	    connectAttr(blendshape.outMesh,BSLN_2.blendMeshIn)

	    connectAttr(BSLN_1.blendMeshOut, avgMeshNode.meshOne)
	    connectAttr(BSLN_2.blendMeshOut, avgMeshNode.meshTwo)
	    connectAttr(blendshape.outMesh, avgMeshNode.meshIn)
	    connectAttr(avgMeshNode.meshOut, blendshape.inMesh)

	    blendShapeLocatorList.append(name)

	#Creates a new blend shape mask.
	def newBlendShapeLocator(*args):
	    
	    node = createNode("blendShapeLocatorNode")
	    name = newBlendShapeLocatorTxt.getText()
	    expressiveName = expressiveTxt.getText()
	    expressive = PyNode(expressiveName)
	    driven = PyNode(drivenTxt.getText())
	    select(expressive)
	    select(driven,add=True)

	    expressiveShape = expressive.getShape()
	    drivenShape = driven.getShape()
	   
	    if len(name) <= 0:
	        warning("No mask name specified")
	        return
	    else:
	        locname = expressiveName + "_" + name + "_loc"
	        

	    locator = spaceLocator(n=locname)

	    blendshape = duplicate(driven,n=expressiveName + "_" + name,st=True)[0]

	    transY = getAttr(blendshape.translateY)
	    boundingY = getAttr(blendshape.boundingBoxSizeY)

	    setAttr(blendshape.translateY,transY + boundingY)

	    blendShapeLocatorList.append(locname)


	    connectAttr(locator.worldPosition,node.blndLoc)
	    connectAttr(locator.scaleX,node.blendFalloff)
	    connectAttr(drivenShape.outMesh,node.drvnMesh)
	    connectAttr(expressiveShape.outMesh,node.exprMesh)
	    connectAttr(expressiveShape.worldMatrix,node.exprPosn)
	    connectAttr(blendshape.outMesh,node.blendMeshIn)
	    connectAttr(node.blndMeshOut,blendshape.inMesh)

	def doIt(self, args):
		#if the window exists, delete it and create a new one.
		if uitypes.Window.exists("blendShapeLocators"):
		    deleteUI('blendShapeLocators')
		win = window('blendShapeLocators',title="Blend Shape Locators")

		##############################
		# UI SETUP
		##############################

		layout = scrollLayout()
		loadBothBtn = button(label="Load Blend Shape AND Mesh")
		loadExpressiveBtn = button(label="Load Expressive Blend Shape", parent=layout)
		expressiveTxt = textField(text="EXPRESSIVE",ed=False)
		loadDrivenBtn = button(label="Load Driven Mesh", parent=layout)
		drivenTxt = textField(text="DRIVEN",ed=False)
		mirrorBlendShapeLocatorBtn = button(label="Mirror Selected Locator")
		addLocatorToBlendShapeBtn = button(label="Add Locator to Blend Shape")
		newBlendShapeLocatorBtn = button(label="New Blend Shape Locator")
		newBlendShapeLocatorTxt = textField(text="") 
		blendShapeLocatorList = textScrollList(allowMultiSelection=True)

		loadDrivenBtn.setCommand(self.loadDriven)
		loadExpressiveBtn.setCommand(self.loadExpressive)
		loadBothBtn.setCommand(self.loadBoth)
		addLocatorToBlendShapeBtn.setCommand(self.addLocatorToBlendShape)
		newBlendShapeLocatorBtn.setCommand(self.newBlendShapeLocator)
		mirrorBlendShapeLocatorBtn.setCommand(self.mirrorBlendShapeLocator)
		win.show()

def cmdCreator():
	ptr = OpenMayaMPx.asMPxPtr( blendShapeUI() )
	return ptr

class blendShapeLocatorNode(OpenMayaMPx.MPxNode):

	kPluginNodeName = "blendShapeLocatorNode"
	kPluginNodeId = OpenMaya.MTypeId(0x00000001)

	def __init__(self):
		OpenMayaMPx.MPxNode.__init__(self)

	def compute(self, plug, data):
		if plug == blendShapeLocatorNode.blendMeshOut:

			drivenMeshHandle = data.inputValue(blendShapeLocatorNode.drivenMesh)
			drvnMesh = drivenMeshHandle.data()

			expressiveMeshHandle = data.inputValue(blendShapeLocatorNode.expressiveMesh)
			exprMesh = expressiveMeshHandle.data()
			expressivePosnHandle = data.inputValue(blendShapeLocatorNode.expressivePosn)
			matrix = expressivePosnHandle.asMatrix()
			exprPosn = [matrix(3,0),matrix(3,1),matrix(3,2)]

			blendLocator = data.inputValue(blendShapeLocatorNode.blendLocator)
			blndLoc = blendLocator.asDouble3()
			blendFalloff = data.inputValue(blendShapeLocatorNode.blendFalloff)
			falloff = max(min(blendFalloff.asDouble(), 200), .01)

			blendMeshHandle = data.inputValue(blendShapeLocatorNode.blendMeshIn)
			blndMesh = blendMeshHandle.data()
			# blndMFnMesh = OpenMaya.MFnMesh(blndMesh)

			# rampHandle = data.inputValue(blendShapeLocatorNode.ramp)
			# ramp = ramp.data()


			drvnVertIter = OpenMaya.MItMeshVertex(drvnMesh)
			exprVertIter = OpenMaya.MItMeshVertex(exprMesh)
			blndVertIter = OpenMaya.MItMeshVertex(blndMesh)
			if not exprVertIter.count() == blndVertIter.count():
				print "Mesh vertex counts are not equivalent" 
				return

			# colors = OpenMaya.MColorArray()
			# vertCount = blndVertIter.count()
			# verts = []

			while not exprVertIter.isDone():
				exprVertPos = exprVertIter.position()
				drvnVertPos = drvnVertIter.position()

				exprVertPosX = exprVertPos.x + exprPosn[0]
				exprVertPosY = exprVertPos.y + exprPosn[1]
				exprVertPosZ = exprVertPos.z + exprPosn[2]

				x = (exprVertPosX-blndLoc[0])**2
				y = (exprVertPosY-blndLoc[1])**2
				z = (exprVertPosZ-blndLoc[2])**2

				dist = (x+y+z)**0.5

				softness = dist/falloff

				softness = max(min(softness, 1), 0)

				# colors.append(OpenMaya.MColor(softness,0.0,0.0))
				# verts.append(exprVertIter.index())

				diffX = exprVertPos.x - drvnVertPos.x
				diffY = exprVertPos.y - drvnVertPos.y
				diffZ = exprVertPos.z - drvnVertPos.z

				exprVertPos.x = exprVertPos.x - diffX*softness
				exprVertPos.y = exprVertPos.y - diffY*softness
				exprVertPos.z = exprVertPos.z - diffZ*softness

				if dist < falloff:
					blndVertIter.setPosition(exprVertPos)
				else:
					blndVertIter.setPosition(drvnVertPos)
				drvnVertIter.next()
				exprVertIter.next()
				blndVertIter.next()

			# intArr = OpenMaya.MIntArray()
			# for v in verts:
			# 	intArr.append(v)
			# blndMFnMesh.setVertexColors(colors,intArr)
			outputHandle = data.outputValue(blendShapeLocatorNode.blendMeshOut)
			outputHandle.setMObject(blndMesh)

			data.setClean(plug)
		else:
			return OpenMaya.kUnknownParameter
 
def nodeCreator():
	return OpenMayaMPx.asMPxPtr( blendShapeLocatorNode() )
 
def nodeInitializer():
	typedAttr = OpenMaya.MFnTypedAttribute()
	numericAttr  = OpenMaya.MFnNumericAttribute()
	matrixAttr = OpenMaya.MFnMatrixAttribute()
	# rampAttr = OpenMaya.MFnRamp
 
	blendShapeLocatorNode.expressiveMesh = typedAttr.create("expressiveMesh", "exprMesh", OpenMaya.MFnData.kMesh)
	blendShapeLocatorNode.expressivePosn = matrixAttr.create("expressivePosn", "exprPosn")
	blendShapeLocatorNode.drivenMesh = typedAttr.create("drivenMesh", "drvnMesh", OpenMaya.MFnData.kMesh)
	blendShapeLocatorNode.blendLocator = numericAttr.create("blendLocator", "blndLoc", OpenMaya.MFnNumericData.k3Double)
	blendShapeLocatorNode.blendFalloff = numericAttr.create("blendFalloff", "falloff", OpenMaya.MFnNumericData.kDouble)
	blendShapeLocatorNode.blendMeshIn = typedAttr.create("blendMeshIn", "blndMeshIn", OpenMaya.MFnData.kMesh)
	blendShapeLocatorNode.blendMeshOut = typedAttr.create("blendMeshOut", "blndMeshOut", OpenMaya.MFnData.kMesh)

	blendShapeLocatorNode.addAttribute(blendShapeLocatorNode.expressiveMesh)
	blendShapeLocatorNode.addAttribute(blendShapeLocatorNode.expressivePosn)
	blendShapeLocatorNode.addAttribute(blendShapeLocatorNode.drivenMesh)
	blendShapeLocatorNode.addAttribute(blendShapeLocatorNode.blendLocator)
	blendShapeLocatorNode.addAttribute(blendShapeLocatorNode.blendFalloff)
	blendShapeLocatorNode.addAttribute(blendShapeLocatorNode.blendMeshIn)
	blendShapeLocatorNode.addAttribute(blendShapeLocatorNode.blendMeshOut)
 
	blendShapeLocatorNode.attributeAffects(blendShapeLocatorNode.expressiveMesh, blendShapeLocatorNode.blendMeshOut)
	blendShapeLocatorNode.attributeAffects(blendShapeLocatorNode.expressivePosn, blendShapeLocatorNode.blendMeshOut)
	blendShapeLocatorNode.attributeAffects(blendShapeLocatorNode.blendLocator, blendShapeLocatorNode.blendMeshOut)
 
 
# initialize the script plug-in
def initializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.registerNode( blendShapeLocatorNode.kPluginNodeName, blendShapeLocatorNode.kPluginNodeId, nodeCreator, nodeInitializer)
	except:
		sys.stderr.write( "Failed to register node: %s" % blendShapeLocatorNode.kPluginNodeName )
		raise
	try:
		mplugin.registerCommand( blendShapeUI.kPluginCmdName, cmdCreator)
	except:
		sys.stderr.write( "Failed to register command: %s" % blendShapeUI.kPluginCmdName )
		raise
 
# uninitialize the script plug-in
def uninitializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterNode( blendShapeLocatorNode.kPluginNodeId )
	except:
		sys.stderr.write( "Failed to deregister node: %s" % blendShapeLocatorNode.kPluginNodeName )
		raise
	try:
		mplugin.deregisterCommand( blendShapeUI.kPluginCmdName )
	except:
		sys.stderr.write( 'Failed to unregister command: ' + blendShapeUI.kPluginCmdName )
		raise




