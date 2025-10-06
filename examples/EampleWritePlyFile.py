import os
import numpy
from plyfile import PlyData, PlyElement
from tempfile import NamedTemporaryFile

vertex = numpy.array([(0, 0, 0),
                      (0, 1, 1),
                      (1, 0, 1),
                      (1, 1, 0)],
                     dtype=[('x', 'f4'), ('y', 'f4'),
                            ('z', 'f4')])
face = numpy.array([([0, 1, 2], 255, 255, 255),
                    ([0, 2, 3], 255,   0,   0),
                    ([0, 1, 3],   0, 255,   0),
                    ([1, 2, 3],   0,   0, 255)],
                   dtype=[('vertex_indices', 'i4', (3,)),
                          ('red', 'u1'), ('green', 'u1'),
                          ('blue', 'u1')])
el_v = PlyElement.describe(vertex, 'vertex')
# el = PlyElement.describe(vertex, 'vertex',
#                          comments=['comment1',
#                                    'comment2'])
el_f = PlyElement.describe(face, 'face',
                         val_types={'vertex_indices': 'u2'},
                         len_types={'vertex_indices': 'u4'})
# PlyData([el]).write('some_binary.ply')
f = NamedTemporaryFile(mode='w+', delete=False)
# f.write("there is a lot of blah blah in this so-called file")
# f.close()
# with open(f.name, "r") as new_f:
#     yo = new_f.read()
# os.unlink(f.name)
PlyData([el_v, el_f], text=True).write(f)
f.close()
with open(f.name, "r") as new_f:
    ply_content = new_f.read()
os.unlink(f.name)
PlyData([el_v, el_f], text=True).write('some_ascii.ply')

# Force the byte order of the output to big-endian, independently of
# the machine's native byte order
# PlyData([el],
#         byte_order='>').write('some_big_endian_binary.ply')

# Use a file object. Binary mode is used here, which will cause
# Unix-style line endings to be written on all systems.
# with open('some_ascii.ply', mode='wb') as f:
#     PlyData([el], text=True).write(f)

# ply = PlyData([el], comments=['header comment'])
# print(ply.comments)
# ply = PlyData([el], obj_info=['obj_info1', 'obj_info2'])
# print(ply.obj_info)
yo = 1