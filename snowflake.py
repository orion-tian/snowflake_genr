import maya.cmds as cmds
from functools import partial
import math
import random

objName = "snowflake"
height = 0.025
radius = 0.05
length = 0.5
scale = 0.1
sub_scale = (.1,.1,.1)

mainBranchDefault = 6
subdivDefault = 20
subBranchDefault = 3
p_lenDefault = 0.01

posiMin = lenMin = angleMin = 0
posiMax = 1
lenMax = 0.5
angleMax = 180
posiStep = 0.01
lenStep = 0.01
anglStep = 0.1

#-------------Functions--------------------#
def ws_center(pObj):
  bbx = cmds.xform(pObj, q=True, bb=True, ws=True)
  centerX = (bbx[0] + bbx[3]) / 2.0
  centerY = (bbx[1] + bbx[4]) / 2.0
  centerZ = (bbx[2] + bbx[5]) / 2.0
  return (centerX, centerY, centerZ)

def make_sub_branch(percntAlongBranch, local_scl, len, angle):
  lx = len*math.cos(angle*math.pi/180)
  lz = len*math.sin(angle*math.pi/180)

  mainBranches = cmds.intSliderGrp(d_mainBranchSlider, q=True, value=True)
  subdiv = cmds.intSliderGrp(d_numSubdvSlider, q=True, value=True)

  startFace = int(percntAlongBranch*(subdiv-1)) + (mainBranches+2+subdiv)

  for i in range(startFace, startFace+(subdiv*2)*(mainBranches*2), subdiv*2):
    if mainBranches%2==1:
      # if coord of face in -z, change local_dir so branches point right way
      if ws_center(objName+'.f[%s]' %i)[0] < 0:
        local_dir = (-1,0,0)
      else:
        local_dir = (1,0,0)
    else:
      # if odd number of branches, based on x-axis instead
      if ws_center(objName+'.f[%s]' %i)[2] < 0:
        local_dir = (0,0,-1)
      else:
        local_dir = (0,0,1)

    cmds.polyExtrudeFacet(objName+'.f[%s]' %i, ld=local_dir, lt=(lx, 0, lz), ls=local_scl)

def make_subs():
  numSub = cmds.intSliderGrp(d_numSubBranches, q=True, value=True)
  for i in range(len(d_allSubControls)):
    subLabel, posiSlider, lenSlider, angleSlider = d_allSubControls[i]
    if i < numSub:
      posi = cmds.floatSliderGrp(posiSlider, q=True, value=True)
      length = cmds.floatSliderGrp(lenSlider, q=True, value=True)
      angle = cmds.floatSliderGrp(angleSlider, q=True, value=True)
      make_sub_branch(posi, sub_scale, length, angle)
      # enable controls
      cmds.text(subLabel, e=True, enable=True)
      cmds.floatSliderGrp(posiSlider, e=True, enable=True)
      cmds.floatSliderGrp(lenSlider, e=True, enable=True)
      cmds.floatSliderGrp(angleSlider, e=True, enable=True)
    else:
      #disenable controls
      cmds.text(subLabel, e=True, enable=False)
      cmds.floatSliderGrp(posiSlider, e=True, enable=False)
      cmds.floatSliderGrp(lenSlider, e=True, enable=False)
      cmds.floatSliderGrp(angleSlider, e=True, enable=False)

def create(*args):
  flkLst = cmds.ls(objName)
  if len(flkLst) > 0:
    cmds.delete(flkLst)

  mainBranches = cmds.intSliderGrp(d_mainBranchSlider, q=True, value=True)
  subdiv = cmds.intSliderGrp(d_numSubdvSlider, q=True, value=True)

  cmds.polyCylinder(n=objName, sa=mainBranches, h=height, r=radius)
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(mainBranches-1), kft=False, 
                        lt=(0,0,length), ls=(scale,scale,1), d=subdiv)
  
  make_subs()

def random_callback(*pArgs):
  # make sub branch controls random
  for i in range(len(d_allSubControls)):
    _, posiSlider, lenSlider, angleSlider = d_allSubControls[i]
    cmds.floatSliderGrp(posiSlider, e=True, value=random.random())
    cmds.floatSliderGrp(lenSlider, e=True, value=random.random()*lenMax)
    cmds.floatSliderGrp(angleSlider, e=True, value=random.randint(angleMin, angleMax))

  # remake snowflake
  create()

def reset_callback(*pArgs):
  # return UI to default values
  cmds.intSliderGrp(d_mainBranchSlider, e=True, value=mainBranchDefault)
  cmds.intSliderGrp(d_numSubdvSlider, e=True, value=subdivDefault)
  cmds.intSliderGrp(d_numSubBranches, e=True, value=subBranchDefault)

  random_callback()

def create_branch_controls(pLabel, pPosiVal, pLenVal, pAnglVal, enable=True):
  branchLabel = cmds.text(label=pLabel, en=enable)
  posiSlider = cmds.floatSliderGrp(columnAlign= (1,'right'), field=True, min=posiMin, 
                                   max=posiMax, value=pPosiVal, step=posiStep, dc = 'empty')
  cmds.floatSliderGrp(posiSlider,  e=True, dc = partial(create), en=enable)
  lenSlider = cmds.floatSliderGrp(columnAlign= (1,'right'), field=True, min=lenMin, 
                                   max=lenMax, value=pLenVal, step=lenStep, dc = 'empty')
  cmds.floatSliderGrp(lenSlider,  e=True, dc = partial(create), en=enable)
  angleSlider = cmds.floatSliderGrp(columnAlign= (1,'right'), field=True, min=angleMin, 
                                   max=angleMax, value=pAnglVal, step=anglStep, dc = 'empty')
  cmds.floatSliderGrp(angleSlider,  e=True, dc = partial(create), en=enable)

  return (branchLabel, posiSlider, lenSlider, angleSlider)

#-------------Sectored Plates--------------------#
def make_hexes(percntAlongBranch, pRadi):
  p_branches = cmds.intSliderGrp(p_mainBranchSlider, q=True, value=True)
  p_radius = cmds.floatSliderGrp(p_radiusSlider, q=True, value=True)

  hexLen = p_radius
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(p_branches-1), kft=False, 
                        lt=(0,0,hexLen), ls=(pRadi,1,1))
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(p_branches-1), kft=False, 
                        lt=(0,0,hexLen), ls=(1,1,1))
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(p_branches-1), kft=False, 
                        lt=(0,0,hexLen), ls=(0.5,1,0.5))

def create_sectored_plates(*args):
  flkLst = cmds.ls(objName)
  if len(flkLst) > 0:
    cmds.delete(flkLst)

  p_branches = cmds.intSliderGrp(p_mainBranchSlider, q=True, value=True)
  p_radius = cmds.floatSliderGrp(p_radiusSlider, q=True, value=True)
  p_len = cmds.floatSliderGrp(p_lenBranchesSlider, q=True, value=True)

  cmds.polyCylinder(n=objName, sa=p_branches, h=height, r=p_radius)
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(p_branches-1), kft=False, 
                        lt=(0,0,p_len), ls=(1,1,1))
  
  hexLen = 0.03
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(p_branches-1), kft=False, 
                        lt=(0,0,hexLen), ls=(2,1,1))
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(p_branches-1), kft=False, 
                        lt=(0,0,hexLen), ls=(1,1,1))
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(p_branches-1), kft=False, 
                        lt=(0,0,hexLen), ls=(0.5,1,0.5))
  
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(p_branches-1), kft=False, 
                        lt=(0,0,0.05), ls=(1,1,1))

  hexLen = 0.03
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(p_branches-1), kft=False, 
                        lt=(0,0,hexLen), ls=(3,1,1))
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(p_branches-1), kft=False, 
                        lt=(0,0,2*hexLen), ls=(1,1,1))
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(p_branches-1), kft=False, 
                        lt=(0,0,hexLen), ls=(0,1,0))

#-------------UI--------------------#
windowID = "myWindowID"

if cmds.window(windowID, exists=True):
  cmds.deleteUI(windowID)
    
cmds.window(windowID, title='Snowflake Generator', sizeable=False, resizeToFitChildren=True)
tabs = cmds.tabLayout()

#************************Tab 1**************************#
dendrite = cmds.columnLayout(adjustableColumn=True)
cmds.tabLayout(tabs, edit=True, tabLabel=[dendrite, 'Dendrites'])

# branch controls
cmds.separator(h=10, style='none')
d_mainBranchSlider = cmds.intSliderGrp(label='Main Branches', columnAlign= (1,'right'), 
                                  field=True, min=3, max=12, value=mainBranchDefault, 
                                  step=1, dc = partial(create))
d_numSubdvSlider = slider = cmds.intSliderGrp(label='Subdivision', columnAlign= (1,'right'), 
                                  field=True, min=1, max=50, value=subdivDefault, 
                                  step=1, dc = partial(create))
d_numSubBranches = slider = cmds.intSliderGrp(label='Sub-Branches', columnAlign= (1,'right'), 
                                  field=True, min=1, max=7, value=subBranchDefault, 
                                  step=1, dc = partial(create))
cmds.separator(h=5, style='out')

# sub branch controls
cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[(1,130),(2, 150),(3, 150),(4, 150)],
                     adjustableColumn=True)
# headings
cmds.separator(h=5, style='none')
cmds.text(label='position', align='left')
cmds.text(label='length', align='left')
cmds.text(label='angle', align='left')
# branches
d_allSubControls = [
  create_branch_controls('Sub-Branch 1', random.random(), random.random()*lenMax, 
                        random.randint(angleMin, angleMax)),
  create_branch_controls('Sub-Branch 2', random.random(), random.random()*lenMax, 
                        random.randint(angleMin, angleMax)),
  create_branch_controls('Sub-Branch 3', random.random(), random.random()*lenMax, 
                        random.randint(angleMin, angleMax)),
  create_branch_controls('Sub-Branch 4', random.random(), random.random()*lenMax, 
                        random.randint(angleMin, angleMax), False),
  create_branch_controls('Sub-Branch 5', random.random(), random.random()*lenMax, 
                        random.randint(angleMin, angleMax), False),
  create_branch_controls('Sub-Branch 6', random.random(), random.random()*lenMax, 
                        random.randint(angleMin, angleMax), False),
  create_branch_controls('Sub-Branch 7', random.random(), random.random()*lenMax, 
                        random.randint(angleMin, angleMax), False)
]

#buttons
cmds.separator(h=10, style='none')
cmds.setParent('..')
cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[(1,400),(2, 75), (3, 10), (4,75)])
cmds.separator(h=5, style='none')
cmds.button(label='Random', command=partial(random_callback))
cmds.separator(h=5, style='none')
cmds.button(label='Reset', command=partial(reset_callback, windowID))
cmds.separator(h=5, style='none')

#************************Tab 2**************************#
cmds.setParent('..')
cmds.setParent('..')
plates = cmds.columnLayout(adjustableColumn=True)
cmds.tabLayout(tabs, edit=True, tabLabel=[(plates, 'Plates')])

cmds.separator(h=10, style='none')
p_mainBranchSlider = cmds.intSliderGrp(label='Main Branches', columnAlign= (1,'right'), 
                                  field=True, min=3, max=12, value=mainBranchDefault, 
                                  step=1, dc = partial(create_sectored_plates))
p_radiusSlider = cmds.floatSliderGrp(label='Radius', columnAlign= (1,'right'), 
                                  field=True, min=0.01, max=1, value=radius, 
                                  step=0.01, dc = partial(create_sectored_plates))
p_lenBranchesSlider = cmds.floatSliderGrp(label='Branch Length', columnAlign= (1,'right'), 
                                  field=True, min=0.01, max=1, value=p_lenDefault, 
                                  step=0.01, dc = partial(create_sectored_plates))
p_numHexSlider = cmds.intSliderGrp(label='Hexagons', columnAlign= (1,'right'), 
                                  field=True, min=1, max=7, value=subBranchDefault, 
                                  step=1, dc = partial(create_sectored_plates))
cmds.separator(h=5, style='out')

# sub hexagon controls
cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[(1,130),(2, 150),(3, 150),(4, 150)],
                     adjustableColumn=True)
# headings
cmds.separator(h=5, style='none')
cmds.text(label='position', align='left')
cmds.text(label='radius', align='left')
cmds.text(label='length', align='left')
# branches
p_allSubControls = [
  create_branch_controls('Hexagon 1', random.random(), random.random()*lenMax, 
                        random.randint(angleMin, angleMax)),
  create_branch_controls('Hexagon 2', random.random(), random.random()*lenMax, 
                        random.randint(angleMin, angleMax)),
  create_branch_controls('Hexagon 3', random.random(), random.random()*lenMax, 
                        random.randint(angleMin, angleMax)),
  create_branch_controls('Hexagon 4', random.random(), random.random()*lenMax, 
                        random.randint(angleMin, angleMax), False),
  create_branch_controls('Hexagon 5', random.random(), random.random()*lenMax, 
                        random.randint(angleMin, angleMax), False),
  create_branch_controls('Hexagon 6', random.random(), random.random()*lenMax, 
                        random.randint(angleMin, angleMax), False),
  create_branch_controls('Hexagon 7', random.random(), random.random()*lenMax, 
                        random.randint(angleMin, angleMax), False)
]

#buttons
cmds.separator(h=10, style='none')
cmds.setParent('..')
cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[(1,400),(2, 75), (3, 10), (4,75)])
cmds.separator(h=5, style='none')
cmds.button(label='Random', command=partial(random_callback))
cmds.separator(h=5, style='none')
cmds.button(label='Reset', command=partial(reset_callback, windowID))
cmds.separator(h=5, style='none')

cmds.showWindow()
  
#-----------------Main----------------------#
create()
# create_sectored_plates()