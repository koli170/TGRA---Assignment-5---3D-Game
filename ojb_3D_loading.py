from Base3DObjects import *


def load_mtl_file(file_location, file_name, mesh_model):
    print("  Start loading MTL: " + file_name)
    mtl = None
    fin = open(file_location + "/" + file_name)
    for line in fin.readlines():
        tokens = line.split()
        if len(tokens) == 0:
            continue
        if tokens[0] == "newmtl":
            print("    Material: " + tokens[1])
            mtl = Material()
            mesh_model.add_material(tokens[1], mtl)
        elif tokens[0] == "Kd":
            mtl.diffuse = Color(float(tokens[1]), float(tokens[2]), float(tokens[3]))
        elif tokens[0] == "Ks":
            mtl.specular = Color(float(tokens[1]), float(tokens[2]), float(tokens[3]))
        elif tokens[0] == "Ns":
            mtl.shininess = float(tokens[1])
    print("  Finished loading MTL: " + file_name)


def load_obj_file(file_location, file_name):
    print("Start loading OBJ: " + file_name)
    mesh_model = MeshModel()
    current_object_id = None
    current_position_list = []
    current_normal_list = []
    fin = open(file_location + "/" + file_name)
    for line in fin.readlines():
        tokens = line.split()
        if len(tokens) == 0:
            continue
        if tokens[0] == "mtllib":
            load_mtl_file(file_location, tokens[1], mesh_model)
        elif tokens[0] == "o":
            print("  Mesh: " + tokens[1])
            current_object_id = tokens[1]
            # current_position_list = []
            # current_normal_list = []
        elif tokens[0] == "v":
            current_position_list.append(
                Point(float(tokens[1]), float(tokens[2]), float(tokens[3]))
            )
        elif tokens[0] == "vn":
            current_normal_list.append(
                Vector(float(tokens[1]), float(tokens[2]), float(tokens[3]))
            )
        elif tokens[0] == "usemtl":
            mesh_model.set_mesh_material(current_object_id, tokens[1])
        elif tokens[0] == "f":
            for i in range(1, len(tokens)):
                tokens[i] = tokens[i].split("/")
            vertex_count = len(tokens) - 1
            for i in range(vertex_count - 2):

                def get_idx(v, idx):
                    return int(v[idx]) - 1 if len(v) > idx and v[idx] != "" else None

                v1_p = get_idx(tokens[1], 0)
                v1_n = get_idx(tokens[1], 2)
                v2_p = get_idx(tokens[i + 2], 0)
                v2_n = get_idx(tokens[i + 2], 2)
                v3_p = get_idx(tokens[i + 3], 0)
                v3_n = get_idx(tokens[i + 3], 2)

                # Fallback for missing normals
                n1 = current_normal_list[v1_n] if v1_n is not None else Vector(0, 0, 1)
                n2 = current_normal_list[v2_n] if v2_n is not None else Vector(0, 0, 1)
                n3 = current_normal_list[v3_n] if v3_n is not None else Vector(0, 0, 1)

                mesh_model.add_vertex(
                    current_object_id, current_position_list[v1_p], n1
                )
                mesh_model.add_vertex(
                    current_object_id, current_position_list[v2_p], n2
                )
                mesh_model.add_vertex(
                    current_object_id, current_position_list[v3_p], n3
                )

    mesh_model.set_opengl_buffers()
    print("Finished loading OBJ: " + file_name)
    return mesh_model
