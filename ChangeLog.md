# Change Log v0.4.0-beta

This release **migrates the Daedalus to reworked and unified object definition model**, in which:
- An airfoil is composed of separate Leading Edge (LE), Trailing Edge (TE), Pressure Side (PS), and Suction Side (SS) which use common **spline geometrical object**.
- The Wing surface is crated using **Surface Patch object** creating an interpolated or approximated loft between the Segments.

Additionally, the changes to the program code/structure were introduced separating ***Project***, form ***Program***.

### Program
 - Program now stores the user preferences and **appearance**.
    - four color schemes are available for Daedalus GUI: *Light*, *Dark*, *Daeadalus-Light*, *Daedalus-Dark*
    - four color schemes are available for Airfoil Designer: *Light*, *Dark*, *Greenprint*, *Blueprint*
 - The GUI environment migrated from PyQt5 to latest standard **PyQt6**
 - Splash Screen menu replaced with **Home Screen**

### Project
Saving adapted to new airfoil and component standards.
Each object (Component, Wing, Segment, Airfoil) now has to have unique name. When creating or renaming the program takes care of it.

### Widget
Widgets are now devided between *commmon* and *module specific*.
*Common*:
1. **Project description** - Edits the **Project** description
2. **Logger Console** - outputs the data. Updates the log file once the file is updated. The color is adjusted to differenciate between DEBUG, INFO, WARNING, ERROR, CRITICAL.
3. **Tool Bar** - quick access to the functions of the program. It is possible to use shortcuts: `Ctrl+N` for New Project, `Ctrl+O` for Open Project, `Ctrl+S` for Save Project, `Ctrl+E` for Edit description.
    > Common between modules are file menu functions
4. **Parameters Table** - displays and modifies the parameters (Each module has its own instance but build is common)
5. **Statistics Table** - displays selected airfoil statistics (Each module has its own instance but build is common)

For now the airfoil functions are displayed for quick access it also supports shortcuts:


## Compatibility note

> Projects and exporters must account for the v0.4 hierarchy: LE, TE, PS, and SS are independent objects rather than subsections stored only in the airfoil parameter or attribute dictionaries.

### Known limitations

- Some archived DDLS versions may require recreation during reference import;
    inspect the loaded geometry before fitting.
- Some preference changes still require an application restart.

---
## Airfoil Designer

### New Airfoil definition
Several changes were made in the Airfoil Designer including a new airfoil definition. New airfoil definition divides the airfoil's parameters into:
- **main paramters** - which allow to specify thickness, legnth and angles
- **curvature parameters** - which refine the airfoil and control the shape of the curves

Module was extended to new widgets and old ones got refined. 

### Airfoils
There are several operations to be performed on airfoil in v0.4 which can be:
- Select via: **Airfoil Tree Widget**
- Modified via: **Edit menu**, **Parameter Table Widget**, **Tool Bar Widget**
- Analyzed via: **Statistics Table**


New functions:
- **Duplicate** selected airfoil
- **Fit to Reference** shows a widgets where interatively an airfoil can be matched with a reference

Removed functions:
- **Airfoil description** option was removed and replaced with **Project description**

### References
The references in the v0.4 can be handled independently of selected airfoil. The references can be accessed:
- via dockable widget
- via Reference menu and Reference Manager Window

In both cases it is possible to:
-  **Add** which allows to load:
    - current format airfoil,
    - ddls v0.3 format airfoil,
    - XY-point reference airfoil, 
- **Delete** selected unused reference
- **Show/Hide** an airfoil in the viewport
- **Edit** to scale the XY-point reference to the size of interest

### Widgets
1. **Airfoil Tree** was adjusted to match new convention. The column ***type*** was also added to the widget. It displays the type of the spline. The type of Leading Edge *LE*, Trailing Edge *TE*, Pressure Side *PS* and Suction Side *SS*: can be set to **G1** or **G2**
2. **Tool Bar** New element added to GUI to quickly navigate the functions of the program. The toolbar provides airfoil actions and keyboard shortcuts: `Shift+N` (new), `Shift+A` (append), `Shift+X` (delete), `Shift+F` (flip), and `Shift+S` (save).

---
## Wing Designer

Wing Designer changes were triggered by the refined Airfoil definition. Similarly the Wing object was changed from several segments to 4 normalzied surfaces defined by spline geometrical objects.

**New:**
- **Rename Object** - it is possible to rename the objects in the Wing Designer. The objects must have the unique name which is ensured on each name change. If name is taken an intiger will be assigned in the end of the name.
- 

### Component object

**New:**
- **Duplicate** - it is possible to duplicate the component

### Wing object
Wing object now stores the surfaces defined by it's segments and the connecting spline. 

**Removed:**
- Wings no longer have their own coordinate system

**New:**
- Wings now have 2 attributes: 
    - ***direction*** - will allow to change the growth direction
    - ***connection*** - does allow to change the connecting splines definition (*Approximated* or *Interpolated*)
- **Duplicate** - it is possible to duplicate the wing

### Segment object
Segments continue to store parameters such as *position X, Y*, but the Z coordinate was changed to ***span***. In v0.4 in **Object Tree** below the *Segment* instance the parent Airfoil appears allowing to modify the main airfoil parameters on the spot in Wing Designer. For detailed airfoil modification movig to Airfoil Designer is needed.

**New:**
- **Duplicate** - it is possible to duplicate the segment


### Widgets
1. **Tool Bar** New element added to GUI to quickly navigate the functions of the program. The toolbar provides Component/Wing/Segment actions and keyboard shortcuts: `Shift+C` (new component), `Shift+W` (new wing), `Shift+S` (new segment)

### STEP export
STEP export now modified to proveide more robust model from standardized geometries definition. The export uses the same spline for surface definition in STEP ensuring connectivity and continuity of the surface.