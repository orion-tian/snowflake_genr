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
subBranchDefault = subHexDefault = 3
p_lenDefault = 0.01

posiMin = lenMin = angleMin = 0
posiMax = 1
lenMax = 0.5
angleMax = 180
posiStep = lenStep = 0.01
anglStep = 0.1
p_radiusMax = 20

#-------------Helper Functions--------------------#
def delete():
  """deletes any old instances of the snowflake"""
  flkLst = cmds.ls(objName)
  if len(flkLst) > 0:
    cmds.delete(flkLst)

#-------------Dendrite Functions--------------------#
def ws_center(pObj):
  bbx = cmds.xform(pObj, q=True, bb=True, ws=True)
  centerX = (bbx[0] + bbx[3]) / 2.0
  centerY = (bbx[1] + bbx[4]) / 2.0
  centerZ = (bbx[2] + bbx[5]) / 2.0
  return (centerX, centerY, centerZ)

def make_sub_branch(percntAlongBranch, local_scl, len, angle):
  mainBranches = cmds.intSliderGrp(d_mainBranchSlider, q=True, value=True)
  subdiv = cmds.intSliderGrp(d_numSubdvSlider, q=True, value=True)

  lx = len*math.cos(angle*math.pi/180)
  lz = len*math.sin(angle*math.pi/180)
  
  startFace = int(percntAlongBranch*(subdiv-1)) + (mainBranches+2+subdiv)
  for i in range(startFace, startFace+(subdiv*2)*(mainBranches*2), subdiv*2):
    if mainBranches%2==1:
      # if coord of face in -x, change local_dir so branches point right way
      if ws_center(objName+'.f[%s]' %i)[0] < 0:
        local_dir = (-1,0,0)
      else:
        local_dir = (1,0,0)
    else:
      # if even number of branches, based on z-axis instead
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
  delete()
  mainBranches = cmds.intSliderGrp(d_mainBranchSlider, q=True, value=True)
  radii = cmds.floatSliderGrp(d_radiusSlider, q=True, value=True)
  subdiv = cmds.intSliderGrp(d_numSubdvSlider, q=True, value=True)

  scaleFactor = radii/radius

  cmds.polyCylinder(n=objName, sa=mainBranches, h=height*scaleFactor, r=radii)
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(mainBranches-1), kft=False, 
                        lt=(0,0,length*scaleFactor), ls=(scale,scale,1), d=subdiv)
  # make sub branches
  make_subs()

def d_random_callback(*pArgs):
  """make sub branch controls random"""
  for i in range(len(d_allSubControls)):
    _, posiSlider, lenSlider, angleSlider = d_allSubControls[i]
    cmds.floatSliderGrp(posiSlider, e=True, value=random.random())
    cmds.floatSliderGrp(lenSlider, e=True, value=random.random()*lenMax)
    cmds.floatSliderGrp(angleSlider, e=True, value=random.randint(angleMin, angleMax))

  # remake snowflake
  create()

def d_reset_callback(*pArgs):
  # return UI to default values
  cmds.intSliderGrp(d_mainBranchSlider, e=True, value=mainBranchDefault)
  cmds.floatSliderGrp(d_radiusSlider, e=True, value=radius)
  cmds.intSliderGrp(d_numSubdvSlider, e=True, value=subdivDefault)
  cmds.intSliderGrp(d_numSubBranches, e=True, value=subBranchDefault)

  d_random_callback()

def create_branch_controls(pLabel, pPosiVal, pLenVal, pAnglVal, enable=True):
  branchLabel = cmds.text(label=pLabel, en=enable)
  posiSlider = cmds.floatSliderGrp(columnAlign= (1,'right'), field=True, min=posiMin, 
                                   max=posiMax, value=pPosiVal, step=posiStep, 
                                   dc = partial(create), en=enable)
  lenSlider = cmds.floatSliderGrp(columnAlign= (1,'right'), field=True, min=lenMin, 
                                   max=lenMax, value=pLenVal, step=lenStep, 
                                   dc = partial(create), en=enable)
  angleSlider = cmds.floatSliderGrp(columnAlign= (1,'right'), field=True, min=angleMin, 
                                   max=angleMax, value=pAnglVal, step=anglStep, 
                                   dc = partial(create), en=enable)

  return (branchLabel, posiSlider, lenSlider, angleSlider)

#-------------Plates Functions--------------------#
def make_hexes():
  p_branches = cmds.intSliderGrp(p_mainBranchSlider, q=True, value=True)
  p_branchLen = cmds.floatSliderGrp(p_lenBranchesSlider, q=True, value=True)
  numHex = cmds.intSliderGrp(p_numHexSlider, q=True, value=True)

  hex_info = []
  for i in range(len(p_allSubControls)):
    subLabel, posiSlider, radiusSlider, lenSlider = p_allSubControls[i]
    if i < numHex:
      posi = cmds.floatSliderGrp(posiSlider, q=True, value=True)
      radius = cmds.floatSliderGrp(radiusSlider, q=True, value=True)
      length = cmds.floatSliderGrp(lenSlider, q=True, value=True)
      hex_info.append((posi, radius, length))
      # enable controls
      cmds.text(subLabel, e=True, enable=True)
      cmds.floatSliderGrp(posiSlider, e=True, enable=True)
      cmds.floatSliderGrp(lenSlider, e=True, enable=True)
      cmds.floatSliderGrp(radiusSlider, e=True, enable=True)
    else:
      #disenable controls
      cmds.text(subLabel, e=True, enable=False)
      cmds.floatSliderGrp(posiSlider, e=True, enable=False)
      cmds.floatSliderGrp(lenSlider, e=True, enable=False)
      cmds.floatSliderGrp(radiusSlider, e=True, enable=False)

  # extrude the main branch and hexagons
  hex_info.sort(key=lambda x:x[0])
  for i in range(numHex):
    posi, radius, hexLen = hex_info[i]
    if i == 0:
      cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(p_branches-1), kft=False, 
                        lt=(0,0,posi*p_branchLen), ls=(1,1,1))
    else:
      old_posi, _, _ = hex_info[i-1]
      cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(p_branches-1), kft=False, 
                        lt=(0,0,(posi-old_posi)*p_branchLen), ls=(1,1,1))
    
    if p_branches%2==1:
      lcl_d = (0,0,1)
    else:
      lcl_d = (1,0,0)
    faceToChange = int(p_branches/2)-1
    if faceToChange-1 >=0:
      cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(faceToChange-1), kft=False, 
                            lt=(0,0,hexLen), ls=(radius,1,1))
    cmds.polyExtrudeFacet(objName + '.f[%s]' %(faceToChange), kft=False, 
                          lt=(0,0,hexLen), ld=lcl_d, ls=(radius,1,1))
    cmds.polyExtrudeFacet(objName + '.f[%s:%s]' %(faceToChange+1, p_branches-1), 
                          kft=False, lt=(0,0,hexLen), ls=(radius,1,1))
    cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(p_branches-1), kft=False, 
                          lt=(0,0,hexLen), ls=(1,1,1))
    
    if i==numHex-1 and posi==1:
      lcl_scl_2 = (0, 1, 1)
    else:
      lcl_scl_2 = (1/radius, 1, 1)
    if faceToChange-1 >=0:
      cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(faceToChange-1), kft=False, 
                            lt=(0,0,hexLen), ls=lcl_scl_2)
    cmds.polyExtrudeFacet(objName + '.f[%s]' %(faceToChange), kft=False, 
                          lt=(0,0,hexLen), ld=lcl_d, ls=lcl_scl_2)
    cmds.polyExtrudeFacet(objName + '.f[%s:%s]' %(faceToChange+1, p_branches-1), 
                          kft=False, lt=(0,0,hexLen), ls=lcl_scl_2)
    # cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(p_branches-1), kft=False, 
    #                       lt=(0,0,hexLen), ls=lcl_scl_2)
    
    # cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(p_branches-1), kft=False, 
    #                       lt=(0,0,hexLen), ls=lcl_scl_2)
  
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(p_branches-1), kft=False, 
                        lt=(0,0,(1-posi)*p_branchLen), ls=(1,1,1))

def create_plates(*args):
  delete()
  p_branches = cmds.intSliderGrp(p_mainBranchSlider, q=True, value=True)
  p_radius = cmds.floatSliderGrp(p_radiusSlider, q=True, value=True)

  cmds.polyCylinder(n=objName, sa=p_branches, h=height, r=p_radius)
  make_hexes()

def p_random_callback(*pArgs):
  # make sub hexagon controls random
  for i in range(len(p_allSubControls)):
    _, posiSlider, radiusSlider, lenSlider = p_allSubControls[i]
    cmds.floatSliderGrp(posiSlider, e=True, value=random.random())
    cmds.floatSliderGrp(radiusSlider, e=True, value=random.random()*p_radiusMax)
    cmds.floatSliderGrp(lenSlider, e=True, value=random.random()*lenMax)

  # remake snowflake
  create_plates()

def p_reset_callback(*pArgs):
  # return UI to default values
  cmds.intSliderGrp(p_mainBranchSlider, e=True, value=mainBranchDefault)
  cmds.floatSliderGrp(p_radiusSlider, e=True, value=radius)
  cmds.floatSliderGrp(p_lenBranchesSlider, e=True, value=p_lenDefault)
  cmds.intSliderGrp(p_numHexSlider, e=True, value=subBranchDefault)

  p_random_callback()

def create_hex_controls(pLabel, pPosiVal, pRadiVal, pLenVal, enable=True):
  branchLabel = cmds.text(label=pLabel, en=enable)
  posiSlider = cmds.floatSliderGrp(columnAlign= (1,'right'), field=True, min=posiMin, 
                                   max=posiMax, value=pPosiVal, step=posiStep, 
                                   dc = partial(create_plates), en=enable)
  radiSlider = cmds.floatSliderGrp(columnAlign= (1,'right'), field=True, min=0.1, 
                                   max=p_radiusMax, value=pRadiVal, step=lenStep, 
                                   dc = partial(create_plates), en=enable)
  lenSlider = cmds.floatSliderGrp(columnAlign= (1,'right'), field=True, min=lenMin, 
                                   max=lenMax, value=pLenVal, step=lenStep, 
                                   dc = partial(create_plates), en=enable)

  return (branchLabel, posiSlider, radiSlider, lenSlider)

#-------------UI--------------------#
windowID = "myWindowID"

if cmds.window(windowID, exists=True):
  cmds.deleteUI(windowID)
    
cmds.window(windowID, title='Snowflake Generator', sizeable=False, resizeToFitChildren=True)
tabs = cmds.tabLayout()

#************************Dendrites Tab**************************#
dendrite = cmds.columnLayout(adjustableColumn=True)
cmds.tabLayout(tabs, edit=True, tabLabel=[dendrite, 'Dendrites'])

# branch controls
cmds.separator(h=10, style='none')
d_mainBranchSlider = cmds.intSliderGrp(label='Main Branches', cal= (1,'right'), 
                                  field=True, min=3, max=12, value=mainBranchDefault, 
                                  step=1, dc = partial(create))
d_radiusSlider = cmds.floatSliderGrp(label='Radius', cal= (1,'right'), 
                                  field=True, min=0.01, max=1, value=radius, 
                                  step=0.01, dc = partial(create))
d_numSubdvSlider = cmds.intSliderGrp(label='Subdivision', cal= (1,'right'), 
                                  field=True, min=1, max=50, value=subdivDefault, 
                                  step=1, dc = partial(create))
d_numSubBranches = cmds.intSliderGrp(label='Sub-Branches', cal= (1,'right'), 
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
cmds.button(label='Random', command=partial(d_random_callback))
cmds.separator(h=5, style='none')
cmds.button(label='Reset', command=partial(d_reset_callback, windowID))
cmds.separator(h=5, style='none')

#************************Plates Tab**************************#
cmds.setParent('..')
cmds.setParent('..')
plates = cmds.columnLayout(adjustableColumn=True)
cmds.tabLayout(tabs, edit=True, tabLabel=[(plates, 'Plates')])

cmds.separator(h=10, style='none')
p_mainBranchSlider = cmds.intSliderGrp(label='Main Branches', cal= (1,'right'), 
                                  field=True, min=3, max=12, value=mainBranchDefault, 
                                  step=1, dc = partial(create_plates))
p_radiusSlider = cmds.floatSliderGrp(label='Radius', cal= (1,'right'), 
                                  field=True, min=0.01, max=1, value=radius, 
                                  step=0.01, dc = partial(create_plates))
p_lenBranchesSlider = cmds.floatSliderGrp(label='Branch Length', cal= (1,'right'), 
                                  field=True, min=0.01, max=1, value=p_lenDefault, 
                                  step=0.01, dc = partial(create_plates))
p_numHexSlider = cmds.intSliderGrp(label='Hexagons', cal= (1,'right'), 
                                  field=True, min=1, max=7, value=subHexDefault, 
                                  step=1, dc = partial(create_plates))
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
  create_hex_controls('Hexagon 1', random.random(), random.random()*p_radiusMax, 
                        random.random()*lenMax),
  create_hex_controls('Hexagon 2', random.random(), random.random()*p_radiusMax, 
                        random.random()*lenMax),
  create_hex_controls('Hexagon 3', random.random(), random.random()*p_radiusMax, 
                        random.random()*lenMax),
  create_hex_controls('Hexagon 4', random.random(), random.random()*p_radiusMax, 
                        random.random()*lenMax, False),
  create_hex_controls('Hexagon 5', random.random(), random.random()*p_radiusMax, 
                        random.random()*lenMax, False),
  create_hex_controls('Hexagon 6', random.random(), random.random()*p_radiusMax, 
                        random.random()*lenMax, False),
  create_hex_controls('Hexagon 7', random.random(), random.random()*p_radiusMax, 
                        random.random()*lenMax, False)
]

#buttons
cmds.separator(h=10, style='none')
cmds.setParent('..')
cmds.rowColumnLayout(numberOfColumns=4, columnWidth=[(1,400),(2, 75), (3, 10), (4,75)])
cmds.separator(h=5, style='none')
cmds.button(label='Random', command=partial(p_random_callback))
cmds.separator(h=5, style='none')
cmds.button(label='Reset', command=partial(p_reset_callback, windowID))
cmds.separator(h=5, style='none')

cmds.showWindow()
  
#-----------------Main----------------------#
create()