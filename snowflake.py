import maya.cmds as cmds

objName = "snowflake"

flkLst = cmds.ls(objName)
if len(flkLst) > 0:
  cmds.delete(flkLst)

# snowflakeGrp = cmds.group(name='snowflake', empty=True)
# for i in range(3):
#   cubeName = cmds.polyCube(w=5, h=0.1, d=0.2, name='snowflk#')[0]
#   cmds.rotate(0, i*60, 0, cubeName)
#   cmds.parent(cubeName, snowflakeGrp)

cmds.polyCylinder(n=objName, sa=6, h=0.1, r=0.2)
cmds.polyExtrudeFacet(objName + '.f[0:5]', kft=False, lt=(0,0,2), ls=(0.1,0.1,1))

# cmds.select(objName + '.e[14:25]')
# cmds.polyBevel(objName + '.e[14:25]')

# cmds.polyCut(objName + '.f[0]', cd='X')
# cmds.select(objName + '.e[14:25]')
# cmds.polySplitRing()

for j in range(3):
  for i in range(9, 32, 2):
    # cmds.polySubdivideFacet(objName+'.f[%s]' %i, dv=5)
    cmds.polyCut(objName+'.f[%s]' %i, cd='X')
  for k in range(32, 32+j*12):
    cmds.polyCut(objName+'.f[%s]' %k, cd='X')

# cmds.select(objName + '.e[14:25]')
# cmds.polySubdivideEdge(dv=4)

cmds.select(objName)