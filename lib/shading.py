#!/usr/bin/env python
# -*- coding: utf-8 -*-
# type: ignore

"""
https://github.com/drmats
"""

import bpy




# Node Group: Emission mixed with Diffuse BDSF for shadows
# input: color
# output: shader
def emissionshadow_node_group(
    name = "EmissionShadow",
    mix: float = 0.75,
):
    # node group
    emissionshadow = bpy.data.node_groups.get(name)

    # in-place update for existing node group (don't touch interface)
    if emissionshadow is not None:
        emissionshadow.nodes.clear()
        emissionshadow.links.clear()

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
            name="Color",
            in_out="INPUT",
            socket_type="NodeSocketColor",
        )
        in_color_socket.default_value = (0.8, 0.8, 0.8, 1.0)
        in_color_socket.attribute_domain = "POINT"
        in_color_socket.default_input = "VALUE"
        in_color_socket.structure_type = "AUTO"

        # output socket: Shader
        out_shader_socket = emissionshadow.interface.new_socket(
            name="Shader",
            in_out="OUTPUT",
            socket_type="NodeSocketShader",
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

    # link: group_input.Color -> emission.Color
    links.new(
        nodes["Group Input"].outputs[0],
        nodes["Emission"].inputs[0],
    )

    # link: group_input.Color -> diffuse_bsdf.Color
    links.new(
        nodes["Group Input"].outputs[0],
        nodes["Diffuse BSDF"].inputs[0],
    )

    # link: emission.Emission -> mix_shader.Shader
    links.new(
        nodes["Emission"].outputs[0],
        nodes["Mix Shader"].inputs[1],
    )

    # link: diffuse_bsdf.BSDF -> mix_shader.Shader
    links.new(
        nodes["Diffuse BSDF"].outputs[0],
        nodes["Mix Shader"].inputs[2],
    )

    # link: mix_shader.Shader -> group_output.Shader
    links.new(
        nodes["Mix Shader"].outputs[0],
        nodes["Group Output"].inputs[0],
    )

    return emissionshadow




# Node Group: Height-dependent (Z-axis) texturing.
# input 1: color
# input 2: color
# input 3: min float
# input 4: max float
# output: color
def dualheighttexture_node_group(
    name = "DualHeightTexture",
    transition = 0.2,
):
    # node group
    dualheighttexture = bpy.data.node_groups.get(name)

    # in-place update for existing node group (don't touch interface)
    if dualheighttexture is not None:
        dualheighttexture.nodes.clear()
        dualheighttexture.links.clear()

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
            name="Color",
            in_out="INPUT",
            socket_type="NodeSocketColor",
        )
        in_color_socket_1.default_value = (0.8, 0.8, 0.8, 1.0)
        in_color_socket_1.attribute_domain = "POINT"
        in_color_socket_1.default_input = "VALUE"
        in_color_socket_1.structure_type = "AUTO"

        # input socket: Color
        in_color_socket_2 = dualheighttexture.interface.new_socket(
            name="Color",
            in_out="INPUT",
            socket_type="NodeSocketColor",
        )
        in_color_socket_2.default_value = (0.8, 0.8, 0.8, 1.0)
        in_color_socket_2.attribute_domain = "POINT"
        in_color_socket_2.default_input = "VALUE"
        in_color_socket_2.structure_type = "AUTO"

        # input socket: Min
        in_min_socket = dualheighttexture.interface.new_socket(
            name="Min",
            in_out="INPUT",
            socket_type="NodeSocketFloat",
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
            name="Max",
            in_out="INPUT",
            socket_type="NodeSocketFloat",
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
            name="Color",
            in_out="OUTPUT",
        socket_type="NodeSocketColor",
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

    # link: group_input.Color -> mix.A
    links.new(
        nodes["Group Input"].outputs[0],
        nodes["Mix"].inputs[6],
    )

    # link: group_input.Color -> mix.B
    links.new(
        nodes["Group Input"].outputs[1],
        nodes["Mix"].inputs[7],
    )

    # link: group_input.Min -> map_range.From Min
    links.new(
        nodes["Group Input"].outputs[2],
        nodes["Map Range"].inputs[1],
    )

    # link: group_input.Max -> map_range.From Max
    links.new(
        nodes["Group Input"].outputs[3],
        nodes["Map Range"].inputs[2],
    )

    # link: texture_coordinate.Object -> separate_xyz.Vector
    links.new(
        nodes["Texture Coordinate"].outputs[3],
        nodes["Separate XYZ"].inputs[0],
    )

    # link: separate_xyz.Z -> map_range.Value
    links.new(
        nodes["Separate XYZ"].outputs[2],
        nodes["Map Range"].inputs[0],
    )

    # link: map_range.Result -> color_ramp.Factor
    links.new(
        nodes["Map Range"].outputs[0],
        nodes["Color Ramp"].inputs[0],
    )

    # link: color_ramp.Color -> mix.Factor
    links.new(
        nodes["Color Ramp"].outputs[0],
        nodes["Mix"].inputs[0],
    )

    # link: mix.Result -> group_output.Color
    links.new(
        nodes["Mix"].outputs[2],
        nodes["Group Output"].inputs[0],
    )

    return dualheighttexture
