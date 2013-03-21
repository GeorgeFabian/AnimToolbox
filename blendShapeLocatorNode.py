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

kPluginNodeName = "blendShapeLocatorNode"
kPluginNodeId = OpenMaya.MTypeId(0x00000001)


class blendShapeLocatorNode(OpenMayaMPx.MPxNode):

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
		mplugin.registerNode( kPluginNodeName, kPluginNodeId, nodeCreator, nodeInitializer)
	except:
		sys.stderr.write( "Failed to register node: %s" % kPluginNodeName )
		raise
 
# uninitialize the script plug-in
def uninitializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterNode( kPluginNodeId )
	except:
		sys.stderr.write( "Failed to deregister node: %s" % kPluginNodeName )
		raise
