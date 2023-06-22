import maya.cmds as cmds
from functools import partial
import math
import random

objName = "snowflake"
mainBranchDefault = 6
subdivDefault = 20
height = 0.1
radius = 0.2
length = 2
scale = 0.1

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
                            ls=local_scl, d=subdiv)

def create(*args):
  flkLst = cmds.ls(objName)
  if len(flkLst) > 0:
    cmds.delete(flkLst)

  mainBranches = cmds.intSliderGrp(mainBranchSlider, q=True, value=True)
  subdiv = cmds.intSliderGrp(numSubdvSlider, q=True, value=True)

  cmds.polyCylinder(n=objName, sa=mainBranches, h=height, r=radius)
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(mainBranches-1), kft=False, 
                        lt=(0,0,length), ls=(scale,scale,1), d=subdiv)

def resetCallback(*pArgs):
        # return UI to default values
        cmds.intSliderGrp(mainBranchSlider, e=True, value=mainBranchDefault)
        cmds.intSliderGrp(numSubdvSlider, e=True, value=subdivDefault)

        # remake default snowflake
        create()

#-------------UI--------------------#
windowID = "myWindowID"

if cmds.window(windowID, exists=True):
  cmds.deleteUI(windowID)
    
cmds.window(windowID, title='Snowflake Generator', sizeable=False, resizeToFitChildren=True)
cmds.columnLayout(adjustableColumn=True)

# branch controls
cmds.separator(h=10, style='none')

mainBranchSlider = cmds.intSliderGrp(label='Main Branches', columnAlign= (1,'right'), 
                                field=True, min=3, max=12, value=mainBranchDefault, 
                                step=1, dc = 'empty')
cmds.intSliderGrp(mainBranchSlider,  e=True, dc = partial(create))

numSubdvSlider = cmds.intSliderGrp(label='Subdivisions', columnAlign= (1,'right'), 
                                field=True, min=1, max=100, value=subdivDefault, 
                                step=1, dc = 'empty')
cmds.intSliderGrp(numSubdvSlider,  e=True, dc = partial(create))

#reset button
cmds.separator(h=10, style='none')
cmds.button(label='Reset', command=partial(resetCallback, windowID))

cmds.showWindow()
  
#-----------------Operations----------------------#
create()
cmds.select(objName)

ls = (.1,.1,.1)

make_sub_branches(0.25, ls, 0.5, 90)
make_sub_branches(0.5, ls, 1, 85)
make_sub_branches(0.6, ls, 0.6, 85)
make_sub_branches(0.75, ls, 0.7, 60)
make_sub_branches(0.85, ls, 0.8, 60)
make_sub_branches(0.95, ls, 0.9, 60)




