"""The Anatomy of a Suit: one continuous Blender shot, rendered as the site's 535 frames.

blender -b --factory-startup --python tools/suit_film.py -- OUTDIR [frame,frame,...] [WIDTH]
With a frame list it renders only those frames (for checking the look); otherwise all 535.

Chapters (frame ranges match CH in index.html):
  0   1- 60  empty spotlit stage, a ghost of a man under the light
  1  60-130  the shirt floats in
  2 130-200  the waistcoat flies in and closes around it
  3 200-290  jacket panels drift in from an exploded view and lock together
  4 290-340  trousers rise into place, the full cut turns in the light
  5 340-400  a man fills the suit
  6 400-470  he walks forward; three men in other cloths walk with him
  7 470-535  push into the cuff: four buttons and a quarter-inch of shirt, fade out
"""
import bpy, bmesh, math, sys, random
from mathutils import Vector, Euler

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OUT = argv[0] if argv else '//frames'
ONLY = [int(f) for f in argv[1].split(',')] if len(argv) > 1 and argv[1] else None
WIDTH = int(argv[2]) if len(argv) > 2 else 1920
TOTAL = 535
random.seed(7)


def lin(h):
    h = h.lstrip('#')
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (1,)


# ---------- scene ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x, sc.render.resolution_y = WIDTH, WIDTH * 9 // 16
sc.render.fps = 24
sc.frame_start, sc.frame_end = 1, TOTAL
sc.view_settings.view_transform = 'AgX'
sc.view_settings.look = 'AgX - Punchy'
sc.render.image_settings.file_format = 'JPEG'
sc.render.image_settings.quality = 88
ee = sc.eevee
ee.taa_render_samples = 48
ee.use_raytracing = True
ee.use_volumetric_shadows = True
ee.volumetric_tile_size = '4'
ee.volumetric_end = 40

world = bpy.data.worlds.new('World')
sc.world = world
world.use_nodes = True
wn = world.node_tree.nodes
wn['Background'].inputs['Color'].default_value = lin('#070908')
wn['Background'].inputs['Strength'].default_value = 1.0
haze = wn.new('ShaderNodeVolumePrincipled')
haze.inputs['Density'].default_value = 0.009
haze.inputs['Color'].default_value = lin('#c9d4c6')
world.node_tree.links.new(haze.outputs[0], wn['World Output'].inputs['Volume'])


def key(obj, frame, **kw):
    for attr, val in kw.items():
        setattr(obj, attr, val)
        obj.keyframe_insert(attr, frame=frame)


def mat(name, color, rough=0.75, sheen=0.6, weave=True, metal=0.0, emit=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.surface_render_method = 'DITHERED'
    nt = m.node_tree
    p = nt.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value = lin(color) if isinstance(color, str) else color
    p.inputs['Roughness'].default_value = rough
    p.inputs['Metallic'].default_value = metal
    p.inputs['Sheen Weight'].default_value = sheen
    p.inputs['Sheen Tint'].default_value = (1, 1, 1, 1)
    if emit:
        p.inputs['Emission Color'].default_value = lin(emit)
        p.inputs['Emission Strength'].default_value = 1.5
    if weave:  # fine twill bump so the cloth reads as cloth
        tc = nt.nodes.new('ShaderNodeTexCoord')
        wave = nt.nodes.new('ShaderNodeTexWave')
        wave.inputs['Scale'].default_value = 420
        wave.inputs['Distortion'].default_value = 2
        noise = nt.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 900
        mix = nt.nodes.new('ShaderNodeMixRGB')
        bump = nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = 0.12
        nt.links.new(tc.outputs['Object'], wave.inputs['Vector'])
        nt.links.new(tc.outputs['Object'], noise.inputs['Vector'])
        nt.links.new(wave.outputs['Color'], mix.inputs[1])
        nt.links.new(noise.outputs['Color'], mix.inputs[2])
        nt.links.new(mix.outputs[0], bump.inputs['Height'])
        nt.links.new(bump.outputs[0], p.inputs['Normal'])
    return m


def fade(m, pairs):
    """pairs: [(frame, alpha), ...] keyed on the material's alpha"""
    a = m.node_tree.nodes['Principled BSDF'].inputs['Alpha']
    for f, v in pairs:
        a.default_value = v
        a.keyframe_insert('default_value', frame=f)


def link(obj, parent=None, m=None):
    sc.collection.objects.link(obj)
    if parent:
        obj.parent = parent
    if m:
        obj.data.materials.append(m)
    return obj


def apply_all(obj):
    bpy.context.view_layer.objects.active = obj
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    for md in list(obj.modifiers):
        bpy.ops.object.modifier_apply(modifier=md.name)


def skin(name, verts, edges, radii, parent=None, m=None, level=2, smooth=True):
    """A tube body from a vertex skeleton: Skin + Subsurf, applied."""
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, edges, [])
    ob = link(bpy.data.objects.new(name, me), None, None)
    ob.modifiers.new('skin', 'SKIN')
    if not me.skin_vertices:
        me.skin_vertices.new()
    for i, r in enumerate(radii):
        me.skin_vertices[0].data[i].radius = r
    me.skin_vertices[0].data[0].use_root = True
    sub = ob.modifiers.new('sub', 'SUBSURF')
    sub.levels = sub.render_levels = level
    apply_all(ob)
    if smooth:
        for poly in ob.data.polygons:
            poly.use_smooth = True
    if m:
        ob.data.materials.append(m)
    if parent:
        ob.parent = parent
    return ob


def prim(kind, name, loc, scale, parent=None, m=None, rot=(0, 0, 0), **kw):
    getattr(bpy.ops.mesh, 'primitive_%s_add' % kind)(location=loc, rotation=rot, **kw)
    ob = bpy.context.active_object
    ob.name = name
    ob.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    if m:
        ob.data.materials.append(m)
    if parent:  # parts are built around the origin, so local == world at build time
        ob.parent = parent
    return ob


def cut_v(ob, depth_y, top, bottom, half_w):
    """Boolean a V-shaped neckline out of the front of a garment."""
    me = bpy.data.meshes.new('wedge')
    v = [(-half_w, -1, top), (half_w, -1, top), (0, -1, bottom),
         (-half_w, depth_y, top), (half_w, depth_y, top), (0, depth_y, bottom)]
    me.from_pydata(v, [], [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)])
    w = link(bpy.data.objects.new('wedge', me))
    b = ob.modifiers.new('v', 'BOOLEAN')
    b.object = w
    b.solver = 'EXACT'
    apply_all(ob)
    bpy.data.objects.remove(w)


def bisect(ob, keep_positive):
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=(0, 0, 0), plane_no=(1, 0, 0),
                           clear_inner=keep_positive, clear_outer=not keep_positive)
    bm.to_mesh(ob.data)
    bm.free()


def thicken(ob, t=0.008):
    s = ob.modifiers.new('solid', 'SOLIDIFY')
    s.thickness = t
    s.offset = 1
    apply_all(ob)


# ---------- a man and his suit ----------
# skeleton (metres, z up, facing -y)
P = dict(pelvis=(0, 0, 1.0), waist=(0, 0, 1.15), chest=(0, 0, 1.33), neck=(0, 0, 1.53),
         sl=(-0.19, 0, 1.47), sr=(0.19, 0, 1.47), el=(-0.27, 0.02, 1.2), er=(0.27, 0.02, 1.2),
         wl=(-0.3, -0.04, 0.96), wr=(0.3, -0.04, 0.96))


def torso(name, lo, hi_neck, k, parent, m, arms=True, arm_end=1.0, shoulders=False):
    """Body-shaped garment. k scales every radius; arm_end < 1 shortens sleeves."""
    vs = [P['pelvis'], P['waist'], P['chest'], (0, 0, hi_neck)]
    rs = [(0.16 * k, 0.1 * k), (0.143 * k, 0.093 * k), (0.195 * k, 0.108 * k), (0.066 * k, 0.066 * k)]
    es = [(0, 1), (1, 2), (2, 3)]
    vs[0] = (0, 0, lo)
    if shoulders and not arms:  # a tailored shoulder line for the jacket body
        for s in ('sl', 'sr'):
            i = len(vs)
            vs.append((P[s][0] * 1.05, 0, P[s][2] + 0.01))
            rs.append((0.085 * k, 0.07 * k))
            es.append((2, i))
    if arms:
        for s, e, w in (('sl', 'el', 'wl'), ('sr', 'er', 'wr')):
            wx, wy, wz = P[w]
            ex, ey, ez = P[e]
            wrist = (ex + (wx - ex) * arm_end, ey + (wy - ey) * arm_end, ez + (wz - ez) * arm_end)
            i = len(vs)
            vs += [P[s], P[e], wrist]
            rs += [(0.07 * k, 0.07 * k), (0.05 * k, 0.05 * k), (0.042 * k, 0.042 * k)]
            es += [(2, i), (i, i + 1), (i + 1, i + 2)]
    return skin(name, vs, es, rs, parent, m)


def leg(name, side, k, parent, m):
    x = 0.095 * side
    hip = Vector((x, 0, 0.98))
    vs = [(0, 0, 0), (0, 0.01, -0.45), (0, 0.02, -0.9)]
    rs = [(0.088 * k, 0.088 * k), (0.062 * k, 0.062 * k), (0.052 * k, 0.052 * k)]
    pivot = bpy.data.objects.new(name + '_hip', None)
    link(pivot, parent)
    pivot.location = hip
    ob = skin(name, vs, [(0, 1), (1, 2)], rs, pivot, m)
    shoe = prim('cube', name + '_shoe', (0, 0, 0), (0.055, 0.13, 0.04), pivot, MAT['shoe'])
    shoe.location = (0, -0.05, -0.93)
    bev = shoe.modifiers.new('b', 'BEVEL'); bev.width = 0.03; bev.segments = 4
    return pivot, ob, shoe


MAT = {
    'shoe': mat('shoe', '#0a0a0a', 0.25, 0.0, False),
    'button': mat('button', '#1a1714', 0.3, 0.0, False),
    'brass': mat('brass', '#b08d57', 0.3, 0.0, False, metal=1.0),
    'skin': mat('skin', '#8a5d45', 0.55, 0.0, False),
    'shirt': mat('shirt', '#ece9e2', 0.7, 0.4),
    'tie': mat('tie', '#3a1016', 0.45, 0.5),
    'hat': mat('hat', '#121212', 0.85, 0.3),
    'ghost': mat('ghost', '#0b0f0d', 0.8, 0.0, False, emit='#9fb0a0'),
}


def man(name, cloth, origin, hero=False):
    """Builds one figure. Returns a dict of parts for animation."""
    root = bpy.data.objects.new(name, None)
    link(root)
    suit = mat(name + '_suit', cloth, 0.8, 0.28)
    vest = mat(name + '_vest', cloth, 0.7, 0.5)
    parts = {'root': root, 'suit': suit, 'vest': vest}

    shirt = torso(name + '_shirt', 0.92, 1.58, 1.0, root, MAT['shirt'], arm_end=1.04)
    collar = prim('torus', name + '_collar', (0, 0, 1.57), (1, 1, 1.6), root, MAT['shirt'],
                  major_radius=0.074, minor_radius=0.012)
    tie = prim('cube', name + '_tie', (0, -0.118, 1.38), (0.03, 0.006, 0.17), root, MAT['tie'])
    knot = prim('cube', name + '_knot', (0, -0.075, 1.545), (0.022, 0.012, 0.02), root, MAT['tie'], rot=(0.3, 0, 0))
    parts['shirt'] = [shirt, collar, tie, knot]

    w = torso(name + '_waistcoat', 0.96, 1.5, 1.07, root, vest, arms=False)
    cut_v(w, -0.06, 1.62, 1.27, 0.1)
    thicken(w, 0.006)
    wbtn = [prim('uv_sphere', name + '_wb%d' % i, (0, -0.122 - (0.006 if i > 2 else 0), 1.25 - i * 0.05),
                 (0.009, 0.005, 0.009), root, MAT['button'], segments=12, ring_count=8) for i in range(5)]
    parts['vest_parts'] = [w] + wbtn

    jt = torso(name + '_jacket', 0.8, 1.56, 1.17, None, suit, arms=False, shoulders=True)
    cut_v(jt, -0.05, 1.66, 1.13, 0.13)
    jl = jt.copy(); jl.data = jt.data.copy(); link(jl)
    bisect(jt, True); bisect(jl, False)
    for o in (jt, jl):
        thicken(o, 0.01)
        o.parent = root
    jt.name, jl.name = name + '_front_r', name + '_front_l'
    sleeves = []
    for side, (s, e, wr) in ((-1, ('sl', 'el', 'wl')), (1, ('sr', 'er', 'wr'))):
        vs = [P[s], P[e], P[wr]]
        sv = skin(name + '_sleeve%d' % side, vs, [(0, 1), (1, 2)],
                  [(0.094, 0.09), (0.066, 0.066), (0.056, 0.056)], root, suit)
        sleeves.append(sv)
        for i in range(4):  # cuff buttons
            t = 0.9 - i * 0.035
            p = Vector(P[e]).lerp(Vector(P[wr]), t)
            prim('uv_sphere', name + '_cb%d%d' % (side, i), (p.x + side * 0.05, p.y + 0.012, p.z), (0.008, 0.008, 0.008),
                 sv, MAT['button'], segments=12, ring_count=8)
    lap = []
    for side in (-1, 1):
        l = prim('cube', name + '_lapel%d' % side, (side * 0.07, -0.13, 1.42), (0.035, 0.004, 0.11), root, suit,
                 rot=(0.2, side * 0.25, side * 0.42))
        lap.append(l)
    pocket = prim('cube', name + '_square', (-0.11, -0.142, 1.36), (0.03, 0.003, 0.012), root, MAT['shirt'], rot=(0, 0, 0.15))
    jbtn = [prim('uv_sphere', name + '_jb%d' % i, (0, -0.145, 1.08 - i * 0.07), (0.012, 0.006, 0.012), root, MAT['button'],
                 segments=12, ring_count=8) for i in range(2)]
    parts['jacket'] = [jl, jt] + sleeves + lap + [pocket] + jbtn

    legs = [leg(name + '_leg%d' % s, s, 1.0, root, suit) for s in (-1, 1)]
    parts['legs'] = legs

    head = prim('uv_sphere', name + '_head', (0, -0.01, 1.73), (0.095, 0.11, 0.125), root, MAT['skin'] if not hero else mat(name + '_skin', '#8a5d45', 0.55, 0, False))
    neck = prim('cylinder', name + '_neck', (0, 0, 1.6), (0.05, 0.05, 0.06), root, head.data.materials[0])
    hands = [prim('uv_sphere', name + '_hand%d' % s, (s * 0.275, -0.035, 0.89), (0.04, 0.028, 0.06), root, head.data.materials[0])
             for s in (-1, 1)]
    hair = prim('uv_sphere', name + '_hair', (0, 0.005, 1.78), (0.1, 0.115, 0.09), root, MAT['shoe'])
    crown = prim('cylinder', name + '_crown', (0, -0.005, 1.83), (0.105, 0.12, 0.065), root, MAT['hat'])
    brim = prim('cylinder', name + '_brim', (0, -0.01, 1.775), (0.2, 0.215, 0.006), root, MAT['hat'], rot=(0.06, 0, 0))
    band = prim('cylinder', name + '_band', (0, -0.005, 1.785), (0.107, 0.122, 0.014), root, MAT['tie'])
    parts['body'] = [head, neck, hair, crown, brim, band] + hands
    root.location = origin
    return parts


hero = man('Hero', '#17191b', (0, 0, 0), hero=True)
others = [man('Grey', '#5d6266', (-1.3, 1.1, 0)), man('Cream', '#d8ccb4', (1.3, 1.0, 0)), man('Burgundy', '#4a1a22', (2.5, 2.2, 0))]

# ghost silhouette for the opening
ghost = torso('Ghost', 0.05, 1.6, 1.05, None, MAT['ghost'])
prim('uv_sphere', 'GhostHead', (0, 0, 1.74), (0.1, 0.115, 0.13), ghost, MAT['ghost'])

# ---------- stage ----------
bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, -0.0))
floor = bpy.context.active_object
fm = mat('floor', '#0c0e0d', 0.12, 0.0, False)
fn = fm.node_tree.nodes
rough = fn.new('ShaderNodeTexNoise'); rough.inputs['Scale'].default_value = 6
ramp = fn.new('ShaderNodeMapRange'); ramp.inputs['To Min'].default_value = 0.04; ramp.inputs['To Max'].default_value = 0.35
fm.node_tree.links.new(rough.outputs['Fac'], ramp.inputs['Value'])
fm.node_tree.links.new(ramp.outputs['Result'], fn['Principled BSDF'].inputs['Roughness'])
floor.data.materials.append(fm)

def light(kind, name, loc, energy, color='#ffffff', size=1.0, rot=(0, 0, 0)):
    d = bpy.data.lights.new(name, kind)
    d.energy = energy
    d.color = lin(color)[:3]
    if kind == 'SPOT':
        d.spot_size = math.radians(38); d.spot_blend = 0.6; d.shadow_soft_size = size
    elif kind == 'AREA':
        d.size = size
    else:
        d.shadow_soft_size = size
    o = bpy.data.objects.new(name, d)
    link(o)
    o.location = loc
    o.rotation_euler = rot
    return o

spot = light('SPOT', 'Key', (0.2, -0.6, 5.2), 2600, '#f2f0e6', 0.4, (math.radians(8), 0, 0))
rim = light('AREA', 'Rim', (0, 2.6, 2.6), 380, '#cfe0d0', 2.5, (math.radians(-60), 0, 0))
fill = light('AREA', 'Fill', (-2.5, -2.5, 1.6), 60, '#e8dcc8', 3, (math.radians(70), 0, math.radians(-45)))
# gas lamps for the street, dark until chapter 6
lamps = []
for i, (x, y) in enumerate([(-3.2, 4), (3.4, 6), (-3.6, 9), (3.8, 12), (-4, 15)]):
    pole = prim('cylinder', 'Pole%d' % i, (x, y, 1.6), (0.035, 0.035, 1.6), None, MAT['shoe'])
    key(pole, 1, hide_render=True); key(pole, 395, hide_render=False); key(pole, 480, hide_render=True)
    l = light('POINT', 'Lamp%d' % i, (x, y, 3.3), 0, '#ffb36b', 0.08)
    lamps.append(l)

# ---------- camera ----------
cam_d = bpy.data.cameras.new('Cam')
cam_d.lens = 50
cam_d.shift_x = -0.09  # subject sits right of centre, copy goes on the left
cam_d.dof.use_dof = True
cam_d.dof.aperture_fstop = 2.2
cam = link(bpy.data.objects.new('Cam', cam_d))
sc.camera = cam
target = link(bpy.data.objects.new('Target', None))
cam_d.dof.focus_object = target
tr = cam.constraints.new('TRACK_TO'); tr.target = target; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'

def shot(f, cam_loc, look):
    key(cam, f, location=Vector(cam_loc))
    key(target, f, location=Vector(look))

shot(1, (0, -7.5, 1.6), (0, 0, 1.25))
shot(60, (0, -5.6, 1.5), (0, 0, 1.25))
shot(130, (0.5, -3.2, 1.45), (0, 0, 1.25))
shot(200, (-0.6, -3.0, 1.4), (0, 0, 1.22))
shot(290, (0.3, -3.6, 1.35), (0, 0, 1.15))
shot(340, (0.9, -4.6, 1.3), (0, 0, 1.0))
shot(400, (0.2, -4.2, 1.6), (0, 0, 1.3))
shot(470, (0.2, -4.6, 1.35), (0.1, -1.6, 1.1))
shot(505, (0.95, -2.05, 1.08), (0.33, -1.74, 0.98))
shot(535, (0.72, -1.93, 1.03), (0.33, -1.74, 0.98))
key(cam_d.dof, 470, aperture_fstop=2.2); key(cam_d.dof, 500, aperture_fstop=4.5)

# ---------- choreography ----------
F = {'shirt': 60, 'vest': 130, 'jacket': 200, 'cut': 290, 'man': 340, 'walk': 400, 'detail': 470}

def hide_until(objs, f, mats=None):
    for o in objs:
        key(o, f - 1, hide_render=True)
        key(o, f, hide_render=False)

fade(MAT['ghost'], [(1, 0.0), (14, 0.0), (40, 0.28), (62, 0.28), (82, 0.0)])
key(ghost, 1, hide_render=False); key(ghost, 84, hide_render=True)

# 1. the shirt floats down and turns into the light
hide_until(hero['shirt'], F['shirt'])
key(hero['root'], 1, location=Vector((0, 0, 0.22)), rotation_euler=Euler((0, 0, math.radians(-35))))
key(hero['root'], F['shirt'], location=Vector((0, 0, 0.22)), rotation_euler=Euler((0, 0, math.radians(-35))))
key(hero['root'], F['vest'], location=Vector((0, 0, 0.08)), rotation_euler=Euler((0, 0, math.radians(8))))
fade(MAT['shirt'], [(F['shirt'], 0), (F['shirt'] + 30, 1)])

# 2. waistcoat flies in from behind the camera
def fly(objs, f0, f1, spread, spin=40):
    for o in objs:
        home = o.location.copy()
        r0 = o.rotation_euler.copy()
        off = Vector((random.choice((-1, 1)) * random.uniform(0.5, 1) * spread, random.uniform(0.1, 0.9) * spread, random.uniform(-0.4, 0.7) * spread))
        key(o, f0 - 1, hide_render=True)
        key(o, f0, hide_render=False)
        key(o, f0, location=home + off,
            rotation_euler=Euler((r0.x + math.radians(random.uniform(-spin, spin)), r0.y + math.radians(random.uniform(-spin, spin)),
                                  r0.z + math.radians(random.uniform(-spin, spin)))))
        key(o, f1 + random.randint(-6, 6), location=home, rotation_euler=r0)

fly(hero['vest_parts'][:1], F['vest'], F['vest'] + 50, 2.2, 50)
fly(hero['vest_parts'][1:], F['vest'] + 30, F['vest'] + 62, 0.5, 0)
key(hero['root'], F['jacket'], location=Vector((0, 0, 0.05)), rotation_euler=Euler((0, 0, math.radians(-12))))

# 3. jacket: exploded view, then everything locks together
fly(hero['jacket'], F['jacket'], F['jacket'] + 72, 1.3, 70)
key(hero['root'], F['cut'], location=Vector((0, 0, 0.0)), rotation_euler=Euler((0, 0, math.radians(14))))

# 4. trousers rise into place; the full cut turns
for pivot, l, shoe in hero['legs']:
    key(pivot, F['cut'] - 1, hide_render=True)
    key(pivot, F['cut'], hide_render=False, location=pivot.location + Vector((0, 0, -1.2)))
    key(pivot, F['cut'] + 34, location=pivot.location.copy() + Vector((0, 0, 1.2)))
    for o in (l, shoe):
        key(o, F['cut'] - 1, hide_render=True); key(o, F['cut'], hide_render=False)
key(hero['root'], F['man'], rotation_euler=Euler((0, 0, math.radians(-4))))

# 5. the man fills the suit
hide_until(hero['body'], F['man'])
skin_m = hero['body'][0].data.materials[0]
fade(skin_m, [(F['man'], 0), (F['man'] + 36, 1)])
key(hero['root'], F['walk'], rotation_euler=Euler((0, 0, 0)))

# 6. they walk toward camera on a wet street
def walk(parts, f0, f1, start, end, phase=0.0):
    root = parts['root']
    key(root, f0, location=Vector(start))
    root.keyframe_insert('location', frame=f0)
    for f in range(f0, f1 + 1, 3):
        t = (f - f0) / (f1 - f0)
        pos = Vector(start).lerp(Vector(end), t)
        step = math.sin((f - f0) / 24 * math.pi * 2 * 0.95 + phase)
        pos.z = start[2] + abs(step) * 0.025
        root.location = pos
        root.keyframe_insert('location', frame=f)
        for (pivot, _, _), s in zip(parts['legs'], (1, -1)):
            pivot.rotation_euler = Euler((math.radians(22) * step * s, 0, 0))
            pivot.keyframe_insert('rotation_euler', frame=f)
    for pivot, _, _ in parts['legs']:  # settle feet together after the walk
        pivot.rotation_euler = Euler((0, 0, 0)); pivot.keyframe_insert('rotation_euler', frame=f1 + 8)

walk(hero, F['walk'], F['detail'] - 4, (0, 0, 0), (0, -1.7, 0))
for i, o in enumerate(others):
    o['root'].hide_render = True
    o['root'].keyframe_insert('hide_render', frame=1)
    for part in o['root'].children_recursive:
        part.hide_render = True; part.keyframe_insert('hide_render', frame=1)
        part.hide_render = False; part.keyframe_insert('hide_render', frame=F['walk'])
    o['root'].hide_render = False; o['root'].keyframe_insert('hide_render', frame=F['walk'])
    sx, sy, _ = o['root'].location
    walk(o, F['walk'], F['detail'] - 4, (sx, sy + 1.6, 0), (sx * 0.85, sy - 1.2, 0), phase=0.8 * (i + 1))
    for part in o['root'].children_recursive:  # leave once we push into the cuff
        part.keyframe_insert('hide_render', frame=F['detail'] + 10)
        part.hide_render = True; part.keyframe_insert('hide_render', frame=F['detail'] + 11)
for l in lamps:
    key(l.data, F['walk'] - 10, energy=0)
    key(l.data, F['walk'] + 25, energy=180)
    key(l.data, F['detail'] + 10, energy=180)
    key(l.data, F['detail'] + 30, energy=0)
key(floor.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['Base Color'], F['walk'] - 10, default_value=lin('#0c0e0d'))

# 7. a small light to model the cuff, then fade out
cuff = light('AREA', 'Cuff', (0.9, -2.3, 1.4), 0, '#f2ece0', 0.6, (math.radians(65), 0, math.radians(60)))
key(cuff.data, F['detail'], energy=0); key(cuff.data, F['detail'] + 20, energy=14); key(cuff.data, F['detail'] + 52, energy=14); key(cuff.data, TOTAL, energy=0)
# fade out
for l, e in ((spot, 2600), (rim, 380), (fill, 60)):
    key(l.data, F['detail'] + 52, energy=e)
    key(l.data, TOTAL, energy=0)
bg = wn['Background'].inputs['Strength']
key(bg, F['detail'] + 52, default_value=1.0); key(bg, TOTAL, default_value=0.0)

# ---------- render ----------
sc.render.filepath = OUT.rstrip('/\\') + '/'
if ONLY:
    for f in ONLY:
        sc.frame_set(f)
        sc.render.filepath = OUT.rstrip('/\\') + '/%04d' % f
        bpy.ops.render.render(write_still=True)
else:
    sc.render.filepath = OUT.rstrip('/\\') + '/'
    bpy.ops.render.render(animation=True)
