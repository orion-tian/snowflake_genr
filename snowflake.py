import maya.cmds as cmds

flkLst = cmds.ls("snowflake")
if len(flkLst) > 0:
  cmds.delete(flkLst)

snowflakeGrp = cmds.group(name='snowflake', empty=True)
for i in range(3):
  cubeName = cmds.polyCube(w=5, h=0.1, d=0.2, name='snowflk#')[0]
  cmds.rotate(0, i*60, 0, cubeName)
  cmds.parent(cubeName, snowflakeGrp)