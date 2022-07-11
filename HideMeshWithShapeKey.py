import textwrap
import bpy

bl_info = {
    # required
    'name': 'Hide Mesh With Shape Key',
    'blender': (3, 1, 0),
    'category': 'Object',
    # optional
    'version': (1, 0, 0),
    'author': 'Jared Williams',
    'description': 'Hide sub-meshes with a shape key.',
}


class HideMeshWithShapeKeyPanel(bpy.types.Panel):
    bl_label = 'Hide Mesh With Shape Key'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        wrapper = textwrap.TextWrapper()
        list = wrapper.wrap(
            text='Select the base mesh to join the new mesh into. A shape key will be created with _Hide at the end. A vertex group will be created with the original vertices.')
        for text in list:
            row = layout.row(align=True)
            row.alignment = 'EXPAND'
            row.label(text=text)
        col = layout.column()
        for (prop_name, _) in PROPS:
            row = col.row()
            row.prop(context.scene, prop_name)
        layout.operator('mswsk.hide_mesh_with_shape_key', text='Create')

    def execute(self, context):
        if self.action == 'CLEAR':
            self.do_it(context=context)

    def do_it(context):
        print('Doing it!')


class HideMeshWithShapeKey(bpy.types.Operator):
    bl_idname = "mswsk.hide_mesh_with_shape_key"
    bl_label = "Hide Mesh With Shape Key"
    bl_options = {"UNDO"}

    def invoke(self, context, event):
        bpy.ops.object.mode_set(mode='OBJECT')
        base_mesh = context.scene.BaseMesh
        incoming_mesh = context.scene.NewMesh
        if (not base_mesh or not incoming_mesh):
            print('Base or target mesh not provided')
            return {"FINISHED"}
        if (base_mesh == incoming_mesh):
            print('Base and target mesh are the same')
            return {"FINISHED"}
        print("Using base mesh:", base_mesh.name, incoming_mesh.name)
        incoming_mesh_vertices = incoming_mesh.data.vertices
        incoming_mesh_name = incoming_mesh.name
        new_vertex_group = incoming_mesh.vertex_groups.new(
            name=incoming_mesh_name)
        new_vertex_group.add(
            range(len(incoming_mesh_vertices)), 1.0, 'REPLACE')
        for obj in bpy.data.objects:
            obj.select_set(False)
        incoming_mesh.select_set(True)
        base_mesh.select_set(True)
        context.view_layer.objects.active = base_mesh
        bpy.ops.object.join()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        if not base_mesh.data.shape_keys:
            base_mesh.shape_key_add(name='Basis')
        # create shape key
        hide_shape_key = base_mesh.shape_key_add(
            name=incoming_mesh_name + '_Hide', from_mix=False)
        hide_shape_key.value = 1
        # select it
        active_object = bpy.context.active_object
        keys = active_object.data.shape_keys.key_blocks.keys()
        active_object.active_shape_key_index = keys.index(hide_shape_key.name)
        # select vertices
        vertices = [vert for vert in base_mesh.data.vertices if base_mesh.vertex_groups[incoming_mesh_name].index in [
            i.group for i in vert.groups]]
        for vertice in vertices:
            vertice.select = True
        # scale
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.transform.resize(
            value=(0.0000001, 0.0000001, 0.0000001)
        )
        bpy.ops.object.mode_set(mode='OBJECT')
        hide_shape_key.value = 0
        return {"FINISHED"}


CLASSES = [
    HideMeshWithShapeKey,
    HideMeshWithShapeKeyPanel
]

PROPS = [
    ('BaseMesh', bpy.props.PointerProperty(name="Base", type=bpy.types.Object)),
    ('NewMesh', bpy.props.PointerProperty(
        name="New", type=bpy.types.Object)),
]


def register():
    for (prop_name, prop_value) in PROPS:
        setattr(bpy.types.Scene, prop_name, prop_value)

    for klass in CLASSES:
        bpy.utils.register_class(klass)


def unregister():
    for (prop_name, _) in PROPS:
        delattr(bpy.types.Scene, prop_name)

    for klass in CLASSES:
        bpy.utils.unregister_class(klass)


if __name__ == '__main__':
    register()
