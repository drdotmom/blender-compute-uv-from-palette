import moderngl
import numpy as np


class ComputeBuffer():

    def __init__(self, gl_context, array=None):
        self.context = gl_context
        self.buffer = None
        self.array = array
        self.bind_code = None
        self.size_x = 1
        self.size_y = 1
        self.size_z = 1

    def FromPythonArray(self, array, size_x, size_y, size_z):
        self.array = np.float32(np.array(array)).reshape(size_x, size_y, size_z)
        self.size_x = size_x
        self.size_y = size_y
        self.size_z = size_z
        return self
    
    def FromPythonImage(self, image):
        self.array = np.float32(np.array(image.pixels)).reshape(image.size[0]*image.size[1], 1, 4)
        self.size_x = image.size[0]*image.size[1]
        self.size_y = 1
        self.size_z = 4
        return self

    def CreateArray(self, size_x, size_y, size_z):
        self.array = np.empty((size_x, size_y, size_z), dtype=np.float32)
        self.size_x = size_x
        self.size_y = size_y
        self.size_z = size_z
        return self

    def Bind(self, id):
        self.bind_code = id
        buffer = self.context.buffer(self.array)
        buffer.bind_to_storage_buffer(id)
        self.buffer = buffer
        return self

    def GetFromBuffer(self, size_x, size_y, size_z):
        return np.frombuffer(self.buffer.read(), dtype=np.float32).reshape(size_x, size_y, size_z)

    def Release(self):
        self.buffer.release()


class ComputeShader():

    def __init__(self, path):
        self.path = path
        self.source = None
        self.shader = None
        self.threads_x = 64
        self.threads_y = 1
        self.threads_z = 1

        shader_file = open(self.path, "r")

        shader = ""
        for line in shader_file.readlines():
            shader += line
            if line.find("#define STEP_SIZE_X ") != -1:
                self.threads_x = int(line.split("#define STEP_SIZE_X ")[-1])

        self.source = shader
        shader_file.close()
        
    def Dispatch(self, context, groupX, groupY=None, groupZ=None):
        self.shader = context.compute_shader(self.source)
        self.shader.run( group_x=int(groupX) )

    def Release(self):
        self.shader.release()
