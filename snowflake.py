import maya.cmds as cmds
from functools import partial
import math
import random




#-------------Global Variables--------------------#
objName = "snowflake"
heightDef = 0.025
radiusDef = 0.05
lengthDef = 0.5
scaleDef = 0.1
subScaleDef = (.1,.1,.1)

mainBranchDef = 6
subdivDef = 20
subBranchDef = subHexDef = 3
p_lenDef = 0.01

posiMin = angleMin = 0
lenMin = 0.01
posiMax = 1
lenMax = 0.5
angleMax = 180
posiStep = lenStep = 0.01
anglStep = 0.1
p_radiusMax = 20

#-------------Helper Functions--------------------#
def delete_old():
  """deletes any old instances of the snowflake"""
  flkLst = cmds.ls(objName)
  if len(flkLst) > 0:
    cmds.delete(flkLst)

def enable_subControls(pLabelControl, pListControls, pBool):
  cmds.text(pLabelControl, e=True, en=pBool)
  for cntrl in pListControls:
    cmds.floatSliderGrp(cntrl, e=True, en=pBool)

#-------------Dendrite Functions--------------------#
def ws_center(pObj):
  bbx = cmds.xform(pObj, q=True, bb=True, ws=True)
  centerX = (bbx[0] + bbx[3]) / 2.0
  centerY = (bbx[1] + bbx[4]) / 2.0
  centerZ = (bbx[2] + bbx[5]) / 2.0
  return (centerX, centerY, centerZ)

def make_sub_branch(percntAlongBranch, pLclScl, pLength, pAngle):
  mainBranches = cmds.intSliderGrp(d_mainBranchSlider, q=True, v=True)
  subdiv = cmds.intSliderGrp(d_numSubdvSlider, q=True, v=True)
  lx = pLength*math.cos(pAngle*math.pi/180)
  lz = pLength*math.sin(pAngle*math.pi/180)
  
  startFace = int(percntAlongBranch*(subdiv-1)) + (mainBranches+2+subdiv)
  for i in range(startFace, startFace+(subdiv*2)*(mainBranches*2), subdiv*2):
    if mainBranches%2==1:
      # if coord of face in -x, change lclDir so branches point right way
      if ws_center(objName+'.f[%s]' %i)[0] < 0:
        lclDir = (-1,0,0)
      else:
        lclDir = (1,0,0)
    else:
      # if even number of branches, based on z-axis instead
      if ws_center(objName+'.f[%s]' %i)[2] < 0:
        lclDir = (0,0,-1)
      else:
        lclDir = (0,0,1)

    cmds.polyExtrudeFacet(objName+'.f[%s]' %i, ld=lclDir, lt=(lx, 0, lz), ls=pLclScl)

def make_subs():
  numSub = cmds.intSliderGrp(d_numSubBranches, q=True, v=True)
  for i in range(len(d_allSubControls)):
    subLabel, posiSlider, lenSlider, angleSlider = d_allSubControls[i]
    if i < numSub:
      posi = cmds.floatSliderGrp(posiSlider, q=True, v=True)
      length = cmds.floatSliderGrp(lenSlider, q=True, v=True)
      angle = cmds.floatSliderGrp(angleSlider, q=True, v=True)
      make_sub_branch(posi, subScaleDef, length, angle)
      # enable controls
      enable_subControls(subLabel, [posiSlider, lenSlider, angleSlider], True)
    else:
      #disenable controls
      enable_subControls(subLabel, [posiSlider, lenSlider, angleSlider], False)

def create_dendrite(pSubIndex=0, *pArgs):
  delete_old()
  mainBranches = cmds.intSliderGrp(d_mainBranchSlider, q=True, v=True)
  radii = cmds.floatSliderGrp(d_radiusSlider, q=True, v=True)
  subdiv = cmds.intSliderGrp(d_numSubdvSlider, q=True, v=True)

  scaleFactor = radii/radiusDef
  cmds.polyCylinder(n=objName, sa=mainBranches, h=heightDef*scaleFactor, r=radii)
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(mainBranches-1), 
                        kft=False, 
                        lt=(0,0,lengthDef*scaleFactor), 
                        ls=(scaleDef,scaleDef,1), 
                        d=subdiv)
  # make sub branches
  make_subs()
  # select object and faces being manipulated
  startFace = mainBranches+2+subdiv*mainBranches*4 + (pSubIndex-1)*mainBranches*8
  endFace = startFace + mainBranches*8
  if pSubIndex == 0:
    sel = objName
  else:
    sel = [objName, objName+'.f[%s:%s]'%(startFace+1, endFace-1)]
  cmds.select(sel)

def d_random_callback(*pArgs):
  """make sub branch controls random"""
  for i in range(len(d_allSubControls)):
    _, posiSlider, lenSlider, angleSlider = d_allSubControls[i]
    cmds.floatSliderGrp(posiSlider, e=True, v=random.random())
    cmds.floatSliderGrp(lenSlider, e=True, v=random.random()*lenMax)
    cmds.floatSliderGrp(angleSlider, e=True, v=random.randint(angleMin, angleMax))

  # remake snowflake
  create_dendrite()

def d_reset_callback(*pArgs):
  # return UI to default values
  cmds.intSliderGrp(d_mainBranchSlider, e=True, v=mainBranchDef)
  cmds.floatSliderGrp(d_radiusSlider, e=True, v=radiusDef)
  cmds.intSliderGrp(d_numSubdvSlider, e=True, v=subdivDef)
  cmds.intSliderGrp(d_numSubBranches, e=True, v=subBranchDef)

  create_dendrite()

def create_branch_controls(pIndex, pLabel, pPosiVal, pLenVal, pAnglVal, pEnable=True):
  branchLabel = cmds.text(l=pLabel, en=pEnable)
  posiSlider = cmds.floatSliderGrp(columnAlign=(1,'right'),
                                   f=True, 
                                   min=posiMin, 
                                   max=posiMax, 
                                   v=pPosiVal, 
                                   step=posiStep, 
                                   dc=partial(create_dendrite, pIndex), 
                                   en=pEnable)
  lenSlider = cmds.floatSliderGrp(columnAlign=(1,'right'), 
                                  f=True, 
                                  min=lenMin, 
                                  max=lenMax, 
                                  v=pLenVal, 
                                  step=lenStep, 
                                  dc=partial(create_dendrite, pIndex), 
                                  en=pEnable)
  angleSlider = cmds.floatSliderGrp(columnAlign=(1,'right'), 
                                    f=True, 
                                    min=angleMin, 
                                    max=angleMax, 
                                    v=pAnglVal, 
                                    step=anglStep, 
                                    dc=partial(create_dendrite, pIndex), 
                                    en=pEnable)

  return (branchLabel, posiSlider, lenSlider, angleSlider)

#-------------Plates Functions--------------------#
def hex_extrude_helper(pFace, pLen, pBranches, pLclScl, pLclDir):
  if pFace-1 >=0:
      cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(pFace-1), 
                            kft=False, 
                            lt=(0,0,pLen), 
                            ls=pLclScl)
  cmds.polyExtrudeFacet(objName + '.f[%s]' %(pFace), 
                        kft=False, 
                        lt=(0,0,pLen), 
                        ld=pLclDir, 
                        ls=pLclScl)
  cmds.polyExtrudeFacet(objName + '.f[%s:%s]' %(pFace+1, pBranches-1), 
                        kft=False, 
                        lt=(0,0,pLen), 
                        ls=pLclScl)

def make_hexes_helper(pHexList, pBranches, pBranchLen, pNumHex):
  """extrude the main branch and hexagons"""
  for i in range(pNumHex):
    posi, hexRadius, hexLen = pHexList[i]
    # extrude main branch between hexagons
    if i == 0:
      lclT = (0,0,posi*pBranchLen)
    else:
      old_posi, _, _ = pHexList[i-1]
      lclT = (0,0,(posi-old_posi)*pBranchLen)
    cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(pBranches-1), 
                          kft=False, 
                          lt=lclT, 
                          ls=(1,1,1))
    # make sure hexagons extrude in right direction
    if pBranches%2==1:
      lclDir = (0,0,1)
    else:
      lclDir = (1,0,0)
    faceToChange = int(pBranches/2)-1
    # extrude beginning of hexagon
    hex_extrude_helper(faceToChange, hexLen, pBranches, (hexRadius, 1, 1), lclDir)
    # extrude middle of hexagon
    cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(pBranches-1), 
                          kft=False, 
                          lt=(0,0,hexLen), 
                          ls=(1,1,1))
    # if hexagon at end of branch, make it pointy
    if i==pNumHex-1 and posi==1:
      lclScl = (0, 1, 1)
    else:
      lclScl = (1/hexRadius, 1, 1)
    # extrude end of hexagon
    hex_extrude_helper(faceToChange, hexLen, pBranches, lclScl, lclDir)

  # extrude rest of main branch if needed
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(pBranches-1), 
                        kft=False, 
                        lt=(0,0,(1-posi)*pBranchLen), 
                        ls=(1,1,1))
  
def make_hexes(pIndex):
  p_branches = cmds.intSliderGrp(p_mainBranchSlider, q=True, v=True)
  p_branchLen = cmds.floatSliderGrp(p_lenBranchesSlider, q=True, v=True)
  numHex = cmds.intSliderGrp(p_numHexSlider, q=True, v=True)

  hexInfo = []
  for i in range(len(p_allSubControls)):
    subLabel, posiSlider, radiusSlider, lenSlider = p_allSubControls[i]
    if i < numHex:
      posi = cmds.floatSliderGrp(posiSlider, q=True, v=True)
      radius = cmds.floatSliderGrp(radiusSlider, q=True, v=True)
      length = cmds.floatSliderGrp(lenSlider, q=True, v=True)
      hexInfo.append((posi, radius, length))
      # enable controls
      enable_subControls(subLabel, [posiSlider, radiusSlider, lenSlider], True)
    else:
      #disenable controls
      enable_subControls(subLabel, [posiSlider, radiusSlider, lenSlider], False)

  # extrude the main branch and hexagons
  hexInfo.sort(key=lambda x:x[0])
  make_hexes_helper(hexInfo, p_branches, p_branchLen, numHex)

  # select object and faces being manipulated
  if pIndex == 0:
    sel = objName
  else:
    indexPosi = cmds.floatSliderGrp(p_allSubControls[pIndex-1][1], q=True, v=True)
    indexRadi = cmds.floatSliderGrp(p_allSubControls[pIndex-1][2], q=True, v=True)
    indexLen = cmds.floatSliderGrp(p_allSubControls[pIndex-1][3], q=True, v=True)
    sortedIndex = hexInfo.index((indexPosi, indexRadi, indexLen))
    startFace = p_branches+2+p_branches*4 + sortedIndex*p_branches*16
    endFace = startFace + p_branches*12
    sel = [objName, objName+'.f[%s:%s]'%(startFace, endFace-1)]
  cmds.select(sel)

def create_plate(pHexIndex=0, *pArgs):
  delete_old()
  p_branches = cmds.intSliderGrp(p_mainBranchSlider, q=True, v=True)
  p_radius = cmds.floatSliderGrp(p_radiusSlider, q=True, v=True)

  cmds.polyCylinder(n=objName, sa=p_branches, h=heightDef, r=p_radius)
  make_hexes(pHexIndex)

def p_random_callback(*pArgs):
  # make sub hexagon controls random
  for i in range(len(p_allSubControls)):
    _, posiSlider, radiusSlider, lenSlider = p_allSubControls[i]
    cmds.floatSliderGrp(posiSlider, e=True, v=random.random())
    cmds.floatSliderGrp(radiusSlider, e=True, v=random.random()*p_radiusMax)
    cmds.floatSliderGrp(lenSlider, e=True, v=random.random()*lenMax)

  # remake snowflake
  create_plate()

def p_reset_callback(*pArgs):
  # return UI to default values
  cmds.intSliderGrp(p_mainBranchSlider, e=True, v=mainBranchDef)
  cmds.floatSliderGrp(p_radiusSlider, e=True, v=radiusDef)
  cmds.floatSliderGrp(p_lenBranchesSlider, e=True, v=p_lenDef)
  cmds.intSliderGrp(p_numHexSlider, e=True, v=subBranchDef)

  create_plate()

def create_hex_controls(pIndex, pLabel, pPosiVal, pRadiVal, pLenVal, pEnable=True):
  branchLabel = cmds.text(l=pLabel, en=pEnable)
  posiSlider = cmds.floatSliderGrp(columnAlign= (1,'right'), 
                                   field=True, 
                                   min=posiMin, 
                                   max=posiMax, 
                                   v=pPosiVal, 
                                   step=posiStep, 
                                   dc=partial(create_plate, pIndex), 
                                   en=pEnable)
  radiSlider = cmds.floatSliderGrp(columnAlign= (1,'right'), 
                                   field=True, 
                                   min=0.1, 
                                   max=p_radiusMax, 
                                   v=pRadiVal, 
                                   step=lenStep, 
                                   dc=partial(create_plate, pIndex), 
                                   en=pEnable)
  lenSlider = cmds.floatSliderGrp(columnAlign= (1,'right'), 
                                  field=True, 
                                  min=lenMin, 
                                  max=lenMax, 
                                  v=pLenVal, 
                                  step=lenStep, 
                                  dc=partial(create_plate, pIndex), 
                                  en=pEnable)

  return (branchLabel, posiSlider, radiSlider, lenSlider)

#-------------UI--------------------#
windowID = "myWindowID"

if cmds.window(windowID, exists=True):
  cmds.deleteUI(windowID)
    
cmds.window(windowID, title='Simple Snowflake Generator', sizeable=False, resizeToFitChildren=True)
tabs = cmds.tabLayout()

#************************Dendrites Tab**************************#
dendrite = cmds.rowColumnLayout(adjustableColumn=True)
cmds.tabLayout(tabs, e=True, tabLabel=[dendrite, 'Dendrites'])

# branch controls
cmds.separator(h=10, style='none')
d_mainBranchSlider = cmds.intSliderGrp(l='Main Branches', 
                                       columnAlign= (1,'right'), 
                                       field=True, 
                                       min=3, 
                                       max=12, 
                                       v=mainBranchDef, 
                                       step=1, 
                                       dc=partial(create_dendrite, 0))
d_radiusSlider = cmds.floatSliderGrp(l='Radius', 
                                     columnAlign= (1,'right'), 
                                     field=True, 
                                     min=0.01, 
                                     max=1, 
                                     v=radiusDef, 
                                     step=0.01, 
                                     dc=partial(create_dendrite, 0))
d_numSubdvSlider = cmds.intSliderGrp(l='Subdivision', 
                                     columnAlign= (1,'right'), 
                                     field=True, 
                                     min=1, 
                                     max=50, 
                                     v=subdivDef, 
                                     step=1, 
                                     dc=partial(create_dendrite, 0))
d_numSubBranches = cmds.intSliderGrp(label='Sub-Branches', 
                                     columnAlign= (1,'right'), 
                                     field=True, 
                                     min=1, 
                                     max=7, 
                                     v=subBranchDef, 
                                     step=1, 
                                     dc=partial(create_dendrite, 0))
cmds.separator(h=5, style='out')

# sub branch controls
cmds.rowColumnLayout(numberOfColumns=4, 
                     columnWidth=[(1,130),(2, 150),(3, 150),(4, 150)],
                     adjustableColumn=True)
# headings
cmds.separator(h=5, style='none')
cmds.text(l='position', align='left')
cmds.text(l='length', align='left')
cmds.text(l='angle', align='left')
# branches
d_allSubControls = [
  create_branch_controls(1,
                         'Sub-Branch 1', 
                         random.random(), 
                         random.random()*lenMax, 
                         random.randint(angleMin, angleMax)),
  create_branch_controls(2,
                         'Sub-Branch 2', 
                         random.random(), 
                         random.random()*lenMax, 
                         random.randint(angleMin, angleMax)),
  create_branch_controls(3,
                         'Sub-Branch 3', 
                         random.random(), 
                         random.random()*lenMax, 
                         random.randint(angleMin, angleMax)),
  create_branch_controls(4,
                         'Sub-Branch 4', 
                         random.random(), 
                         random.random()*lenMax, 
                         random.randint(angleMin, angleMax), 
                         False),
  create_branch_controls(5,
                         'Sub-Branch 5', 
                         random.random(), 
                         random.random()*lenMax, 
                         random.randint(angleMin, angleMax), 
                         False),
  create_branch_controls(6,
                         'Sub-Branch 6', 
                         random.random(), 
                         random.random()*lenMax, 
                         random.randint(angleMin, angleMax), 
                         False),
  create_branch_controls(7,
                         'Sub-Branch 7', 
                         random.random(), 
                         random.random()*lenMax, 
                         random.randint(angleMin, angleMax), 
                         False)
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
cmds.tabLayout(tabs, e=True, tabLabel=[(plates, 'Plates')])

cmds.separator(h=10, style='none')
p_mainBranchSlider = cmds.intSliderGrp(l='Main Branches', 
                                       columnAlign=(1,'right'), 
                                       field=True, 
                                       min=3, 
                                       max=12, 
                                       v=mainBranchDef, 
                                       step=1, 
                                       dc=partial(create_plate, 0))
p_radiusSlider = cmds.floatSliderGrp(l='Radius', 
                                     columnAlign=(1,'right'), 
                                     field=True, 
                                     min=0.01, 
                                     max=1, 
                                     v=radiusDef, 
                                     step=0.01, 
                                     dc=partial(create_plate, 0))
p_lenBranchesSlider = cmds.floatSliderGrp(l='Branch Length', 
                                          columnAlign=(1,'right'), 
                                          field=True, 
                                          min=0.01, 
                                          max=1, 
                                          v=p_lenDef, 
                                          step=0.01, 
                                          dc=partial(create_plate, 0))
p_numHexSlider = cmds.intSliderGrp(label='Hexagons', 
                                   columnAlign=(1,'right'), 
                                   field=True, 
                                   min=1, 
                                   max=7, 
                                   v=subHexDef, 
                                   step=1, 
                                   dc=partial(create_plate, 0))
cmds.separator(h=5, style='out')

# sub hexagon controls
cmds.rowColumnLayout(numberOfColumns=4, 
                     columnWidth=[(1,130),(2, 150),(3, 150),(4, 150)],
                     adjustableColumn=True)
# headings
cmds.separator(h=5, style='none')
cmds.text(label='position', align='left')
cmds.text(label='radius', align='left')
cmds.text(label='length', align='left')
# branches
p_allSubControls = [
  create_hex_controls(1,
                      'Hexagon 1', 
                      random.random(), 
                      random.random()*p_radiusMax, 
                      random.random()*lenMax),
  create_hex_controls(2,
                      'Hexagon 2', 
                      random.random(), 
                      random.random()*p_radiusMax, 
                      random.random()*lenMax),
  create_hex_controls(3,
                      'Hexagon 3', 
                      random.random(), 
                      random.random()*p_radiusMax, 
                      random.random()*lenMax),
  create_hex_controls(4,
                      'Hexagon 4', 
                      random.random(), 
                      random.random()*p_radiusMax, 
                      random.random()*lenMax, 
                      False),
  create_hex_controls(5,
                      'Hexagon 5', 
                      random.random(), 
                      random.random()*p_radiusMax, 
                      random.random()*lenMax, 
                      False),
  create_hex_controls(6,
                      'Hexagon 6', 
                      random.random(), 
                      random.random()*p_radiusMax, 
                      random.random()*lenMax, 
                      False),
  create_hex_controls(7,
                      'Hexagon 7',
                      random.random(), 
                      random.random()*p_radiusMax, 
                      random.random()*lenMax, 
                      False)
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
create_dendrite()