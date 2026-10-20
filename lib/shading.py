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
        color_socket = emissionshadow.interface.new_socket(
            name="Color",
            in_out="INPUT",
            socket_type="NodeSocketColor",
        )
        color_socket.default_value = (0.8, 0.8, 0.8, 1.0)
        color_socket.attribute_domain = "POINT"
        color_socket.default_input = "VALUE"
        color_socket.structure_type = "AUTO"

        # output socket: Shader
        shader_socket = emissionshadow.interface.new_socket(
            name="Shader",
            in_out="OUTPUT",
            socket_type="NodeSocketShader",
        )
        shader_socket.attribute_domain = "POINT"
        shader_socket.default_input = "VALUE"
        shader_socket.structure_type = "AUTO"

    # shortcuts
    nodes = emissionshadow.nodes
    links = emissionshadow.links

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

    # node group input
    group_input = nodes.new("NodeGroupInput")
    group_input.name = "Group Input"
    group_input.show_options = True

    # node group output
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
