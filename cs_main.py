import os
import bgl
import bpy
from . import gl_wrapper
import numpy as np
import moderngl
import numpy as np


def compute_uv(shader, obj, image, color):

    texcoords = []
    uv_layer = obj.data.uv_layers.active.data
    for polygon in obj.data.polygons:
        for loop in range(polygon.loop_start, polygon.loop_start + polygon.loop_total):
            texcoords.append(uv_layer[loop].uv.x)
            texcoords.append(uv_layer[loop].uv.y)
            texcoords.append(float(0.0))
            texcoords.append(float(0.0))

    uv_array_size = int(len(texcoords)//4)

    gl_context = moderngl.create_context(require=430)

    if image is None:
        arr = [0,0,0,0]

        img = gl_wrapper.ComputeBuffer(gl_context).CreateArray(1, 1, 4).Bind(1)
    else:

        img = gl_wrapper.ComputeBuffer(gl_context).FromPythonImage(image).Bind(1)
        arr = [image.size[0], image.size[1], 1,1]

    texcoords_in = gl_wrapper.ComputeBuffer(gl_context).FromPythonArray(texcoords, uv_array_size, 1, 4).Bind(2)
    texcoords_out = gl_wrapper.ComputeBuffer(gl_context).CreateArray(uv_array_size, 1, 4).Bind(3)
    col = gl_wrapper.ComputeBuffer(gl_context).FromPythonArray(color, 1, 1, 4).Bind(4)
    use_tex = gl_wrapper.ComputeBuffer(gl_context).FromPythonArray(arr, 1, 1, 4).Bind(5)

    shader.Dispatch(gl_context, (uv_array_size//shader.threads_x)+1)

    new_texcoords = texcoords_out.GetFromBuffer(uv_array_size, 1, 4)

    for polygon in obj.data.polygons:
        for loop in range(polygon.loop_start, polygon.loop_start + polygon.loop_total):
            vertex_array = new_texcoords[loop][0].tolist()
            uv_layer[loop].uv = (vertex_array[0], vertex_array[1])

    img.Release()
    texcoords_in.Release()
    texcoords_out.Release()
    col.Release()
    use_tex.Release()
