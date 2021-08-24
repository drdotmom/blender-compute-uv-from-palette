
class Content():

    def __init__(self, material, texture, color, mesh, fbx):

        self.material = material
        self.texture = texture
        self.color = color
        self.mesh = mesh
        self.fbx = fbx

def read_unity_project(path):

    project = open(path, "r")

    content_list = []
    for line in project.readlines():
        lst = line.split(";")
        material = lst[0]
        MainTex = lst[1]
        if lst[1] == "null":
            MainTex = None
        
        Color = lst[2].split("|")
        if lst[2]=="null":
            Color = "1|1|1|1".split("|")
        
        mesh = lst[3]
        fbx = lst[4].replace("\n","")

        content_list.append(Content(material, MainTex, Color, mesh, fbx))

    project.close()

    return content_list
