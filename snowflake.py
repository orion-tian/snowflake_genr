import maya.cmds as cmds
from functools import partial

objName = "snowflake"
mainBranchDefault = 6
subdivDefault = 30
height = 0.1
radius = 0.2
length = 2
scale = 0.1


def create(*args):
  flkLst = cmds.ls(objName)
  if len(flkLst) > 0:
    cmds.delete(flkLst)

  mainBranches = cmds.intSliderGrp(mainBranchSlider, q=True, value=True)
  subdiv = cmds.intSliderGrp(numSubdvSlider, q=True, value=True)

  cmds.polyCylinder(n=objName, sa=mainBranches, h=height, r=radius)
  cmds.polyExtrudeFacet(objName + '.f[0:%s]' %(mainBranches-1), kft=False, 
                        lt=(0,0,length), ls=(scale,scale,1), d=subdiv)

def resetCallback(pwindID, *pArgs):
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

# for i in range(32, 32+12):
#   cmds.polyExtrudeFacet(objName+'.f[%s]' %i, lt=(.55,0,.5), ls=(0.1,0.1,1))

