import maya.cmds as cmds
from functools import partial
import math
import random

objName = "snowflake"
height = 0.05
radius = 0.1
length = 1
scale = 0.1

mainBranchDefault = 6
subdivDefault = 20
subBranchDefault = 3
ls = (.1,.1,.1)

posiMin = lenMin = 0
posiMax = lenMax = 1
angleMin = 5
angleMax = 90
posiStep = 0.01
lenStep = 0.1
anglStep = 1

def ws_center(pObj):
  bbx = cmds.xform(pObj, q=True, bb=True, ws=True)
  centerX = (bbx[0] + bbx[3]) / 2.0
  centerY = (bbx[1] + bbx[4]) / 2.0
  centerZ = (bbx[2] + bbx[5]) / 2.0
  return (centerX, centerY, centerZ)

def make_sub_branches(percntAlongBranch, local_scl, len, angle):
  lx = len*math.cos(angle*math.pi/180)
  lz = len*math.sin(angle*math.pi/180)

  mainBranches = cmds.intSliderGrp(mainBranchSlider, q=True, value=True)
  subdiv = cmds.intSliderGrp(numSubdvSlider, q=True, value=True)

  startFace = int(percntAlongBranch*(subdiv-1)) + (mainBranches+2+subdiv)

  for i in range(startFace, startFace+(subdiv*2)*(mainBranches*2), subdiv*2):
    # if coord of face in -z, change local_dir so branches point right way
    if mainBranches%2==1:
      if ws_center(objName+'.f[%s]' %i)[0] < 0:
        local_dir = (-1,0,0)
      else:
        local_dir = (1,0,0)
    else:
      if ws_center(objName+'.f[%s]' %i)[2] < 0:
        local_dir = (0,0,-1)
      else:
        local_dir = (0,0,1)
    

    cmds.polyExtrudeFacet(objName+'.f[%s]' %i, ld=local_dir, lt=(lx, 0, lz), 
                            ls=local_scl)#, d=subdiv/2)

def random_sub_br(slider):
  for i in range(cmds.intSliderGrp(slider, q=True, value=True)):
    make_sub_branches(random.random(), ls, random.random(), random.randint(10, 90))

def create(*args):
  flkLst = cmds.ls(objName)
  if len(flkLst) > 0:
    cmds.delete(flkLst)

  mainBranches = cmds.intSliderGrp(mainBranchSlider, q=True, value=True)
  subdiv = cmds.intSliderGrp(numSubdvSlider, q=True, value=True)

  cmds.polyCylinder(n=objName, sa=mainBranches, h=height, r=radius)
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(mainBranches-1), kft=False, 
                        lt=(0,0,length), ls=(scale,scale,1), d=subdiv)
  
  random_sub_br(numSubBranches)

def resetCallback(*pArgs):
  # return UI to default values
  cmds.intSliderGrp(mainBranchSlider, e=True, value=mainBranchDefault)
  cmds.intSliderGrp(numSubdvSlider, e=True, value=subdivDefault)
  cmds.intSliderGrp(numSubBranches, e=True, value=subBranchDefault)

  # remake default snowflake
  create()

def create_slider(pLabel, pMin, pMax, pVal, pStep, function, show=True):
  slider = cmds.intSliderGrp(label=pLabel, columnAlign= (1,'right'), 
                                  field=True, min=pMin, max=pMax, value=pVal, 
                                  step=pStep, dc = 'empty')
  cmds.intSliderGrp(slider,  e=True, dc = partial(function), visible=show)

  return slider

def create_branch_controls(pLabel, pPosiVal, pLenVal, pAnglVal, function, enable=True):
  cmds.text(label=pLabel, en=enable)
  posiSlider = cmds.floatSliderGrp(columnAlign= (1,'right'), field=True, min=posiMin, 
                                   max=posiMax, value=pPosiVal, step=posiStep, dc = 'empty')
  cmds.floatSliderGrp(posiSlider,  e=True, dc = partial(function), en=enable)
  lenSlider = cmds.floatSliderGrp(columnAlign= (1,'right'), field=True, min=lenMin, 
                                   max=lenMax, value=pLenVal, step=lenStep, dc = 'empty')
  cmds.floatSliderGrp(lenSlider,  e=True, dc = partial(function), en=enable)
  angleSlider = cmds.intSliderGrp(columnAlign= (1,'right'), field=True, min=angleMin, 
                                   max=angleMax, value=pAnglVal, step=anglStep, dc = 'empty')
  cmds.intSliderGrp(angleSlider,  e=True, dc = partial(function), en=enable)

  return (posiSlider, lenSlider, angleSlider)

#-------------UI--------------------#
windowID = "myWindowID"

if cmds.window(windowID, exists=True):
  cmds.deleteUI(windowID)
    
cmds.window(windowID, title='Snowflake Generator', sizeable=False, resizeToFitChildren=True)
cmds.columnLayout(adjustableColumn=True)

# branch controls
cmds.separator(h=10, style='none')
mainBranchSlider = create_slider('Main Branches', 3, 12, mainBranchDefault, 1, create)
numSubdvSlider = create_slider('Subdivision', 1, 50, subdivDefault, 1, create)
numSubBranches = create_slider('Sub-Branches', 1, 7, subBranchDefault, 1, create)
cmds.separator(h=5, style='out')

# sub branch controls
cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[(1,130),(2, 150),(3, 150),(4, 150)])
# headings
cmds.separator(h=5, style='none')
cmds.text(label='position', align='left')
cmds.text(label='length', align='left')
cmds.text(label='angle', align='left')
# branches
sub_1 = create_branch_controls('Sub-Branch 1', random.random(), random.random(), 
                               random.randint(angleMin, angleMax), create)
sub_2 = create_branch_controls('Sub-Branch 2', random.random(), random.random(), 
                               random.randint(angleMin, angleMax), create)
sub_3 = create_branch_controls('Sub-Branch 3', random.random(), random.random(), 
                               random.randint(angleMin, angleMax), create)
sub_4 = create_branch_controls('Sub-Branch 4', random.random(), random.random(), 
                               random.randint(angleMin, angleMax), create, False)
sub_5 = create_branch_controls('Sub-Branch 5', random.random(), random.random(), 
                               random.randint(angleMin, angleMax), create, False)
sub_6 = create_branch_controls('Sub-Branch 6', random.random(), random.random(), 
                               random.randint(angleMin, angleMax), create, False)
sub_7 = create_branch_controls('Sub-Branch 7', random.random(), random.random(), 
                               random.randint(angleMin, angleMax), create, False)

#buttons
# cmds.separator(h=10, style='none')
cmds.setParent('..')
cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[(1,400),(2, 75), (3, 10), (4,75)])
cmds.separator(h=5, style='none')
cmds.button(label='Re-Create', command=partial(create))
cmds.separator(h=5, style='none')
cmds.button(label='Reset', command=partial(resetCallback, windowID))
cmds.separator(h=5, style='none')

cmds.showWindow()
  
#-----------------Main----------------------#
create()
cmds.select(objName)