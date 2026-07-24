# authors:
# David Hernandez Lopez, david.hernandez@uclm.es

import os
from tempfile import NamedTemporaryFile
import numpy as np

from plyfile import PlyData, PlyElement
import subprocess
import sys

TRIANGLE_EXTERNAL_TOOL_RELATIVE_PATH = "/external_tools/triangle.exe"
TRIANGLE_EXTERNAL_TOOL_DEFAULT_PARAMETERS = "-p -P -N -Q"

class TriangleTools(object):

    @classmethod
    def export_to_ply_content(self,
                              points,
                              triangles,
                              file_path = None):
        str_error = ''
        ply_content = ''
        if not isinstance(points, list):
            str_error = 'Points object must be a list'
            return str_error, ply_content
        if not isinstance(points[0], list):
            str_error = 'Points object must be a list of lists'
            return str_error, ply_content
        if len(points[0]) != 3:
            str_error = 'Points object must be a list of lists of three coordinates'
            return str_error, ply_content
        if not isinstance(triangles, list):
            str_error = 'Triangles object must be a list'
            return str_error, ply_content
        if not isinstance(triangles[0], list):
            str_error = 'Triangles object must be a list of lists'
            return str_error, ply_content
        if len(triangles[0]) != 3:
            str_error = 'Triangles object must be a list of lists of three coordinates'
            return str_error, ply_content
        points_as_list_of_tuples = []
        for i in range(len(points)):
            points_as_list_of_tuples.append((points[i][0], points[i][1], points[i][2]))
        vertex = np.array(points_as_list_of_tuples, dtype=[('x', np.float64), ('y', np.float64), ('z', np.float64)])
        triangles_as_list_of_tuples = []
        for i in range(len(triangles)):
            triangles_as_list_of_tuples.append(([triangles[i][0], triangles[i][1], triangles[i][2]], 255, 255, 255))
        face = np.array(triangles_as_list_of_tuples, dtype=[('vertex_indices', 'i4', (3,)),
                          ('red', 'u1'), ('green', 'u1'),
                          ('blue', 'u1')])
        el_v = PlyElement.describe(vertex, 'vertex')
        # el = PlyElement.describe(vertex, 'vertex',
        #                          comments=['comment1',
        #                                    'comment2'])
        el_f = PlyElement.describe(face, 'face',
                                   val_types={'vertex_indices': 'u2'},
                                   len_types={'vertex_indices': 'u1'})
        f = NamedTemporaryFile(mode='w+', delete=False)
        PlyData([el_v, el_f], text=True).write(f)
        f.close()
        with open(f.name, "r") as new_f:
            ply_content = new_f.read()
        os.unlink(f.name)
        if not file_path is None:
            try:
                with open(file_path, "w") as f:
                    f.write(ply_content)
            except Exception as e:
                str_error = ('Writing ply file:\n{}\nError:\n{}'.format(file_path, e))
        return str_error, ply_content

    @classmethod
    def create_triangulation(self,
                             points,
                             segments,
                             holes = None):
        str_error = ''
        triangles = None
        dir_path = os.path.dirname(os.path.realpath(__file__))
        triangle_exe_file_path = os.path.join(dir_path + TRIANGLE_EXTERNAL_TOOL_RELATIVE_PATH)
        triangle_exe_file_path = os.path.normpath(triangle_exe_file_path)
        if not os.path.exists(triangle_exe_file_path):
            str_error = ('Not exists tool file:\n{}'.format(triangle_exe_file_path))
            return str_error, triangles
        triangle_parameters = TRIANGLE_EXTERNAL_TOOL_DEFAULT_PARAMETERS
        if not isinstance(points, np.ndarray):
            str_error = 'Points object must be a numpy array'
            return str_error, triangles
        num_points, num_coordinates = points.shape
        if num_coordinates != 2:
            str_error = 'Points must have two coordinates'
            return str_error, triangles
        if not isinstance(segments, np.ndarray):
            str_error = 'Segments object must be a numpy array'
            return str_error, triangles
        num_segments, num_segments_columns = segments.shape
        if num_segments_columns != 2:
            str_error = 'Segments must have two columns'
            return str_error, triangles
        if not holes is None:
            if not isinstance(holes, np.ndarray):
                str_error = 'Edges object must be a numpy array'
                return str_error, triangles
            num_holes, holes_columns = holes.shape
            if holes_columns != 2:
                str_error = 'Holes must have two columns'
                return str_error, triangles
        input_file_path = dir_path + '/tmp/data.poly'
        input_file_path = os.path.normpath(input_file_path)
        try:
            f = open(input_file_path, 'w')
        except:
            str_error = ('Error opening temporal poly file:\n{}'.format(input_file_path))
            return str_error, triangles
        f.write('{} 2 0 0\n'.format(str(len(points))))
        for i in range(len(points)):
            f.write('{} {:.4f} {:.4f} \n'.format(str(i), points[i][0], points[i][1]))
            # f.write('{} {:.4f} {:.4f} \n'.format(str(i+1), points[i][0], points[i][1]))
        f.write('{} 0\n'.format(str(len(segments))))
        for i in range(len(segments)):
            f.write('{} {} {} \n'.format(str(i+1), str(segments[i][0]), str(segments[i][1])))
            # f.write('{} {} {} \n'.format(str(i+1), str(segments[i][0] + 1), str(segments[i][1] + 1)))
        f.write('0\n'.format(str(len(segments))))
        f.close()
        triangle_exe_file_path = os.path.join(dir_path + TRIANGLE_EXTERNAL_TOOL_RELATIVE_PATH)
        triangle_exe_file_path = os.path.normpath(triangle_exe_file_path)
        if not os.path.exists(triangle_exe_file_path):
            str_error = ('Not exists tool file:\n{}'.format(triangle_exe_file_path))
            return str_error, triangles
        triangle_parameters = TRIANGLE_EXTERNAL_TOOL_DEFAULT_PARAMETERS
        triangle_parameters += (" {}".format(input_file_path))
        output_file_path = dir_path + '/tmp/data.1.ele'
        output_file_path = os.path.normpath(output_file_path)
        command = triangle_exe_file_path + ' ' + triangle_parameters
        os.system(command)
        if not os.path.exists(output_file_path):
            str_error = ('Executing triangle tools::\n{}'.format(triangle_exe_file_path))
            str_error += ('\nwith arguments:\n{}'.format(triangle_parameters))
            str_error += ('\nsomething fails')
            return str_error, triangles
        output_file = None
        try:
            output_file = open(output_file_path, 'r')
        except:
            str_error = ('Error opening output file:\n{}'.format(output_file_path))
            return str_error, triangles
        count = -1
        number_of_triangles = 0
        triangles = []
        for line in output_file:
            count += 1
            values = line.strip()
            values = values.split()
            if count == 0:
                number_of_triangles = int(values[0])
                continue
            if count == (number_of_triangles + 1):
                break
            triangle = [int(values[1]), int(values[2]), int(values[3])]
            triangles.append(triangle)
        output_file.close()
        os.remove(output_file_path)
        os.remove(input_file_path)
        return str_error, triangles

    # @classmethod
    # def create_pytriangulation(self,
    #                            points,
    #                            segments,
    #                            holes = None):
    #     str_error = ''
    #     triangles = None
    #     if not isinstance(points, np.ndarray):
    #         str_error = 'Points object must be a numpy array'
    #         return str_error, triangles
    #     num_points, num_coordinates = points.shape
    #     if num_coordinates != 2:
    #         str_error = 'Points must have two coordinates'
    #         return str_error, triangles
    #     if not isinstance(segments, np.ndarray):
    #         str_error = 'Segments object must be a numpy array'
    #         return str_error, triangles
    #     num_segments, num_segments_columns = segments.shape
    #     if num_segments_columns != 2:
    #         str_error = 'Segments must have two columns'
    #         return str_error, triangles
    #     if not holes is None:
    #         if not isinstance(holes, np.ndarray):
    #             str_error = 'Edges object must be a numpy array'
    #             return str_error, triangles
    #         num_holes, holes_columns = holes.shape
    #         if holes_columns != 2:
    #             str_error = 'Holes must have two columns'
    #             return str_error, triangles
    #     data = None
    #     if not holes is None:
    #         data = dict(vertices=points, segments=segments, holes=holes)
    #     else:
    #         data = dict(vertices=points, segments=segments)
    #     triangulation = None
    #     try:
    #         triangulation = tr.triangulate(data, 'p')  # 'qpa0.05')
    #     except:
    #         str_error = ("An exception occurred in triangulation")
    #         return str_error, triangles
    #     if triangulation is None:
    #         str_error = ("An exception occurred in triangulation")
    #         return str_error, triangles
    #     if not 'triangles' in triangulation:
    #         str_error = ("An exception occurred in triangulation")
    #         return str_error, triangles
    #     triangles = triangulation['triangles'].tolist()
    #     return str_error, triangles
