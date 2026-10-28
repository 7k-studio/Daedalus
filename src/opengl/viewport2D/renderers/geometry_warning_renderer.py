"""Screen-space indicators for invalid airfoil geometry."""

from OpenGL.GL import (
    GL_TRIANGLES,
    GL_TEXTURE_2D,
    glBegin,
    glColor3f,
    glDisable,
    glEnd,
    glVertex2f,
)


def draw(context, message="Self-crossing spline, check the geometry"):
    """Draw a fixed-size warning triangle and label in the viewport corner."""
    width = float(context.width)
    margin = 12.0
    center_x = width - margin - 10.0
    center_y = 20.0

    glDisable(GL_TEXTURE_2D)
    glColor3f(1.0, 0.55, 0.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(center_x, center_y - 10.0)
    glVertex2f(center_x - 9.0, center_y + 7.0)
    glVertex2f(center_x + 9.0, center_y + 7.0)
    glEnd()

    renderer = context.text_renderer
    if renderer is not None:
        renderer.render_text_screen_space(
            "!",
            center_x,
            center_y + 1.0,
            color=(70, 45, 0),
            centered=True,
            viewport_height=context.height,
        )
        renderer.render_text_screen_space(
            message,
            max(8.0, center_x - 24.0 - len(message) * 6.0),
            center_y - 5.0,
            color=(255, 165, 0),
            centered=False,
            viewport_height=context.height,
        )
