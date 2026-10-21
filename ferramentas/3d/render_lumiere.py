# -*- coding: utf-8 -*-
"""Render da Lumière (22005) a partir do CAD V3: estúdio de parede, como as stills de catálogo.

A geometria é a do SolidWorks (step_para_glb.py, sem retoque). Aqui entram só material, luz,
câmera e parede. Material por peça pelo código do desenho (nome da malha no .glb):

- estrutura (aro, tampa traseira, braços, ponteiras, mancais, placa, tampas, haste e rótula):
  metal do acabamento;
- E-0006, E-0011, E-0058, E-0061, E-0062, E-0064 e F-0008: nylon natural (desenhos);
- E-0001 (vidro R600): frente lisa; verso prateado na área espelhada Ø158,75; anel e logo a
  laser sem prata, jateados; normal exata da esfera (R600 na frente, R604 no verso);
- E-0002 (berço refletor): epóxi branco liso brilho (desenho);
- F-0003: os LEDs emitem (4500 K ou 6000 K); o resto da placa e a eletrônica ficam opacos.

Eixos do .glb: x sai da parede, y é o vertical do SolidWorks. A cena gira a peça para z vertical,
com a parede no plano x = 0.

Uso:
  python render_lumiere.py modelo.glb saida.png [--acabamento brushed-nickel] [--led 1]
         [--res 1080x1350] [--amostras 128] [--azimute 28] [--elevacao 6] [--lente 85]
         [--orto] [--silhueta] [--blend cena.blend]
"""
import argparse, json, math, time
import bpy
import bmesh  # depois do bpy
import numpy as np
from mathutils import Vector, Matrix

# Metal (Metallic = 1): F0 linear, rugosidade, anisotropia. Black matte é dielétrico.
# Cor: matiz e croma (CIELAB) da cor F0 iguais aos das referências Deca do Thiago (21/10):
# gold h 88 C 38 (Deca 88/39), red gold h 67 C 33 (67/33), brushed nickel h 90 C 5,8 (90/6,1).
ACABAMENTOS = {
    'cromado':        dict(cor=(0.550, 0.556, 0.554), rug=0.03, ani=0.0, metal=1.0),
    'brushed-nickel': dict(cor=(0.620, 0.585, 0.520), rug=0.26, ani=0.75, metal=1.0),
    'gold':           dict(cor=(1.000, 0.740, 0.320), rug=0.07, ani=0.0, metal=1.0),
    'red-gold':       dict(cor=(0.960, 0.565, 0.315), rug=0.07, ani=0.0, metal=1.0),
    # Black matte: com a luz cheia o preto fosco lia cinza médio (L 47 na placa contra L 18 da
    # Deca); com as softboxes do produto a 25% lê L 25 (pixels não saturados).
    'black-matte':    dict(cor=(0.015, 0.015, 0.015), rug=0.55, ani=0.0, metal=0.0, luz=0.25),
}
NYLON = ('E-0006', 'E-0011', 'E-0058', 'E-0061', 'E-0062', 'E-0064', 'F-0008')
ESTRUTURA = ('C-0', 'D-0', 'E-0003', 'E-0004', 'E-0005', 'E-0007', 'E-0008', 'E-0009', 'E-0010',
             'E-0012', 'E-0013', 'E-0014', 'E-0059', 'E-0060', 'E-0063')


def args():
    ap = argparse.ArgumentParser()
    ap.add_argument('glb'); ap.add_argument('saida')
    ap.add_argument('--acabamento', default='brushed-nickel', choices=sorted(ACABAMENTOS))
    ap.add_argument('--led', type=float, default=1.0, help='0 = apagado; 1 = aceso na força padrão')
    ap.add_argument('--forca-led', type=float, default=60.0)
    ap.add_argument('--kelvin', type=float, default=4500.0)
    ap.add_argument('--so-led', action='store_true', help='apaga estúdio e ambiente (passe do LED)')
    ap.add_argument('--res', default='1080x1350')
    ap.add_argument('--amostras', type=int, default=128)
    ap.add_argument('--azimute', type=float, default=28.0, help='graus; positivo = câmera à esquerda da normal da parede')
    ap.add_argument('--elevacao', type=float, default=6.0)
    ap.add_argument('--lente', type=float, default=85.0)
    ap.add_argument('--margem', type=float, default=0.95)
    ap.add_argument('--exposicao', type=float, default=0.0)
    ap.add_argument('--mundo', type=float, default=0.02, help='força do ambiente')
    ap.add_argument('--halo', type=float, default=40.0, help='abertura do foco na parede (graus)')
    ap.add_argument('--parede', type=float, default=0.18, help='cor da parede (linear)')
    ap.add_argument('--luz', type=float, default=0.4, help='multiplica a potência das luzes de estúdio')
    ap.add_argument('--orto', action='store_true', help='câmera ortográfica de frente (medição)')
    ap.add_argument('--mm-por-px', type=float, default=0.25, help='escala da vista --orto')
    ap.add_argument('--silhueta', action='store_true', help='peças em branco chapado sobre preto, sem parede')
    ap.add_argument('--vista-cor', default='Khronos PBR Neutral', help='transformação de vista (AgX, Standard...)')
    ap.add_argument('--cartao', type=float, default=1.0, help='multiplica o cartão branco que o espelho reflete')
    ap.add_argument('--recorte', help='renderiza só a região x0,y0,x1,y1 (frações do quadro, y de cima)')
    ap.add_argument('--reflexo', type=float, default=0.4, help='brilho do rebatedor que o espelho reflete')
    ap.add_argument('--apagar', default='', help='luzes a zerar, por nome (depuração): chave,preenchimento,halo...')
    ap.add_argument('--rug', type=float, help='calibração: rugosidade do acabamento')
    ap.add_argument('--espec', type=float, help='calibração: Specular IOR Level (só black matte)')
    ap.add_argument('--base', type=float, help='calibração: cor base cinza do acabamento (linear)')
    ap.add_argument('--luz-produto', type=float, help='multiplica só as luzes do produto (padrão: o do acabamento)')
    ap.add_argument('--vidro-luz', type=float, default=0.3,
                    help='fração da luz das softboxes que atravessa o vidro até o berço (0 = barra tudo)')
    ap.add_argument('--blend')
    return ap.parse_args()


def sombra_parcial(m, t):
    """Raio de sombra atravessa o material com transmitância t. Sem cáusticas, o vidro barra toda
    a luz das softboxes e o berço branco atrás do anel fica no escuro: o anel apagado saía preto,
    e nas stills LUX desligadas ele é cinza escuro (Flex Lux: anel L 45 com a parede em L 68)."""
    if t <= 0:
        return
    nt = m.node_tree; out = nt.nodes['Material Output']
    sup = out.inputs['Surface'].links[0].from_socket
    lp = nt.nodes.new('ShaderNodeLightPath'); tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    tr.inputs['Color'].default_value = (t, t, t, 1)
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Shadow Ray'], mx.inputs[0])
    nt.links.new(sup, mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs['Surface'])


def principled(nome, **ent):
    m = bpy.data.materials.new(nome); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    for k, v in ent.items():
        b.inputs[k].default_value = v
    return m


def codigo(o):
    return o.data.name.split('.')[0]


def fit_esfera(P):
    A = np.c_[2 * P, np.ones(len(P))]; b = (P ** 2).sum(1)
    x = np.linalg.lstsq(A, b, rcond=None)[0]; c = x[:3]
    r = float(np.sqrt(x[3] + c @ c))
    return c, r, float(np.abs(np.linalg.norm(P - c, axis=1) - r).max())


def normal_esfera(mat, centro):
    """Normal = direção exata da esfera (centro em coordenadas do mundo), com o lado da face.
    Sem isso o reflexo do vidro côncavo ondula com a triangulação (estudo de 15/10)."""
    nt = mat.node_tree; N = nt.nodes; L = nt.links
    bsdf = N['Principled BSDF']
    geo = N.new('ShaderNodeNewGeometry')
    sub = N.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'
    L.new(geo.outputs['Position'], sub.inputs[0]); sub.inputs[1].default_value = tuple(centro)
    nrm = N.new('ShaderNodeVectorMath'); nrm.operation = 'NORMALIZE'; L.new(sub.outputs[0], nrm.inputs[0])
    dot = N.new('ShaderNodeVectorMath'); dot.operation = 'DOT_PRODUCT'
    L.new(nrm.outputs[0], dot.inputs[0]); L.new(geo.outputs['True Normal'], dot.inputs[1])
    sg = N.new('ShaderNodeMath'); sg.operation = 'SIGN'; L.new(dot.outputs['Value'], sg.inputs[0])
    esc = N.new('ShaderNodeVectorMath'); esc.operation = 'SCALE'
    L.new(nrm.outputs[0], esc.inputs[0]); L.new(sg.outputs[0], esc.inputs['Scale'])
    L.new(esc.outputs[0], bsdf.inputs['Normal'])


def tangente(mat, eixo, centro=None):
    """Direção do escovado: ao longo de `eixo` (centro=None) ou circular em volta dele."""
    nt = mat.node_tree; N = nt.nodes; L = nt.links
    bsdf = N['Principled BSDF']
    if centro is None:
        v = N.new('ShaderNodeCombineXYZ')
        for i in range(3):
            v.inputs[i].default_value = eixo[i]
        L.new(v.outputs[0], bsdf.inputs['Tangent']); return
    geo = N.new('ShaderNodeNewGeometry')
    sub = N.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'
    L.new(geo.outputs['Position'], sub.inputs[0]); sub.inputs[1].default_value = tuple(centro)
    cr = N.new('ShaderNodeVectorMath'); cr.operation = 'CROSS_PRODUCT'
    cr.inputs[0].default_value = tuple(eixo); L.new(sub.outputs[0], cr.inputs[1])
    nrm = N.new('ShaderNodeVectorMath'); nrm.operation = 'NORMALIZE'; L.new(cr.outputs[0], nrm.inputs[0])
    L.new(nrm.outputs[0], bsdf.inputs['Tangent'])


def separar(o, grupos):
    """Divide a malha `o` em objetos novos por grupo de faces {nome: [índices]}."""
    novos = {}
    for nome, idx in grupos.items():
        if not idx:
            continue
        bm = bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
        manter = set(idx)
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in manter], context='FACES')
        me = bpy.data.meshes.new(nome); bm.to_mesh(me); bm.free()
        ob = bpy.data.objects.new(nome, me); ob.matrix_world = o.matrix_world.copy()
        bpy.context.scene.collection.objects.link(ob)
        novos[nome] = ob
    bpy.data.objects.remove(o)
    return novos


def caixa(objs):
    lo = Vector((1e9,) * 3); hi = Vector((-1e9,) * 3)
    for o in objs:
        for c in o.bound_box:
            p = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, p)); hi = Vector(map(max, hi, p))
    return lo, hi


def luz_area(nome, pos, alvo, tam, tam_y, potencia, cor=(1, 1, 1)):
    ld = bpy.data.lights.new(nome, 'AREA'); ld.shape = 'RECTANGLE'
    ld.size = tam; ld.size_y = tam_y; ld.energy = potencia; ld.color = cor
    ob = bpy.data.objects.new(nome, ld); bpy.context.scene.collection.objects.link(ob)
    ob.location = pos
    ob.rotation_euler = (alvo - pos).to_track_quat('-Z', 'Y').to_euler()
    return ob


def main():
    A = args()
    t0 = time.time()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=A.glb)
    for r in [o for o in bpy.context.scene.objects if o.parent is None]:
        r.rotation_mode = 'XYZ'; r.rotation_euler = (math.pi / 2, 0, 0)   # y do CAD -> z
    bpy.context.view_layer.update()
    for o in [o for o in bpy.context.scene.objects if o.type == 'MESH']:
        mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    pecas = [o for o in bpy.context.scene.objects if o.type == 'MESH']

    acab = dict(ACABAMENTOS[A.acabamento])
    if A.rug is not None:
        acab['rug'] = A.rug
    if A.espec is not None:
        acab['espec'] = A.espec
    if A.base is not None:
        acab['cor'] = (A.base,) * 3
    ac = A.acabamento
    usados = {}

    # Vidro E-0001: separa frente, verso prateado, verso sem prata (anel e logo) e borda.
    vidro = next(o for o in pecas if codigo(o) == 'E-0001-V1')
    R3 = vidro.matrix_world.to_3x3()
    g = {'vidro-frente': [], 'vidro-prata': [], 'vidro-jateado': [], 'vidro-borda': []}
    for p in vidro.data.polygons:
        nx = (R3 @ p.normal).normalized().x
        if nx > 0.5:
            g['vidro-frente'].append(p.index)
        elif nx < -0.5:
            cor = vidro.data.materials[p.material_index].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value
            g['vidro-prata' if cor[0] < 0.6 else 'vidro-jateado'].append(p.index)   # cinza no CAD = área espelhada
        else:
            g['vidro-borda'].append(p.index)
    partes = separar(vidro, g)
    pecas = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    esferas = {}
    for nome in ('vidro-frente', 'vidro-prata', 'vidro-jateado'):
        o = partes[nome]
        P = np.array([(o.matrix_world @ v.co)[:] for v in o.data.vertices])
        esferas[nome] = fit_esfera(P)
    lo_v, hi_v = caixa([partes['vidro-frente']])
    eixo_cab = Vector((1, 0, 0))
    centro_cab = Vector((lo_v.x, (lo_v.y + hi_v.y) / 2, (lo_v.z + hi_v.z) / 2))

    if A.silhueta:
        branco = principled('chapado', **{'Base Color': (0, 0, 0, 1), 'Emission Color': (1, 1, 1, 1),
                                          'Emission Strength': 1.0, 'Roughness': 1.0})
        for o in pecas:
            o.data.materials.clear(); o.data.materials.append(branco)
    else:
        if acab['metal']:
            metal = principled('metal-' + ac, **{'Base Color': (*acab['cor'], 1), 'Metallic': 1.0,
                                                  'Roughness': acab['rug'], 'Anisotropic': acab['ani']})
        else:
            metal = principled('metal-' + ac, **{'Base Color': (*acab['cor'], 1), 'Metallic': 0.0,
                                                  'Roughness': acab['rug'], 'Coat Weight': 0.0,
                                                  'Specular IOR Level': acab.get('espec', 0.5)})
        nylon = principled('nylon', **{'Base Color': (0.86, 0.85, 0.81, 1), 'Roughness': 0.42,
                                       'Subsurface Weight': 0.35, 'Subsurface Radius': (0.002, 0.002, 0.0015)})
        berco = principled('berco-branco', **{'Base Color': (0.86, 0.86, 0.86, 1), 'Roughness': 0.12,
                                               'Coat Weight': 0.6, 'Coat Roughness': 0.05})
        aco = principled('aco', **{'Base Color': (0.56, 0.55, 0.53, 1), 'Metallic': 1.0, 'Roughness': 0.25})
        pcb = principled('pcb', **{'Base Color': (0.03, 0.12, 0.04, 1), 'Roughness': 0.35})
        led = principled('led', **{'Base Color': (0.85, 0.80, 0.55, 1), 'Roughness': 0.3,
                                    'Emission Strength': A.forca_led * A.led})
        bb = led.node_tree.nodes.new('ShaderNodeBlackbody'); bb.inputs['Temperature'].default_value = A.kelvin
        led.node_tree.links.new(bb.outputs[0], led.node_tree.nodes['Principled BSDF'].inputs['Emission Color'])
        vidro_liso = principled('vidro-liso', **{'Base Color': (1, 1, 1, 1), 'Roughness': 0.0, 'IOR': 1.52,
                                                  'Transmission Weight': 1.0})
        jateado = principled('vidro-jateado', **{'Base Color': (1, 1, 1, 1), 'Roughness': 0.5, 'IOR': 1.52,
                                                  'Transmission Weight': 1.0})
        prata = principled('prata', **{'Base Color': (0.97, 0.965, 0.955, 1), 'Metallic': 1.0, 'Roughness': 0.0})
        for nome, mat in (('vidro-frente', vidro_liso), ('vidro-prata', prata), ('vidro-jateado', jateado)):
            m = mat.copy(); normal_esfera(m, esferas[nome][0])
            o = partes[nome]; o.data.materials.clear(); o.data.materials.append(m)
            usados[nome] = 'esfera R%.2f mm (resíduo %.4f mm)' % (esferas[nome][1] * 1000, esferas[nome][2] * 1000)
        o = partes['vidro-borda']; o.data.materials.clear(); o.data.materials.append(jateado)
        for nome in ('vidro-frente', 'vidro-jateado', 'vidro-borda'):
            sombra_parcial(partes[nome].data.materials[0], A.vidro_luz)
        usados['vidro-borda'] = 'jateado'

        for o in pecas:
            if o.name.startswith('vidro-'):
                continue
            c = codigo(o)
            if c.startswith(ESTRUTURA):
                m = metal
                if acab['ani'] > 0:
                    m = metal.copy()
                    lo, hi = caixa([o]); d = hi - lo; mid = (lo + hi) / 2
                    if c in ('E-0003-V3', 'E-0004-V3'):
                        tangente(m, eixo_cab, centro_cab); usados[o.name] = c + ' metal, escovado circular (eixo da cabeça)'
                    elif c.startswith(('D-0003', 'D-0006', 'C-0')):
                        ax = [abs(d.x), abs(d.y), abs(d.z)]; i = ax.index(max(ax))
                        tangente(m, tuple(1.0 if k == i else 0.0 for k in range(3))); usados[o.name] = c + ' metal, escovado ao longo do tubo'
                    elif c.startswith('E-0010'):
                        tangente(m, (0, 0, 1)); usados[o.name] = c + ' metal, escovado vertical'
                    else:
                        tangente(m, (0, 0, 1), mid); usados[o.name] = c + ' metal, escovado circular (eixo vertical)'
                else:
                    usados[o.name] = c + ' metal'
            elif c.startswith(NYLON):
                m = nylon; usados[o.name] = c + ' nylon'
            elif c == 'E-0002-V3':
                m = berco; usados[o.name] = c + ' epóxi branco brilho'
            elif c == 'F-0003':
                o.data.materials[1] = led; o.data.materials[0] = pcb
                for s in o.material_slots:
                    s.link = 'DATA'
                usados[o.name] = c + ' placa + LEDs (%g K, força %g)' % (A.kelvin, A.forca_led * A.led)
                continue
            elif c.startswith('F-0006'):
                m = pcb; usados[o.name] = c + ' eletrônica'
            else:
                m = aco; usados[o.name] = c + ' aço (parafuso/porca)'
            o.data.materials.clear(); o.data.materials.append(m)
    for o in [o for o in bpy.context.scene.objects if o.type == 'MESH']:
        for p in o.data.polygons:
            p.use_smooth = True

    visiveis = [o for o in bpy.context.scene.objects if o.type == 'MESH' and caixa([o])[1].x > 0.0005]
    lo, hi = caixa(visiveis); lo.x = max(lo.x, 0.0)   # parafusos e buchas entram na parede
    centro = (lo + hi) / 2; tam = (hi - lo).length

    sc = bpy.context.scene
    w = bpy.data.worlds.new('mundo'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    if A.silhueta:
        bg.inputs['Color'].default_value = (0, 0, 0, 1)
    else:
        bg.inputs['Color'].default_value = (0.6, 0.6, 0.6, 1); bg.inputs['Strength'].default_value = A.mundo
        # Parede: plano x = 0, cinza fosco (as stills de catálogo são em parede cinza).
        bm = bmesh.new()
        L2 = 3.0
        vs = [bm.verts.new((-0.0002, centro.y + a * L2, centro.z + b * L2)) for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        bm.faces.new(vs); me = bpy.data.meshes.new('parede'); bm.to_mesh(me); bm.free()
        par = bpy.data.objects.new('parede', me); sc.collection.objects.link(par)
        par.data.materials.append(principled('parede', **{'Base Color': (A.parede, A.parede, A.parede, 1), 'Roughness': 0.9}))
        k = A.luz
        # Luz no produto (chave, preenchimento e cartão; o foco da parede não muda). Num produto
        # preto o fotógrafo baixa as softboxes, senão o preto fosco vira cinza médio.
        kp = A.luz_produto if A.luz_produto is not None else acab.get('luz', 1.0)
        # Estúdio das stills de catálogo: chave grande à esquerda e acima da câmera, preenchimento
        # fraco à direita, cartão branco grande atrás da câmera (é o que o espelho e o metal
        # refletem) e um foco suave na parede atrás do produto (o halo do fundo cinza).
        chave = luz_area('chave', centro + Vector((0.85, -0.75, 0.70)), centro, 0.9, 0.7, 230 * k * kp)
        preench = luz_area('preenchimento', centro + Vector((0.95, 0.85, 0.10)), centro, 1.0, 0.8, 70 * k * kp)
        # A parede recebe só o foco do halo (degradê), como nas stills: chave e preenchimento
        # iluminam o produto, não a parede (light linking do Cycles).
        col = bpy.data.collections.new('excluidos'); col.objects.link(par)
        # O espelho (prata) também não recebe as luzes: ele reflete só o rebatedor cinza abaixo,
        # que fica atrás da câmera. Assim o anel e o logo a laser acesos aparecem contra um
        # reflexo neutro, em vez de sumirem no branco das softboxes.
        col.objects.link(partes['vidro-prata']); col.objects.link(partes['vidro-frente'])
        for co in col.collection_objects:
            co.light_linking.link_state = 'EXCLUDE'
        for lz in (chave, preench):
            lz.light_linking.receiver_collection = col
        col2 = bpy.data.collections.new('so-espelho'); col2.objects.link(partes['vidro-prata'])
        col2.objects.link(partes['vidro-frente'])
        for co in col2.collection_objects:
            co.light_linking.link_state = 'EXCLUDE'
        cartao = luz_area('cartao-frente', centro + Vector((2.2, -0.35, 0.30)), centro, 2.2, 1.6, 260 * k * kp * A.cartao)
        cartao.visible_diffuse = False   # só reflexo: não lava a parede
        cartao.light_linking.receiver_collection = col2
        # Cúpula cinza em volta da cena, vista só pelo espelho (light linking): o côncavo mostra
        # um campo largo atrás da câmera, e um rebatedor plano deixava metade do espelho preta.
        # Degradê suave, mais claro em cima. O metal não a vê e mantém o contraste das softboxes.
        bm = bmesh.new(); R = 4.0
        bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=R)
        me = bpy.data.meshes.new('cupula'); bm.to_mesh(me); bm.free()
        reb = bpy.data.objects.new('cupula', me); sc.collection.objects.link(reb)
        reb.location = centro
        mr = bpy.data.materials.new('cupula'); mr.use_nodes = True; nt = mr.node_tree
        for n in list(nt.nodes):
            nt.nodes.remove(n)
        tc = nt.nodes.new('ShaderNodeTexCoord'); sx = nt.nodes.new('ShaderNodeSeparateXYZ')
        mp = nt.nodes.new('ShaderNodeMapRange'); em = nt.nodes.new('ShaderNodeEmission')
        out = nt.nodes.new('ShaderNodeOutputMaterial')
        mp.inputs['From Min'].default_value = -R; mp.inputs['From Max'].default_value = R
        mp.inputs['To Min'].default_value = 0.6 * A.reflexo; mp.inputs['To Max'].default_value = 1.2 * A.reflexo
        em.inputs['Color'].default_value = (1, 1, 1, 1)
        nt.links.new(tc.outputs['Object'], sx.inputs[0]); nt.links.new(sx.outputs['Z'], mp.inputs['Value'])
        nt.links.new(mp.outputs['Result'], em.inputs['Strength']); nt.links.new(em.outputs[0], out.inputs['Surface'])
        reb.data.materials.append(mr)
        reb.visible_camera = False; reb.visible_diffuse = False; reb.visible_shadow = False
        col3 = bpy.data.collections.new('espelho'); col3.objects.link(partes['vidro-prata'])
        col3.objects.link(partes['vidro-frente'])
        for co in col3.collection_objects:
            co.light_linking.link_state = 'INCLUDE'
        reb.light_linking.receiver_collection = col3
        sd = bpy.data.lights.new('halo', 'SPOT'); sd.energy = 900 * k; sd.spot_size = math.radians(A.halo)
        sd.spot_blend = 1.0; sd.shadow_soft_size = 0.4
        so = bpy.data.objects.new('halo', sd); sc.collection.objects.link(so)
        so.location = centro + Vector((1.3, -0.2, 0.25)); alvo_h = Vector((0.0, centro.y, centro.z + 0.03))
        so.rotation_euler = (alvo_h - so.location).to_track_quat('-Z', 'Y').to_euler()
        # Fora do reflexo: no espelho o raio sai do vidro da frente por transmissão, então só
        # visible_glossy não basta (na vista de frente o foco aparecia como mancha branca).
        so.visible_glossy = False; so.visible_transmission = False; so.visible_diffuse = True
        # O foco é só da parede (o produto faz sombra nela, mas não recebe a luz dele).
        col4 = bpy.data.collections.new('so-parede'); col4.objects.link(par)
        for co in col4.collection_objects:
            co.light_linking.link_state = 'INCLUDE'
        so.light_linking.receiver_collection = col4
        for nome in filter(None, A.apagar.split(',')):
            sc.objects[nome].data.energy = 0.0
        if A.so_led:
            for o in sc.objects:
                if o.type == 'LIGHT':
                    o.data.energy = 0.0
            bg.inputs['Strength'].default_value = 0.0
            mp.inputs['To Min'].default_value = 0.0; mp.inputs['To Max'].default_value = 0.0

    rx, ry = map(int, A.res.split('x'))
    cd = bpy.data.cameras.new('camera'); cam = bpy.data.objects.new('camera', cd); sc.collection.objects.link(cam)
    if A.orto:
        cd.type = 'ORTHO'; cd.ortho_scale = max(rx, ry) * A.mm_por_px / 1000.0
        cam.location = Vector((1.0, centro.y, centro.z)); cam.rotation_euler = (math.pi / 2, 0, math.pi / 2)
        cd.clip_start = 0.01; cd.clip_end = 5
    else:
        cd.lens = A.lente; cd.sensor_width = 36.0
        meia = math.atan(18.0 / A.lente) * min(rx, ry) / max(rx, ry)
        dist = (tam / 2) * A.margem / math.sin(meia)
        a, e = math.radians(A.azimute), math.radians(A.elevacao)
        cam.location = centro + dist * Vector((math.cos(a) * math.cos(e), -math.sin(a) * math.cos(e), math.sin(e)))
        cam.rotation_euler = (centro - cam.location).to_track_quat('-Z', 'Y').to_euler()
        cd.clip_start = dist / 100; cd.clip_end = dist * 100
    sc.camera = cam

    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    sc.cycles.samples = A.amostras; sc.cycles.use_adaptive_sampling = True
    sc.cycles.use_denoising = not A.silhueta; sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.max_bounces = 24; sc.cycles.glossy_bounces = 12; sc.cycles.transmission_bounces = 16
    sc.cycles.diffuse_bounces = 6
    sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
    sc.cycles.sample_clamp_direct = 0.0; sc.cycles.sample_clamp_indirect = 0.0
    sc.cycles.blur_glossy = 0.0
    if A.silhueta:
        sc.cycles.samples = 16; sc.cycles.max_bounces = 0
    sc.render.resolution_x, sc.render.resolution_y = rx, ry; sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    if A.recorte:
        x0, y0, x1, y1 = map(float, A.recorte.split(','))
        sc.render.use_border = True; sc.render.use_crop_to_border = True
        sc.render.border_min_x, sc.render.border_max_x = x0, x1
        sc.render.border_min_y, sc.render.border_max_y = 1 - y1, 1 - y0
    if A.saida.lower().endswith('.exr'):
        sc.render.image_settings.file_format = 'OPEN_EXR'; sc.render.image_settings.color_depth = '32'
    else:
        sc.render.image_settings.file_format = 'PNG'
    sc.render.filepath = A.saida
    sc.view_settings.view_transform = 'Standard' if A.silhueta else A.vista_cor
    sc.view_settings.exposure = A.exposicao
    if A.blend:
        bpy.ops.wm.save_as_mainfile(filepath=A.blend)
    t1 = time.time()
    bpy.ops.render.render(write_still=True)
    t2 = time.time()
    info = {'saida': A.saida, 'preparo_s': round(t1 - t0, 1), 'render_s': round(t2 - t1, 1),
            'res': A.res, 'amostras': A.amostras, 'acabamento': ac, 'led': A.led,
            'camera': {'orto': A.orto, 'azimute': A.azimute, 'elevacao': A.elevacao, 'lente': A.lente,
                       'local_m': [round(v, 4) for v in cam.location]},
            'caixa_produto_mm': [round(v * 1000, 1) for v in (hi - lo)], 'materiais': usados}
    json.dump(info, open(A.saida.rsplit('.', 1)[0] + '.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps({k: info[k] for k in ('saida', 'preparo_s', 'render_s', 'caixa_produto_mm')}))


main()
