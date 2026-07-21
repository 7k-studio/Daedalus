I went through the viewport implementation. This is actually a pretty solid foundation. It already has:

* camera abstraction (`Camera2D`)
* world/screen conversion
* zoom/pan
* adaptive grid
* rulers
* FreeType text rendering
* airfoil rendering
* control net rendering

The biggest issue isn't functionality—it's architecture and rendering performance. Right now it's written like a 2008 OpenGL immediate-mode CAD viewer. DAEDALUS deserves something closer to Rhino, SolidWorks or Fusion 360.

I would not rewrite everything. I'd evolve it in stages.

---

# Stage 1 — Separate responsibilities (highest ROI)

At the moment `ViewportOpenGL` does everything:

* camera
* drawing
* input
* grid
* rulers
* airfoil
* construction
* text

This will become painful once selections, snapping, dimensions, annotations and multiple objects appear.

I'd split it into renderers.

```
viewport/

    viewport.py          <- QOpenGLWidget

    camera.py

    renderers/
        grid_renderer.py
        ruler_renderer.py
        airfoil_renderer.py
        construction_renderer.py
        controlnet_renderer.py
        overlay_renderer.py

    interaction/
        pan_tool.py
        selection_tool.py
        measure_tool.py
        edit_tool.py
```

Then

```python
class ViewportOpenGL(QOpenGLWidget):

    def paintGL(self):

        self.grid_renderer.draw()

        self.airfoil_renderer.draw()

        self.control_renderer.draw()

        self.overlay_renderer.draw()
```

Now every renderer is under 300 lines.

---

# Stage 2 — Introduce RenderContext

Instead of passing

```
width
height
camera
colors
preferences
```

everywhere...

Create

```python
@dataclass
class RenderContext:

    camera: Camera2D

    width: int

    height: int

    preferences: dict

    colors: dict
```

Then

```python
renderer.draw(context)
```

instead of

```
renderer.draw(
    width,
    height,
    camera,
    preferences,
    ...
)
```

---

# Stage 3 — Remove Immediate Mode

Currently almost everything is

```python
glBegin(GL_LINES)

...

glVertex()

...

glEnd()
```

This is deprecated since OpenGL 3.

Instead

```
NumPy array

↓

Vertex Buffer

↓

glDrawArrays()
```

Example

```python
vertices = np.array([
    [-1,0],
    [ 1,0],

    [0,-1],
    [0, 1]
],dtype=np.float32)
```

Upload once

```python
vao = glGenVertexArrays(1)
vbo = glGenBuffers(1)

glBindVertexArray(vao)

glBindBuffer(GL_ARRAY_BUFFER,vbo)

glBufferData(
    GL_ARRAY_BUFFER,
    vertices.nbytes,
    vertices,
    GL_STATIC_DRAW
)

glVertexAttribPointer(
    0,
    2,
    GL_FLOAT,
    False,
    0,
    None
)

glEnableVertexAttribArray(0)
```

Draw

```python
glBindVertexArray(vao)

glDrawArrays(GL_LINES,0,len(vertices))
```

This alone gives **10x–100x** performance improvement.

---

# Stage 4 — Cache Static Geometry

Grid is regenerated every frame.

Rulers too.

Instead

```
Camera changed?

↓

Yes

↓

Regenerate grid VBO

↓

No

↓

Reuse
```

Pseudo

```python
class GridRenderer:

    def __init__(self):

        self.last_zoom = None

        self.last_center = None

        self.vbo = None
```

Then

```python
if camera.zoom != self.last_zoom:

    self.build_grid()
```

The grid shouldn't be rebuilt 60 times/sec.

---

# Stage 5 — GPU Text

Your FreeType renderer is already nice.

Go further.

Instead of

```
draw_text()

draw_text()

draw_text()

draw_text()

...
```

Create

```
TextBatch
```

```python
batch.add("0.1",x,y)

batch.add("0.2",...)

batch.add("0.3"...)
```

Then

```
batch.draw()
```

One texture bind.

One draw call.

---

# Stage 6 — Scene Graph

Instead of

```
if airfoil:

draw_airfoil()

draw_cp()

draw_construction()
```

Create objects.

```
Scene

    AirfoilNode

    GridNode

    RulerNode

    BackgroundNode

    DimensionNode

    AnnotationNode
```

Then

```python
for node in scene.nodes:

    node.draw(context)
```

Adding a new entity becomes trivial.

---

# Stage 7 — Picking System

Currently there is no proper selection.

I'd introduce

```python
class PickResult:

    object

    distance

    world_position

    screen_position
```

Every drawable implements

```python
pick(mouse_world)
```

Example

```python
def pick(self,pos):

    for cp in self.control_points:

        d=np.linalg.norm(cp-pos)

        if d<radius:

            return PickResult(...)
```

Later this becomes snapping too.

---

# Stage 8 — Camera Improvements

Current zoom

```python
camera.zoom *= factor
```

Zooms toward screen center.

CAD software zooms toward cursor.

Example

```python
before = camera.screen_to_world(
    mouse.x(),
    mouse.y(),
    w,
    h
)

camera.zoom *= factor

after = camera.screen_to_world(
    mouse.x(),
    mouse.y(),
    w,
    h
)

camera.center += before-after
```

Feels infinitely better.

---

# Stage 9 — Infinite Grid

Instead of drawing hundreds of lines

draw only visible ones.

Pseudo

```python
xmin = floor(left/spacing)

xmax = ceil(right/spacing)

for i in range(xmin,xmax):

    ...
```

You already do part of this.

I would also fade minor grids.

```
Zoom far away

↓

Minor grid disappears

↓

Zoom in

↓

Minor grid appears smoothly
```

Exactly like Fusion360.

---

# Stage 10 — Rendering Layers

```
Layer 0

Background

↓

Layer 1

Grid

↓

Layer 2

Construction

↓

Layer 3

Geometry

↓

Layer 4

Selection

↓

Layer 5

Dimensions

↓

Layer 6

Overlay
```

Each renderer owns one layer.

---

# Stage 11 — OpenGL State Manager

Currently

```
glEnable

glDisable

glEnable

glDisable

...
```

all over the code.

Instead

```python
class GLState:

    def lines(self):

        glDisable(GL_DEPTH_TEST)

        glPolygonMode(...)
```

Then

```python
state.begin_overlay()

...

state.begin_geometry()

...

state.begin_ui()
```

No accidental state leaks.

---

# Stage 12 — Geometry Utilities

There are repeated calculations.

For example

```python
left,right,bottom,top = camera.world_bounds(...)
```

appears everywhere.

Create

```python
class ViewTransform:

    left

    right

    top

    bottom

    aspect

    scale_x

    scale_y
```

Computed once per frame.

---

# Stage 13 — Drawable Objects

Instead of

```python
draw_airfoil()

draw_cp()

draw_dashed()
```

Create

```python
class Drawable:

    def draw(self):

        ...

    def bounds(self):

        ...

    def pick(self):

        ...
```

Then

```python
class AirfoilDrawable(Drawable):

...

class ConstructionDrawable(Drawable):

...

class GridDrawable(Drawable):
```

---

# Stage 14 — Dirty Flags

Instead of rebuilding everything

```python
camera_dirty

geometry_dirty

grid_dirty

text_dirty
```

Example

```python
if self.grid_dirty:

    self.grid.build()

    self.grid_dirty=False
```

Huge performance gain.

---

# Stage 15 — Snapping Engine

Eventually you'll want

* endpoint
* midpoint
* spline
* tangent
* perpendicular
* nearest
* intersection

Architecture

```
SnapEngine

↓

GridSnap

↓

ControlPointSnap

↓

SplineSnap

↓

ConstructionSnap
```

Each returns candidates.

---

# Stage 16 — Viewport Tools

Instead of

```python
mousePressEvent()

mouseMoveEvent()

mouseReleaseEvent()
```

containing lots of `if` statements,

introduce tools:

```python
class Tool:

    def mousePress(self,event):
        pass

    def mouseMove(self,event):
        pass

    def mouseRelease(self,event):
        pass
```

Then

```python
self.active_tool.mouseMove(event)
```

Tools become:

* PanTool
* ZoomTool
* EditControlPointTool
* MeasureTool
* SplitSplineTool
* AddPointTool
* MoveTool
* RotateTool

This is how professional CAD systems are structured.

---

## One immediate improvement you can implement

Your `paintGL()` can become much cleaner:

```python
def paintGL(self):
    self._prepare_world_projection()

    self.grid_renderer.draw(self.ctx)
    self.airfoil_renderer.draw(self.ctx)
    self.control_renderer.draw(self.ctx)
    self.construction_renderer.draw(self.ctx)

    self._prepare_overlay_projection()

    self.ruler_renderer.draw(self.ctx)
    self.overlay_renderer.draw(self.ctx)
```

with helper methods:

```python
def _prepare_world_projection(self):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    left, right, bottom, top = self.camera.world_bounds(
        self.width(),
        self.height()
    )

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(left, right, bottom, top)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def _prepare_overlay_projection(self):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()

    glOrtho(
        0,
        self.width(),
        self.height(),
        0,
        -1,
        1,
    )

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
```

---

## Overall roadmap

I would prioritize the work in this order:

1. **Split rendering into dedicated renderer classes** (highest maintainability gain).
2. **Introduce a shared `RenderContext` and `ViewTransform`** to remove duplicated calculations.
3. **Replace immediate-mode rendering with VAOs/VBOs** for all static and semi-static geometry.
4. **Add dirty flags and cache generated geometry** (grid, rulers, construction lines, control nets).
5. **Implement cursor-centered zoom and a proper picking/snap engine** to improve interaction quality.
6. **Refactor input handling into interchangeable tool classes** (pan, edit, measure, etc.).
7. **Move to a scene graph with drawable objects and render layers**, making it straightforward to add dimensions, annotations, reference airfoils, multiple models, and future CAD features.

Following that sequence will transform this viewport from a capable OpenGL widget into a scalable CAD-style rendering engine without requiring a disruptive rewrite.
