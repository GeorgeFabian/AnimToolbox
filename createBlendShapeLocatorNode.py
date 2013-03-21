from pymel.core import *
import time

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


def updateBSLTxt(*args):
    pass
    # selected = blendShapeLocatorList.getSelectItem()[0]
    # newBlendShapeLocatorTxt.setText(selected)    
    
blendShapeLocatorList = textScrollList(selectCommand=updateBSLTxt,allowMultiSelection=True)
# layout.redistribute()

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
    

loadDrivenBtn.setCommand(loadDriven)
loadExpressiveBtn.setCommand(loadExpressive)
loadBothBtn.setCommand(loadBoth)
addLocatorToBlendShapeBtn.setCommand(addLocatorToBlendShape)
newBlendShapeLocatorBtn.setCommand(newBlendShapeLocator)
mirrorBlendShapeLocatorBtn.setCommand(mirrorBlendShapeLocator)
win.show()
