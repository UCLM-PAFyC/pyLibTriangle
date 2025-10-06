import numpy
from plyfile import PlyData, PlyElement

plydata = PlyData.read('tet.ply')
with open('tet.ply', 'rb') as f:
    plydata = PlyData.read(f)
print(plydata.elements[0].name)
print(plydata.elements[0].data[0].tolist())
print(plydata.elements[0].data['x'])
print(plydata['face'].data['vertex_indices'][0])
print(plydata['vertex']['x'])
print(plydata['vertex'][0].tolist())
print(plydata.elements[0].properties)
print(plydata.elements[0].count)
print(plydata.elements[0].ply_property('x'))
# print()
# print()
yo = 1