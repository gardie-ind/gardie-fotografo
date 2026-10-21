# -*- coding: utf-8 -*-
"""Lista as peças de um .glb vindo do CAD: instância, peça (malha), caixa em mm e materiais."""
import sys
import bpy
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=sys.argv[-1])
lin = []
for o in sorted(bpy.context.scene.objects, key=lambda o: (o.data.name if o.type == 'MESH' else '', o.name)):
    if o.type != 'MESH':
        continue
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = [min(p[i] for p in pts) * 1000 for i in range(3)]
    hi = [max(p[i] for p in pts) * 1000 for i in range(3)]
    ms = []
    for i, m in enumerate(o.data.materials):
        n = sum(1 for p in o.data.polygons if p.material_index == i)
        c = m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value[:3] if m and m.node_tree else (0, 0, 0)
        ms.append('(%.2f,%.2f,%.2f)x%d' % (*c, n))
    lin.append('%-8s %-24s x %6.1f..%6.1f y %6.1f..%6.1f z %6.1f..%6.1f  %s' % (
        o.name, o.data.name[:24], lo[0], hi[0], lo[1], hi[1], lo[2], hi[2], ' '.join(ms)))
print('\n'.join(lin))
