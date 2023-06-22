import maya.cmds as cmds

objName = "snowflake"

flkLst = cmds.ls(objName)
if len(flkLst) > 0:
  cmds.delete(flkLst)

obj = cmds.polyCylinder(n=objName, sa=6, h=0.1, r=0.2)
cmds.polyExtrudeFacet(objName + '.f[0:5]', kft=False, lt=(0,0,2), ls=(0.1,0.1,1))

for j in range(5):
  numFaces = cmds.polyEvaluate(objName, f=True)
  for i in range(9, 32, 2):
    cmds.polyCut(objName+'.f[%s]' %i, cd='X')
  for k in range(32, numFaces):
    print(k)
    cmds.polyCut(objName+'.f[%s]' %k, cd='X')

cmds.select(objName)