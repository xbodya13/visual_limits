bl_info = {
"name": "Visual limits",
"category": "3D View",
"version": (1, 3,0),
"blender": (4, 3,0),
"location": "3D View",
"description": "Shows rigid body constraint limits in viewport",
"wiki_url": "https://github.com/xbodya13/visual_limits",
"tracker_url": "https://github.com/xbodya13/visual_limits/issues"
}



import bpy
import gpu
import mathutils
import itertools
from gpu_extras.batch import batch_for_shader
# import os

class gv:
    shader=gpu.shader.from_builtin('SMOOTH_COLOR')
    shader.bind()







def paint_3d():
    if  bpy.context.space_data.overlay.show_overlays:

        # for selected_object in bpy.data.objects:
        for selected_object in itertools.chain(bpy.context.selected_objects):
            if selected_object.rigid_body_constraint!=None:

                rbc=selected_object.rigid_body_constraint
                rbc_object=selected_object

                center_world=rbc_object.matrix_world

                segments=50
                radius=selected_object.empty_display_size

                rotation_axes=(mathutils.Vector((1.,0.,0.)),mathutils.Vector((0.,1.,0.)),mathutils.Vector((0.,0.,1.)))
                axes_to_rotate=(rotation_axes[1],rotation_axes[0],rotation_axes[1])
                colors=((1.0, 0.0, 0.0, 0.3),(0.0, 1.0, 0.0, 0.3),(0.0, 0.0, 1.0, 0.3))
                solid_colors = ((0.7, 0.0, 0.0,1.0), (0.0, 0.7, 0.0,1.0), (0.0, 0.0, 0.7,1.0))


                ang_limits=(
                    (('GENERIC','GENERIC_SPRING','PISTON'),rbc.use_limit_ang_x, rbc.limit_ang_x_lower, rbc.limit_ang_x_upper),
                    (('GENERIC','GENERIC_SPRING'),rbc.use_limit_ang_y, rbc.limit_ang_y_lower, rbc.limit_ang_y_upper),
                    (('GENERIC','GENERIC_SPRING','HINGE'),rbc.use_limit_ang_z, rbc.limit_ang_z_lower, rbc.limit_ang_z_upper),
                )



                linear_matrix=mathutils.Matrix.Translation(center_world.to_translation())@center_world.to_quaternion().to_matrix().to_4x4()


                linear_limits=(
                    (('GENERIC','GENERIC_SPRING','PISTON','SLIDER'),rbc.use_limit_lin_x,linear_matrix@mathutils.Vector((rbc.limit_lin_x_lower,0,0)),linear_matrix@mathutils.Vector((rbc.limit_lin_x_upper,0,0))),
                    (('GENERIC','GENERIC_SPRING'),rbc.use_limit_lin_y,linear_matrix@mathutils.Vector((0,rbc.limit_lin_y_lower,0)),linear_matrix@mathutils.Vector((0,rbc.limit_lin_y_upper,0))),
                    (('GENERIC','GENERIC_SPRING'),rbc.use_limit_lin_z,linear_matrix@mathutils.Vector((0,0,rbc.limit_lin_z_lower)),linear_matrix@mathutils.Vector((0,0,rbc.limit_lin_z_upper)))
                )



                points=[]
                point_colors=[]


                for (allowed,use_angle,low_angle,up_angle),color,rotation_axis,axis_to_rotate in zip(ang_limits,colors,rotation_axes,axes_to_rotate):
                    if use_angle:

                        if rbc.type in allowed:

                            origin_point=tuple(center_world@mathutils.Vector([0, 0, 0]))
                            origin_color=0.,0.,0.,0.


                            last_matrix = center_world @ mathutils.Matrix.Rotation(-low_angle, 4, rotation_axis)
                            last_point=None

                            for x in range(segments+1):

                                point=tuple(last_matrix@(radius*axis_to_rotate))



                                if last_point is not None:
                                    point_colors.append(origin_color)
                                    points.append(origin_point)

                                    point_colors.append(color)
                                    points.append(point)

                                    point_colors.append(color)
                                    points.append(last_point)


                                last_matrix @= mathutils.Matrix.Rotation(-(up_angle - low_angle) / segments, 4, rotation_axis)
                                last_point=point


                # bgl.glEnable(bgl.GL_BLEND)
                gpu.state.blend_set('ALPHA')
                # bgl.glDisable(bgl.GL_DEPTH_TEST)
                gpu.state.depth_mask_set(False)


                render_batch=batch_for_shader(gv.shader,'TRIS',{"pos":points,"color":point_colors})
                render_batch.draw(gv.shader)



                points=[]
                point_colors=[]
                # bgl.glDisable(bgl.GL_BLEND)
                gpu.state.blend_set('NONE')
                # bgl.glLineWidth(2)
                gpu.state.line_width_set(2)

                for (allowed,use_linear,low,up),color in zip(linear_limits,solid_colors):
                    if use_linear:
                        if rbc.type in allowed:

                            points.append(tuple(low))
                            point_colors.append(color)
                            points.append(tuple(up))
                            point_colors.append(color)


                render_batch=batch_for_shader(gv.shader,'LINES',{"pos":points,"color":point_colors})
                render_batch.draw(gv.shader)

                # bgl.glPointSize(8)
                gpu.state.point_size_set(8)
                render_batch=batch_for_shader(gv.shader,'POINTS',{"pos":points,"color":point_colors})
                render_batch.draw(gv.shader)




paint_holder=set()


def register():
    # os.system('cls')

    paint_holder.add(bpy.types.SpaceView3D.draw_handler_add(paint_3d, (), 'WINDOW', 'POST_VIEW'))


def unregister():
    for item in paint_holder:
        bpy.types.SpaceView3D.draw_handler_remove(item, 'WINDOW')




