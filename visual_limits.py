bl_info = {
"name": "Visual limits",
"category": "3D View",
"version": (1, 0),
"blender": (2, 7, 9),
"location": "3D View",
"description": "Shows rigid body constraint limits in viewport",
"wiki_url": "https://github.com/xbodya13/visual_limits",
"tracker_url": "https://github.com/xbodya13/visual_limits/issues"
}



import bpy
import bgl
import mathutils
# import os



def paint_3d():
    if  not bpy.context.space_data.show_only_render:
        for selected_object in bpy.context.selected_objects:
            if selected_object.rigid_body_constraint!=None:


                rbc=selected_object.rigid_body_constraint
                rbc_object=selected_object

                center_world=rbc_object.matrix_world

                bgl.glEnable(bgl.GL_BLEND)
                bgl.glDisable(bgl.GL_DEPTH_TEST)
                bgl.glBegin(bgl.GL_POLYGON)
                segments=50
                radius=selected_object.empty_draw_size

                rotation_axes=(mathutils.Vector((1.,0.,0.)),mathutils.Vector((0.,1.,0.)),mathutils.Vector((0.,0.,1.)))
                axes_to_rotate=(rotation_axes[1],rotation_axes[0],rotation_axes[1])
                colors=((1.0, 0.0, 0.0, 0.3),(0.0, 1.0, 0.0, 0.3),(0.0, 0.0, 1.0, 0.3))
                solid_colors = ((0.7, 0.0, 0.0), (0.0, 0.7, 0.0), (0.0, 0.0, 0.7))


                ang_limits=(
                    (('GENERIC','GENERIC_SPRING','PISTON'),rbc.use_limit_ang_x, rbc.limit_ang_x_lower, rbc.limit_ang_x_upper),
                    (('GENERIC','GENERIC_SPRING'),rbc.use_limit_ang_y, rbc.limit_ang_y_lower, rbc.limit_ang_y_upper),
                    (('GENERIC','GENERIC_SPRING','HINGE'),rbc.use_limit_ang_z, rbc.limit_ang_z_lower, rbc.limit_ang_z_upper),
                )

                ang_matrix=center_world

                for (allowed,use_angle,low_angle,up_angle),color,rotation_axis,axis_to_rotate in zip(ang_limits,colors,rotation_axes,axes_to_rotate):

                    if use_angle:
                        if rbc.type in allowed:
                            bgl.glColor4f(0.,0.,0.,0.)
                            bgl.glVertex3f(*ang_matrix*mathutils.Vector([0, 0, 0]))
                            last_matrix = ang_matrix * mathutils.Matrix.Rotation(-low_angle, 4, rotation_axis)

                            for x in range(segments+1):
                                bgl.glColor4f(*color)
                                bgl.glVertex3f(*last_matrix*(radius*axis_to_rotate))
                                last_matrix *= mathutils.Matrix.Rotation(-(up_angle - low_angle) / segments, 4, rotation_axis)

                bgl.glEnd()


                linear_matrix=mathutils.Matrix.Translation(center_world.to_translation())*center_world.to_quaternion().to_matrix().to_4x4()


                linear_limits=(
                    (('GENERIC','GENERIC_SPRING','PISTON','SLIDER'),rbc.use_limit_lin_x,linear_matrix*mathutils.Vector((rbc.limit_lin_x_lower,0,0)),linear_matrix*mathutils.Vector((rbc.limit_lin_x_upper,0,0))),
                    (('GENERIC','GENERIC_SPRING'),rbc.use_limit_lin_y,linear_matrix*mathutils.Vector((0,rbc.limit_lin_y_lower,0)),linear_matrix*mathutils.Vector((0,rbc.limit_lin_y_upper,0))),
                    (('GENERIC','GENERIC_SPRING'),rbc.use_limit_lin_z,linear_matrix*mathutils.Vector((0,0,rbc.limit_lin_z_lower)),linear_matrix*mathutils.Vector((0,0,rbc.limit_lin_z_upper)))
                )


                bgl.glDisable(bgl.GL_BLEND)

                bgl.glLineWidth(2)
                bgl.glBegin(bgl.GL_LINES)
                for (allowed,use_linear,low,up),color in zip(linear_limits,solid_colors):
                    if use_linear:
                        if rbc.type in allowed:
                            bgl.glColor3f(*color)
                            bgl.glVertex3f(*low)
                            bgl.glVertex3f(*up)
                bgl.glEnd()


                bgl.glPointSize(8)
                bgl.glBegin(bgl.GL_POINTS)
                for (allowed,use_linear,low,up),color in zip(linear_limits,solid_colors):
                    if use_linear:
                        if rbc.type in allowed:
                            bgl.glColor3f(*color)
                            bgl.glVertex3f(*low)
                            bgl.glVertex3f(*up)
                bgl.glEnd()


paint_holder=set()


def register():
    # os.system('cls')
    paint_holder.add(bpy.types.SpaceView3D.draw_handler_add(paint_3d, (), 'WINDOW', 'POST_VIEW'))


def unregister():
    for item in paint_holder:
        bpy.types.SpaceView3D.draw_handler_remove(item, 'WINDOW')




