# Change Log

## v0.4.0-beta status - 2026-09-01

This release migrates the Daedalus to v0.4 object definition model, in which:
- An airfoil is composed of separate Leading Edge (LE), Trailing Edge (TE), Pressure Side (PS), and Suction Side (SS) spline objects
- The Wing surface is crated using Surface Patch creating a loft between the Segments

### Completed

- Airfoil files can be saved using the new LE/TE/PS/SS object hierarchy.
- File **New**, **Open**, **Save**, and **Save As** operations were adapted to
    the new airfoil structure. **Edit Project Description** and **Exit** are
    also working, including widget updates and exit confirmation.
- Airfoil actions now work with the new definition: create, append, delete,
    flip, save, export, and rename. Rename preserves unique airfoil names.
- The airfoil tree now displays spline type information, stores selected
    object data, and handles refreshes when type information is missing.
- The parameter table updates from selected airfoils, clears after deletion,
    and preserves nominal values until project opening or refresh.
- Description editing supports viewing, editing, accepting or rejecting
    changes, and clearing the widget after an airfoil is deleted.
- The statistics table works in both Airfoil Designer and Wing Designer and
    reacts to parameter-table changes.
- Reference airfoils can be added, deleted, shown, and hidden through the
    reference widget and menu. The menu also provides a management pop-up.
- The toolbar provides airfoil actions and keyboard shortcuts:
    `Shift+N` (new), `Shift+A` (append), `Shift+X` (delete), `Shift+F` (flip),
    and `Shift+S` (save).
- View fitting, synchronized window actions, the Wing module switch, and the
    User Manual, About, and Preferences dialogs are available.
- Wing Designer supports adding and deleting components, wings, and segments.
    Segment creation also updates the parent airfoil in the object tree.
- Wing wireframes, connection wireframes, surfaces, skin instances, and
    surface patches are handled by OpenGL. STEP export was adapted to the v0.4
    object model.
- The application was migrated to PyQt6. Window color schemes and the 2D
    viewport modes Bright, Dark, Blueprint, and Greenprint are available.

### Known limitations and postponed work

- Current `.ddls` airfoils and archived `.ddls` files cannot yet be loaded as
    reference airfoils. Selig `.txt` and `.dat` references are supported.
- Reference editing and flipping are postponed to v4.1.
- Fit2Reference, curvature comb, camberline, and spline control-type editing
    are postponed to v4.1.
- Some preference changes still require an application restart.
- Further investigation of the statistics provided by the application is
    postponed to v4.1.

### Compatibility note

Projects and exporters must account for the v0.4 hierarchy: LE, TE, PS, and
SS are independent objects rather than subsections stored only in the
airfoil parameter or attribute dictionaries.

# Previous ToDo

### Airfoil Tree
An airfoil tree was adjusted to match new convention
**ToDo:**
- [x] Add 'type' column Airfoil tree
    - [ ] control type of LE and TE: free (F), circle (C), elipse(E)
- [x] There is a bug on tree refreshe when ***Type*** is missing

### Reference Tree
A reference widget with buttons was created.
- [x] **Add** button works properly for selig format airfoils
- [x] **Show/Hide** button works properly for selig format airfoils
**ToDo:**
- [ ] To be able to load ddls files as reference
- [ ] To allow to delete reference
- [ ] Secondary:
    - [ ] To allow to modify the reference

### Parameter Table
Updates and populates the tabel properly with the selected airfoil data
**ToDo:**
- [ ] To repair nominal to stay put untill project open or refresh

### Description TextArea
Exists but does not work as intendet
**ToDo:**
- [ ] To populate the text area with description of selected airfoil

### Statistics Table
Populates the table with selected airfoil's statistics
**ToDo:**
- [ ] To investigate the statistics of interest
- [ ] To enlarge the available statistics storage

### Tool Bar
Exists but does not work as intendet
**ToDo:**
- [ ] To assign functions to each button
- [ ] To enlarge the Toolbar with other Essentail Tools

### Menu Bar
Has a lot to investiagte
**Checked/Partially Checked:**
- File Menu:
    - [ ] New ← works and refreshes the widgets of tree airfoil and reference
    - [ ] Open ← works as a button but **function should be checked after clarification of new airfoil definition**
    - [ ] Save ← works as a button but **function should be checked after clarification of new airfoil definition**
    - [ ] Save As ← works as a button but **function should be checked after clarification of new airfoil definition**
    - [x] Edit Project Description ← **works as intended**
    - [x] Exit ← **works as intended**

- Program Menu:
    - [x] User Manual ← **works as intended**
    - [x] About ← **works as intended**
    - [x] Preferences ← **works as intended**

**ToDo:**
- Airfoil -- *Check if functions are working with new airfoil definition:*
    - [ ] Create ← works! + to add to tool bar
    - [ ] Append
    - [ ] Delete ← works! + to add to tool bar
    - [ ] Flip
    - [ ] Save
    - [ ] Export
    - [ ] Rename
    - [ ] Edit description ← requires rework
    - [ ] Fit2Reference
- Reference
    - [ ] Add
    - [ ] Delete
    - [ ] Show
    - [ ] Edit
    - [ ] Flip
- View
    - [ ] Fit view
    - [ ] Show Curvature comb
    - [ ] Show camberline
- Window
    - [ ] Airfoil Tree
    - [ ] Reference Tree
    - [ ] Parameter Table
    - [ ] Logger Console
    - [ ] Description TextArea
    - [ ] Statistics Table
- Module
    - [ ] Wing Module

## Rework:
**View menu**
- [ ] set view back to airfoil
- [ ] curvature comb?
- [ ] strzalka ugięcia

**Description Widget**
**Reference Widget**
**Statistics Table**
Looks like it refreshes only after click on airfoil tree

Chords statistic: calc from Pitagoras

---

# Changelog notes

A new airfoil definition was introduced in the 0.4 version. LE, TE, PS and SS are now separated objects, creating whole airofil.
This led to new Tree Layout where Airfoil is created out of respective objects as parents and childrens.

Migration to PyQt6

## Program class

## Project
The structure of Project has been reworked with more conviniently alocated functions such as **New**, **Open**, **Save**, **Save As**, **Edit project description**, **Exit**
Project collects data of:
 - Project Name
 - Project Path
 - Creation Date
 - Modification Date
 - Project Description
 - Created Airfoils
 - Nominal versions of created airfoils - **TO DO: which should refresh on each project launch**
 - Reference Airfoils stored as Selig format .txt or .dat file or **TO DO: handle ddls airfoils**
 - ***Project Components***
 - ***Nominal Components***

## Color schemes
With version 0.4.X color schemes are to be choosen from preferences for viewports and for windows and widgets.
New window modes added:
 - Light - bright mode including white and grey
 - Dark - dark mode including black and dark grey
 - Deadalus Light - bright mode with deadalus characteristic colors light blue and light orange
 - Deadalus Dark - dark mode including reversed Deadalus characterisict colors mostly dark blue  

Additionaly 2D viewport in Airfoil Designer has 4 modes:
 - Bright: white color with dark construction elements 
 - Dark: dark color with bright construction elements
 - Blueprint: dark blue background
 - Greenprint: green background 

---

## Airfoil Designer

### New Airfoil definition
A new airfoil definition was established.

### Airfoil Designer - New widgets
Airfoil Designer was extended to new widgets and old ones got refined. From version v0.4 following widgets are available:

#### 1. Airfoil Tree
An airfoil tree was adjusted to match new convention. The column ***type*** was also added to the widget. It displays the type of the spline: 

The control type of Leading Edge *LE* and Trailing Edge *TE*: free (**F**) <br> for Pressure Side *PS* and Suction Side *SS*: curvature (**C**)

#### 2. Logger Console
Console only outputs the data. Updates the log file once the file is updated. The color is adjusted to differenciate between DEBUG, INFO, WARNING, ERROR, CRITICAL.