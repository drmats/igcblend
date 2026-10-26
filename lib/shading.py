#!/usr/bin/env python
# -*- coding: utf-8 -*-
# type: ignore

"""
https://github.com/drmats
"""

import bpy
import mathutils




# Node Group: Height-dependent (Z-axis) texturing.
# input 1: color
# input 2: color
# input 3: min float
# input 4: max float
# output: color
def create_dualheighttexture_node_group (
    name = "DualHeightTexture",
    transition: float = 0.2,
) -> bpy.types.NodeTree:
    # node group
    dualheighttexture = bpy.data.node_groups.get(name)

    # in-place update for existing node group (don't touch interface)
    if dualheighttexture is not None:
        dualheighttexture.links.clear()
        dualheighttexture.nodes.clear()

    # create new node group if non-existent
    else:
        dualheighttexture = bpy.data.node_groups.new(
            type = "ShaderNodeTree",
            name = name,
        )
        dualheighttexture.color_tag = "NONE"
        dualheighttexture.description = ""
        dualheighttexture.default_group_node_width = 140

        # input socket: Color
        in_color_socket_1 = dualheighttexture.interface.new_socket(
            name = "Color",
            in_out = "INPUT",
            socket_type = "NodeSocketColor",
        )
        in_color_socket_1.default_value = (0.8, 0.8, 0.8, 1.0)
        in_color_socket_1.attribute_domain = "POINT"
        in_color_socket_1.default_input = "VALUE"
        in_color_socket_1.structure_type = "AUTO"

        # input socket: Color
        in_color_socket_2 = dualheighttexture.interface.new_socket(
            name = "Color",
            in_out = "INPUT",
            socket_type = "NodeSocketColor",
        )
        in_color_socket_2.default_value = (0.8, 0.8, 0.8, 1.0)
        in_color_socket_2.attribute_domain = "POINT"
        in_color_socket_2.default_input = "VALUE"
        in_color_socket_2.structure_type = "AUTO"

        # input socket: Min
        in_min_socket = dualheighttexture.interface.new_socket(
            name = "Min",
            in_out = "INPUT",
            socket_type = "NodeSocketFloat",
        )
        in_min_socket.default_value = 0.0
        in_min_socket.min_value = -10000.0
        in_min_socket.max_value = 10000.0
        in_min_socket.subtype = "NONE"
        in_min_socket.attribute_domain = "POINT"
        in_min_socket.default_input = "VALUE"
        in_min_socket.structure_type = "AUTO"

        # input socket: Max
        in_max_socket = dualheighttexture.interface.new_socket(
            name = "Max",
            in_out = "INPUT",
            socket_type = "NodeSocketFloat",
        )
        in_max_socket.default_value = 2000.0
        in_max_socket.min_value = -10000.0
        in_max_socket.max_value = 10000.0
        in_max_socket.subtype = "NONE"
        in_max_socket.attribute_domain = "POINT"
        in_max_socket.default_input = "VALUE"
        in_max_socket.structure_type = "AUTO"

        # output socket: Color
        out_color_socket = dualheighttexture.interface.new_socket(
            name = "Color",
            in_out = "OUTPUT",
            socket_type = "NodeSocketColor",
        )
        out_color_socket.default_value = (0.8, 0.8, 0.8, 1.0)
        out_color_socket.attribute_domain = "POINT"
        out_color_socket.default_input = "VALUE"
        out_color_socket.structure_type = "AUTO"

    # shortcuts
    nodes = dualheighttexture.nodes
    links = dualheighttexture.links

    # node: Group Input
    group_input = nodes.new("NodeGroupInput")
    group_input.name = "Group Input"
    group_input.show_options = True

    # node: Texture Coordinate
    texture_coordinate = nodes.new("ShaderNodeTexCoord")
    texture_coordinate.name = "Texture Coordinate"
    texture_coordinate.show_options = True
    texture_coordinate.from_instancer = False

    # node: Mix
    mix = nodes.new("ShaderNodeMix")
    mix.name = "Mix"
    mix.show_options = True
    mix.blend_type = "MIX"
    mix.clamp_factor = True
    mix.clamp_result = False
    mix.data_type = "RGBA"
    mix.factor_mode = "UNIFORM"

    # node: Separate XYZ
    separate_xyz = nodes.new("ShaderNodeSeparateXYZ")
    separate_xyz.name = "Separate XYZ"
    separate_xyz.show_options = True

    # node: Map Range
    map_range_001 = nodes.new("ShaderNodeMapRange")
    map_range_001.name = "Map Range"
    map_range_001.show_options = True
    map_range_001.clamp = True
    map_range_001.data_type = "FLOAT"
    map_range_001.interpolation_type = "LINEAR"
    map_range_001.inputs[3].default_value = 0.0 # to min
    map_range_001.inputs[4].default_value = 1.0 # to max

    # node: Color Ramp
    color_ramp = nodes.new("ShaderNodeValToRGB")
    color_ramp.name = "Color Ramp"
    color_ramp.show_options = True
    color_ramp.color_ramp.color_mode = "RGB"
    color_ramp.color_ramp.hue_interpolation = "NEAR"
    color_ramp.color_ramp.interpolation = "LINEAR"
    color_ramp.color_ramp.elements.remove(color_ramp.color_ramp.elements[0])
    color_ramp_cre_0 = color_ramp.color_ramp.elements[0]
    color_ramp_cre_0.position = 0.5 - transition / 2
    color_ramp_cre_0.alpha = 1.0
    color_ramp_cre_0.color = (1.0, 1.0, 1.0, 1.0)
    color_ramp_cre_1 = color_ramp.color_ramp.elements.new(0.5 + transition / 2)
    color_ramp_cre_1.alpha = 1.0
    color_ramp_cre_1.color = (0.0, 0.0, 0.0, 1.0)

    # node: Group Output
    group_output = nodes.new("NodeGroupOutput")
    group_output.name = "Group Output"
    group_output.show_options = True
    group_output.is_active_output = True

    # locations
    nodes["Group Input"].location = (-1213.0, 257.0)
    nodes["Texture Coordinate"].location = (-1207.0, 537.0)
    nodes["Mix"].location = (-104.0, 402.0)
    nodes["Separate XYZ"].location = (-954.0, 432.0)
    nodes["Map Range"].location = (-695.0, 169.0)
    nodes["Color Ramp"].location = (-457.0, 465.0)
    nodes["Group Output"].location = (126.0, 287.0)

    # dimensions
    nodes["Group Input"].width  = 140.0
    nodes["Group Input"].height = 100.0
    nodes["Texture Coordinate"].width  = 140.0
    nodes["Texture Coordinate"].height = 100.0
    nodes["Mix"].width  = 140.0
    nodes["Mix"].height = 100.0
    nodes["Separate XYZ"].width  = 140.0
    nodes["Separate XYZ"].height = 100.0
    nodes["Map Range"].width  = 168.0
    nodes["Map Range"].height = 100.0
    nodes["Color Ramp"].width  = 240.0
    nodes["Color Ramp"].height = 100.0
    nodes["Group Output"].width  = 140.0
    nodes["Group Output"].height = 100.0

    # links
    links.new(
        nodes["Group Input"].outputs[0],
        nodes["Mix"].inputs[6],
    )
    links.new(
        nodes["Group Input"].outputs[1],
        nodes["Mix"].inputs[7],
    )
    links.new(
        nodes["Group Input"].outputs[2],
        nodes["Map Range"].inputs[1],
    )
    links.new(
        nodes["Group Input"].outputs[3],
        nodes["Map Range"].inputs[2],
    )
    links.new(
        nodes["Texture Coordinate"].outputs[3],
        nodes["Separate XYZ"].inputs[0],
    )
    links.new(
        nodes["Separate XYZ"].outputs[2],
        nodes["Map Range"].inputs[0],
    )
    links.new(
        nodes["Map Range"].outputs[0],
        nodes["Color Ramp"].inputs[0],
    )
    links.new(
        nodes["Color Ramp"].outputs[0],
        nodes["Mix"].inputs[0],
    )
    links.new(
        nodes["Mix"].outputs[2],
        nodes["Group Output"].inputs[0],
    )

    return dualheighttexture




# Node Group: Emission mixed with Diffuse BDSF for shadows
# input: color
# output: shader
def create_emissionshadow_node_group (
    name = "EmissionShadow",
    mix: float = 0.75,
) -> bpy.types.NodeTree:
    # node group
    emissionshadow = bpy.data.node_groups.get(name)

    # in-place update for existing node group (don't touch interface)
    if emissionshadow is not None:
        emissionshadow.links.clear()
        emissionshadow.nodes.clear()

    # create new node group if non-existent
    else:
        emissionshadow = bpy.data.node_groups.new(
            type = "ShaderNodeTree",
            name = name,
        )
        emissionshadow.color_tag = "NONE"
        emissionshadow.description = ""
        emissionshadow.default_group_node_width = 140

        # input socket: Color
        in_color_socket = emissionshadow.interface.new_socket(
            name = "Color",
            in_out = "INPUT",
            socket_type = "NodeSocketColor",
        )
        in_color_socket.default_value = (0.8, 0.8, 0.8, 1.0)
        in_color_socket.attribute_domain = "POINT"
        in_color_socket.default_input = "VALUE"
        in_color_socket.structure_type = "AUTO"

        # output socket: Shader
        out_shader_socket = emissionshadow.interface.new_socket(
            name = "Shader",
            in_out = "OUTPUT",
            socket_type = "NodeSocketShader",
        )
        out_shader_socket.attribute_domain = "POINT"
        out_shader_socket.default_input = "VALUE"
        out_shader_socket.structure_type = "AUTO"

    # shortcuts
    nodes = emissionshadow.nodes
    links = emissionshadow.links

    # node: Group Input
    group_input = nodes.new("NodeGroupInput")
    group_input.name = "Group Input"
    group_input.show_options = True

    # node: Emission
    emission = nodes.new("ShaderNodeEmission")
    emission.name = "Emission"
    emission.show_options = True
    emission.inputs[1].default_value = 1.0 # strength

    # node: Diffuse BSDF
    diffuse_bsdf = nodes.new("ShaderNodeBsdfDiffuse")
    diffuse_bsdf.name = "Diffuse BSDF"
    diffuse_bsdf.show_options = True
    diffuse_bsdf.inputs[1].default_value = 0.0 # roughness
    diffuse_bsdf.inputs[2].default_value = (0.0, 0.0, 0.0) # normal

    # node: Mix Shader
    mix_shader = nodes.new("ShaderNodeMixShader")
    mix_shader.name = "Mix Shader"
    mix_shader.show_options = True
    mix_shader.inputs[0].default_value = mix # fac

    # node: Group Output
    group_output = nodes.new("NodeGroupOutput")
    group_output.name = "Group Output"
    group_output.show_options = True
    group_output.is_active_output = True

    # locations
    nodes["Group Input"].location = (-398.0, 2.0)
    nodes["Emission"].location = (-160.0, 95.0)
    nodes["Diffuse BSDF"].location = (-160.0, -111.0)
    nodes["Mix Shader"].location = (93.0, 45.0)
    nodes["Group Output"].location = (293.0, 32.0)

    # dimensions
    nodes["Group Input"].width  = 140.0
    nodes["Group Input"].height = 100.0
    nodes["Emission"].width  = 140.0
    nodes["Emission"].height = 100.0
    nodes["Diffuse BSDF"].width  = 160.0
    nodes["Diffuse BSDF"].height = 100.0
    nodes["Mix Shader"].width  = 140.0
    nodes["Mix Shader"].height = 100.0
    nodes["Group Output"].width  = 140.0
    nodes["Group Output"].height = 100.0

    # links
    links.new(
        nodes["Group Input"].outputs[0],
        nodes["Emission"].inputs[0],
    )
    links.new(
        nodes["Group Input"].outputs[0],
        nodes["Diffuse BSDF"].inputs[0],
    )
    links.new(
        nodes["Emission"].outputs[0],
        nodes["Mix Shader"].inputs[1],
    )
    links.new(
        nodes["Diffuse BSDF"].outputs[0],
        nodes["Mix Shader"].inputs[2],
    )
    links.new(
        nodes["Mix Shader"].outputs[0],
        nodes["Group Output"].inputs[0],
    )

    return emissionshadow




# Material based on three images.
def create_terrain_material (
    top_image_path: str,
    middle_image_path: str,
    bottom_image_path: str,
    uv_map_name: str = "UVMap",
    min_point: float = 0.0,
    middle_point: float = 1300.0,
    max_point: float = 2200.0,
    emission_shadow_mix: float = 0.75,
    height_texture_transition: float = 0.2,
    name: str = "TerrainMaterial",
) -> bpy.types.Material:
    # material
    terrainmaterial = bpy.data.materials.get(name)

    # in-place update
    if terrainmaterial is not None:
        terrainmaterial.node_tree.links.clear()
        terrainmaterial.node_tree.nodes.clear()

    # create new if non-existent
    else:
        terrainmaterial = bpy.data.materials.new(name)
        if bpy.app.version < (5, 0, 0):
            terrainmaterial.use_nodes = True
        terrainmaterial.node_tree.color_tag = "NONE"
        terrainmaterial.node_tree.description = ""
        terrainmaterial.node_tree.default_group_node_width = 140

    # load images
    top_image = bpy.data.images.load(
        top_image_path,
        check_existing = True,
    )
    middle_image = bpy.data.images.load(
        middle_image_path,
        check_existing = True,
    )
    bottom_image = bpy.data.images.load(
        bottom_image_path,
        check_existing = True,
    )

    # ensure existence of node groups
    dualheighttexture = create_dualheighttexture_node_group(
        transition = height_texture_transition,
    )
    emissionshadow = create_emissionshadow_node_group(
        mix = emission_shadow_mix,
    )

    # shortcuts
    nodes = terrainmaterial.node_tree.nodes
    links = terrainmaterial.node_tree.links

    # remove all nodes
    for node in nodes:
        nodes.remove(node)

    # node: UV Map
    uv_map = nodes.new("ShaderNodeUVMap")
    uv_map.name = "UV Map"
    uv_map.show_options = True
    uv_map.from_instancer = False
    uv_map.uv_map = uv_map_name

    # node: Image Texture Top
    image_texture_top = nodes.new("ShaderNodeTexImage")
    image_texture_top.name = "Image Texture Top"
    image_texture_top.show_options = True
    image_texture_top.show_texture = True
    image_texture_top.extension = "CLIP"
    image_texture_top.image = top_image
    image_texture_top.image_user.frame_current = 1
    image_texture_top.image_user.frame_duration = 1
    image_texture_top.image_user.frame_offset = 16
    image_texture_top.image_user.frame_start = 1
    image_texture_top.image_user.tile = 0
    image_texture_top.image_user.use_auto_refresh = False
    image_texture_top.image_user.use_cyclic = False
    image_texture_top.interpolation = "Smart"
    image_texture_top.projection = "FLAT"
    image_texture_top.projection_blend = 0.0

    # node: Image Texture Middle
    image_texture_middle = nodes.new("ShaderNodeTexImage")
    image_texture_middle.name = "Image Texture Middle"
    image_texture_middle.show_options = True
    image_texture_middle.extension = "CLIP"
    image_texture_middle.image = middle_image
    image_texture_middle.image_user.frame_current = 0
    image_texture_middle.image_user.frame_duration = 1
    image_texture_middle.image_user.frame_offset = 16
    image_texture_middle.image_user.frame_start = 1
    image_texture_middle.image_user.tile = 0
    image_texture_middle.image_user.use_auto_refresh = False
    image_texture_middle.image_user.use_cyclic = False
    image_texture_middle.interpolation = "Linear"
    image_texture_middle.projection = "FLAT"
    image_texture_middle.projection_blend = 0.0

    # node: Middle Image HSV
    middle_image_hsv = nodes.new("ShaderNodeHueSaturation")
    middle_image_hsv.name = "Middle Image HSV"
    middle_image_hsv.show_options = True
    middle_image_hsv.inputs[0].default_value = 0.450 # hue
    middle_image_hsv.inputs[1].default_value = 1.0 # saturation
    middle_image_hsv.inputs[2].default_value = 1.0 # value
    middle_image_hsv.inputs[3].default_value = 1.0 # fac

    # node: Image Texture Bottom
    image_texture_bottom = nodes.new("ShaderNodeTexImage")
    image_texture_bottom.name = "Image Texture Bottom"
    image_texture_bottom.show_options = True
    image_texture_bottom.extension = "CLIP"
    image_texture_bottom.image = bottom_image
    image_texture_bottom.image_user.frame_current = 0
    image_texture_bottom.image_user.frame_duration = 100
    image_texture_bottom.image_user.frame_offset = 0
    image_texture_bottom.image_user.frame_start = 1
    image_texture_bottom.image_user.tile = 0
    image_texture_bottom.image_user.use_auto_refresh = False
    image_texture_bottom.image_user.use_cyclic = False
    image_texture_bottom.interpolation = "Linear"
    image_texture_bottom.projection = "FLAT"
    image_texture_bottom.projection_blend = 0.0

    # node: Bottom Image Curves
    bottom_image_curves = nodes.new("ShaderNodeRGBCurve")
    bottom_image_curves.name = "Bottom Image Curves"
    bottom_image_curves.show_options = True
    bottom_image_curves.mapping.extend = "EXTRAPOLATED"
    bottom_image_curves.mapping.tone = "STANDARD"
    bottom_image_curves.mapping.black_level = (0.0, 0.0, 0.0)
    bottom_image_curves.mapping.white_level = (1.0, 1.0, 1.0)
    bottom_image_curves.mapping.clip_min_x = 0.0
    bottom_image_curves.mapping.clip_min_y = 0.0
    bottom_image_curves.mapping.clip_max_x = 1.0
    bottom_image_curves.mapping.clip_max_y = 1.0
    bottom_image_curves.mapping.use_clip = True
    bottom_image_curves_curve_0 = bottom_image_curves.mapping.curves[0]
    bottom_image_curves_curve_0_point_0 = bottom_image_curves_curve_0.points[0]
    bottom_image_curves_curve_0_point_0.location = (0.0, 0.0)
    bottom_image_curves_curve_0_point_0.handle_type = "AUTO"
    bottom_image_curves_curve_0_point_1 = bottom_image_curves_curve_0.points[1]
    bottom_image_curves_curve_0_point_1.location = (1.0, 1.0)
    bottom_image_curves_curve_0_point_1.handle_type = "AUTO"
    bottom_image_curves_curve_1 = bottom_image_curves.mapping.curves[1]
    bottom_image_curves_curve_1_point_0 = bottom_image_curves_curve_1.points[0]
    bottom_image_curves_curve_1_point_0.location = (0.0, 0.0)
    bottom_image_curves_curve_1_point_0.handle_type = "AUTO"
    bottom_image_curves_curve_1_point_1 = bottom_image_curves_curve_1.points[1]
    bottom_image_curves_curve_1_point_1.location = (1.0, 1.0)
    bottom_image_curves_curve_1_point_1.handle_type = "AUTO"
    bottom_image_curves_curve_2 = bottom_image_curves.mapping.curves[2]
    bottom_image_curves_curve_2_point_0 = bottom_image_curves_curve_2.points[0]
    bottom_image_curves_curve_2_point_0.location = (0.0, 0.0)
    bottom_image_curves_curve_2_point_0.handle_type = "AUTO"
    bottom_image_curves_curve_2_point_1 = bottom_image_curves_curve_2.points[1]
    bottom_image_curves_curve_2_point_1.location = (0.55, 0.30)
    bottom_image_curves_curve_2_point_1.handle_type = "AUTO"
    bottom_image_curves_curve_2_point_2 = bottom_image_curves_curve_2.points.new(1.0, 1.0)
    bottom_image_curves_curve_2_point_2.handle_type = "AUTO"
    bottom_image_curves_curve_3 = bottom_image_curves.mapping.curves[3]
    bottom_image_curves_curve_3_point_0 = bottom_image_curves_curve_3.points[0]
    bottom_image_curves_curve_3_point_0.location = (0.0, 0.0)
    bottom_image_curves_curve_3_point_0.handle_type = "AUTO"
    bottom_image_curves_curve_3_point_1 = bottom_image_curves_curve_3.points[1]
    bottom_image_curves_curve_3_point_1.location = (0.65, 0.25)
    bottom_image_curves_curve_3_point_1.handle_type = "AUTO"
    bottom_image_curves_curve_3_point_2 = bottom_image_curves_curve_3.points.new(1.0, 1.0)
    bottom_image_curves_curve_3_point_2.handle_type = "AUTO"
    bottom_image_curves.mapping.update()
    bottom_image_curves.inputs[0].default_value = 1.0 # fac

    # node: Bottom Image HSV
    bottom_image_hsv = nodes.new("ShaderNodeHueSaturation")
    bottom_image_hsv.name = "Bottom Image HSV"
    bottom_image_hsv.show_options = True
    bottom_image_hsv.inputs[0].default_value = 0.55 # hue
    bottom_image_hsv.inputs[1].default_value = 0.90 # saturation
    bottom_image_hsv.inputs[2].default_value = 0.50 # value
    bottom_image_hsv.inputs[3].default_value = 1.0 # fac

    # node: Upper Dual Height Texture
    group_001 = nodes.new("ShaderNodeGroup")
    group_001.name = "Upper Dual Height Texture"
    group_001.show_options = True
    group_001.node_tree = dualheighttexture
    group_001.inputs[2].default_value = min_point
    group_001.inputs[3].default_value = max_point

    # node: Lower Dual Height Texture
    group_002 = nodes.new("ShaderNodeGroup")
    group_002.name = "Lower Dual Height Texture"
    group_002.show_options = True
    group_002.node_tree = dualheighttexture
    group_002.inputs[2].default_value = 0.0
    group_002.inputs[3].default_value = middle_point

    # node: Outer Emission Shadow
    group_003 = nodes.new("ShaderNodeGroup")
    group_003.name = "Outer Emission Shadow"
    group_003.show_options = True
    group_003.node_tree = emissionshadow

    # node: Material Output
    material_output = nodes.new("ShaderNodeOutputMaterial")
    material_output.name = "Material Output"
    material_output.show_options = True
    material_output.is_active_output = True
    material_output.target = "ALL"
    material_output.inputs[2].default_value = (0.0, 0.0, 0.0) # displacement
    material_output.inputs[3].default_value = 0.0 # thickness

    # locations
    nodes["UV Map"].location = (-1131.0, -705.0)
    nodes["Image Texture Top"].location = (-770.0, -345.0)
    nodes["Image Texture Middle"].location = (-770.0, -638.0)
    nodes["Middle Image HSV"].location = (-338.0, -729.0)
    nodes["Image Texture Bottom"].location = (-768.0, -940.0)
    nodes["Bottom Image Curves"].location = (-398.0, -930.0)
    nodes["Bottom Image HSV"].location = (-7.0, -1119.0)
    nodes["Upper Dual Height Texture"].location = (2.0, -591.0)
    nodes["Lower Dual Height Texture"].location = (267.0, -824.0)
    nodes["Outer Emission Shadow"].location = (480.0, -849.0)
    nodes["Material Output"].location = (711.0, -852.0)

    # dimensions
    nodes["UV Map"].width  = 160.0
    nodes["UV Map"].height = 100.0
    nodes["Image Texture Top"].width  = 240.0
    nodes["Image Texture Top"].height = 100.0
    nodes["Image Texture Middle"].width  = 240.0
    nodes["Image Texture Middle"].height = 100.0
    nodes["Middle Image HSV"].width  = 160.0
    nodes["Middle Image HSV"].height = 100.0
    nodes["Image Texture Bottom"].width  = 240.0
    nodes["Image Texture Bottom"].height = 100.0
    nodes["Bottom Image Curves"].width  = 240.0
    nodes["Bottom Image Curves"].height = 100.0
    nodes["Bottom Image HSV"].width  = 160.0
    nodes["Bottom Image HSV"].height = 100.0
    nodes["Upper Dual Height Texture"].width  = 140.0
    nodes["Upper Dual Height Texture"].height = 100.0
    nodes["Lower Dual Height Texture"].width  = 140.0
    nodes["Lower Dual Height Texture"].height = 100.0
    nodes["Outer Emission Shadow"].width  = 140.0
    nodes["Outer Emission Shadow"].height = 100.0
    nodes["Material Output"].width  = 140.0
    nodes["Material Output"].height = 100.0

    # links
    links.new(
        nodes["UV Map"].outputs[0],
        nodes["Image Texture Top"].inputs[0],
    )
    links.new(
        nodes["UV Map"].outputs[0],
        nodes["Image Texture Middle"].inputs[0],
    )
    links.new(
        nodes["UV Map"].outputs[0],
        nodes["Image Texture Bottom"].inputs[0],
    )
    links.new(
        nodes["Image Texture Top"].outputs[0],
        nodes["Upper Dual Height Texture"].inputs[0],
    )
    links.new(
        nodes["Image Texture Middle"].outputs[0],
        nodes["Middle Image HSV"].inputs[4],
    )
    links.new(
        nodes["Middle Image HSV"].outputs[0],
        nodes["Upper Dual Height Texture"].inputs[1],
    )
    links.new(
        nodes["Image Texture Bottom"].outputs[0],
        nodes["Bottom Image Curves"].inputs[1],
    )
    links.new(
        nodes["Bottom Image Curves"].outputs[0],
        nodes["Bottom Image HSV"].inputs[4],
    )
    links.new(
        nodes["Upper Dual Height Texture"].outputs[0],
        nodes["Lower Dual Height Texture"].inputs[0],
    )
    links.new(
        nodes["Bottom Image HSV"].outputs[0],
        nodes["Lower Dual Height Texture"].inputs[1],
    )
    links.new(
        nodes["Lower Dual Height Texture"].outputs[0],
        nodes["Outer Emission Shadow"].inputs[0],
    )
    links.new(
        nodes["Outer Emission Shadow"].outputs[0],
        nodes["Material Output"].inputs[0],
    )

    return terrainmaterial




# simple, solid color material.
def create_simple_color_material (
    base_color: tuple[float, float, float, float] = (
        *mathutils.Color((1.0, 0.6, 0.0)).from_srgb_to_scene_linear(), 1.0
    ),
    name: str = "SimpleOrange",
) -> bpy.types.Material:
    # material
    simplecolormaterial = bpy.data.materials.get(name)

    # in-place update
    if simplecolormaterial is not None:
        simplecolormaterial.node_tree.links.clear()
        simplecolormaterial.node_tree.nodes.clear()

    # create new if non-existent
    else:
        simplecolormaterial = bpy.data.materials.new(name)
        if bpy.app.version < (5, 0, 0):
            simplecolormaterial.use_nodes = True
        simplecolormaterial.node_tree.color_tag = "NONE"
        simplecolormaterial.node_tree.description = ""
        simplecolormaterial.node_tree.default_group_node_width = 140

    # shortcuts
    nodes = simplecolormaterial.node_tree.nodes
    links = simplecolormaterial.node_tree.links

    # remove all nodes
    for node in nodes:
        nodes.remove(node)

    # defaults
    simplecolormaterial.alpha_threshold = 0.5
    simplecolormaterial.line_priority = 0
    simplecolormaterial.max_vertex_displacement = 0.0
    simplecolormaterial.metallic = 0.0
    simplecolormaterial.paint_active_slot = 0
    simplecolormaterial.paint_clone_slot = 0
    simplecolormaterial.pass_index = 0
    simplecolormaterial.refraction_depth = 0.0
    simplecolormaterial.roughness = 0.4
    simplecolormaterial.show_transparent_back = True
    simplecolormaterial.specular_intensity = 0.5
    simplecolormaterial.use_backface_culling = False
    simplecolormaterial.use_backface_culling_lightprobe_volume = True
    simplecolormaterial.use_backface_culling_shadow = False
    simplecolormaterial.use_preview_world = False
    simplecolormaterial.use_raytrace_refraction = False
    simplecolormaterial.use_screen_refraction = False
    simplecolormaterial.use_sss_translucency = False
    simplecolormaterial.use_thickness_from_shadow = False
    simplecolormaterial.use_transparency_overlap = True
    simplecolormaterial.use_transparent_shadow = True
    simplecolormaterial.blend_method = "HASHED"
    simplecolormaterial.displacement_method = "BUMP"
    simplecolormaterial.preview_render_type = "SPHERE"
    simplecolormaterial.surface_render_method = "DITHERED"
    simplecolormaterial.thickness_mode = "SPHERE"
    simplecolormaterial.volume_intersection_method = "FAST"
    simplecolormaterial.specular_color = (1.0, 1.0, 1.0)
    simplecolormaterial.diffuse_color = (0.8, 0.8, 0.8, 1.0)
    simplecolormaterial.line_color = (0.0, 0.0, 0.0, 0.0)

    # node: Principled BSDF
    principled_bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    principled_bsdf.name = "Principled BSDF"
    principled_bsdf.show_options = True
    principled_bsdf.distribution = "MULTI_GGX"
    principled_bsdf.subsurface_method = "RANDOM_WALK"
    principled_bsdf.panel_states[0].is_collapsed = True
    principled_bsdf.panel_states[1].is_collapsed = True
    principled_bsdf.panel_states[2].is_collapsed = True
    principled_bsdf.panel_states[3].is_collapsed = True
    principled_bsdf.panel_states[4].is_collapsed = True
    principled_bsdf.panel_states[5].is_collapsed = True
    principled_bsdf.panel_states[6].is_collapsed = True
    principled_bsdf.panel_states[7].is_collapsed = True
    principled_bsdf.inputs[0].default_value = base_color # base color
    principled_bsdf.inputs[1].default_value = 0.0 # metallic
    principled_bsdf.inputs[2].default_value = 0.5 # roughness
    principled_bsdf.inputs[3].default_value = 1.5 # IOR
    principled_bsdf.inputs[4].default_value = 1.0 # alpha
    principled_bsdf.inputs[5].default_value = False # thin wall
    principled_bsdf.inputs[6].default_value = (0.0, 0.0, 0.0) # normal
    principled_bsdf.inputs[8].default_value = 0.0 # diffuse roughness
    principled_bsdf.inputs[9].default_value = 0.0 # subsurface weight
    principled_bsdf.inputs[10].default_value = (1.0, 0.2, 0.1) # subsurface radius
    principled_bsdf.inputs[11].default_value = 0.005 # subsurface scale
    principled_bsdf.inputs[13].default_value = 0.0 # subsurface anisotropy
    principled_bsdf.inputs[14].default_value = 0.5 # specular IOR level
    principled_bsdf.inputs[15].default_value = (1.0, 1.0, 1.0, 1.0) # specular tint
    principled_bsdf.inputs[16].default_value = 0.0 # anisotropic
    principled_bsdf.inputs[17].default_value = 0.0 # anisotropic rotation
    principled_bsdf.inputs[18].default_value = (0.0, 0.0, 0.0) # tangent
    principled_bsdf.inputs[19].default_value = 0.0 # transmission weight
    principled_bsdf.inputs[20].default_value = 0.0 # coat weight
    principled_bsdf.inputs[21].default_value = 0.03 # coat roughness
    principled_bsdf.inputs[22].default_value = 1.5 # coat IOR
    principled_bsdf.inputs[23].default_value = (1.0, 1.0, 1.0, 1.0) # coat tint
    principled_bsdf.inputs[24].default_value = (0.0, 0.0, 0.0) # coat normal
    principled_bsdf.inputs[25].default_value = 0.0 # wheen weight
    principled_bsdf.inputs[26].default_value = 0.5 # sheen roughness
    principled_bsdf.inputs[27].default_value = (1.0, 1.0, 1.0, 1.0) # sheen tint
    principled_bsdf.inputs[28].default_value = (1.0, 1.0, 1.0, 1.0) # emission color
    principled_bsdf.inputs[29].default_value = 0.0 # emission strength
    principled_bsdf.inputs[30].default_value = 0.0 # thin film thickness
    principled_bsdf.inputs[31].default_value = 1.33 # thin film IOR

    # node: Material Output
    material_output = nodes.new("ShaderNodeOutputMaterial")
    material_output.name = "Material Output"
    material_output.show_options = True
    material_output.is_active_output = True
    material_output.target = "ALL"
    material_output.inputs[2].default_value = (0.0, 0.0, 0.0) # displacement
    material_output.inputs[3].default_value = 0.0 # thickness

    # locations
    nodes["Principled BSDF"].location = (-200.0, 100.0)
    nodes["Material Output"].location = (200.0, 100.0)

    # dimensions
    nodes["Principled BSDF"].width  = 240.0
    nodes["Principled BSDF"].height = 100.0

    nodes["Material Output"].width  = 140.0
    nodes["Material Output"].height = 100.0

    # links
    links.new(
        nodes["Principled BSDF"].outputs[0],
        nodes["Material Output"].inputs[0],
    )

    return simplecolormaterial




# assign material to first slot (create it if doesn't exist)
def assign_material (
    material: bpy.types.Material,
    geometry: bpy.types.Mesh | bpy.types.Curve,
) -> None:
    if len(geometry.materials) == 0:
        geometry.materials.append(material)
    else:
        geometry.materials[0] = material
