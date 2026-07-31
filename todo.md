# ToDo

for realease of ***v0.4.0-beta*** version

## Airfoil Designer
---

### File Save
To save LE/TE/PS/SS as instances in airfoil not subsections in params/attrs

### Reference
A reference can now be handled using both bar menu and specified widget. Both allow to add, delete, show and hide a reference airfoil
**ToDo:**
- [x] **Add** button works properly for selig format airfoils
- [x] **Delete** button works properly for selig format airfoils
- [x] **Show/Hide** button works properly for selig format airfoils
- [ ] To be able to load ddls files as reference
- [ ] Secondary: **postponed to version v4.1**
    - [ ] ~~To allow to modify the reference~~
    - [ ] ~~To allow to flip the reference~~

### Tool Bar
New element added to GUI to quickly navigate the functions of the program. For now the airfoil functions are displayed for quick access it also supports shortcuts:
> Shift+N - add new airfoil
> Shift+A - append selected airfoil
> Shift+X - delete selected airfoil
> Shift+F - flip selected airfoil
> Shift+S - save selected airfoil

**ToDo:**
- [x] To assign functions to each button
- [x] To enlarge the Toolbar with other Essentail Tools

### Menu Bar / Basic functions
Has a lot to investiagte
**Checked/Partially Checked:**
- File Menu:
    - [x] New ← works and refreshes the widgets of tree airfoil and reference
    - [ ] Open ← works as a button but **function should be checked after clarification of new airfoil definition**
    - [x] Save ← works and the export was adapted to the new hierarchy of airfoil object
    - [x] Save As ← works and the export was adapted to the new hierarchy of airfoil object
    - [x] Edit Project Description ← works as intended, updates between widgets and modules
    - [x] Exit ← works as intended

- Program Menu:
    - [x] User Manual ← works as intended, opens user manual in web browser
    - [x] About ← works as intended, opens about window as pop-up window
    - [x] Preferences ← works as intended, opens window as pop-up window, allows to save or abort, still requires reboot in some functions.

**ToDo:**
- Airfoil -- **Check if functions are working with new airfoil definition:**    
    - [x] Create ← works, added to toolbar
    - [ ] Append
    - [ ] Delete ← **doesn't work**
    - [x] Flip ← flips the airfoil but does not change the position of PS and SS. Should it?
    - [x] Save ← Saves an airfoil to .arf.ddls format based on json
    - [ ] Export
    - [x] Rename ← renames an airfoil and assures the unique name
    - [ ] ~~Edit description~~ *no longer applicable*
    - [ ] ~~Fit2Reference~~ **postponed to version v4.1**
- Reference
    - [ ] Add ← adds the reference to project
    - [ ] Delete ← deletes selected reference (maybe add warning)
    - [ ] Show ← changes the visibility state, resulting in object appearing ad dissappearing in the viewport
    - [ ] ~~Edit~~ **postponed to version v4.1**
    - [ ] ~~Flip~~ **postponed to version v4.1**
- View
    - [x] Fit view ← **works!**
    - [ ] ~~Show Curvature comb~~ **postponed to version v4.1**
    - [ ] ~~Show camberline~~ **postponed to version v4.1**
- Window -- **NO TICK UPDATE IN MENU BAR**
    - [x] Airfoil Tree
    - [x] Reference Tree
    - [x] Parameter Table
    - [x] Logger Console
    - [x] Description TextArea
    - [x] Statistics Table
- Module
    - [x] Wing Module ← **changes the module correctly**


## Wing Designer
---
### Object Tree
- [x] Adding components ← **works**
- [x] Adding wings ← **works**
- [x] Adding segments ← **works**
    - [x] Adding segments causes parent airfoil do be added to tree ← **works**
- [ ] Deleting components
- [ ] Deleting wings
- [ ] Deleting segments
    - [ ] Deleting segments causes parent airfoil do be added to tree

## Wing Creation
- [x] Segment Wireframe is created
- [x] Connection wireframe is created
- [ ] Surface is created:
    - [ ] Creating Skin instance
    - [ ] Creating Surface patches and assigning exisiting wireframe to it
    - [ ] All handled by OpenGL

### STEP export
- [ ] adapt STEP classes to new objects and methods in DAEDALUS 0.4
- [ ] modify export algorythm
---
 
### Airfoil tree --> Finished and tested for AD
An airfoil tree was adjusted to match new convention
**ToDo:**
- [x] Add 'type' column Airfoil tree
    - [ ] ~~control type of LE and TE: free (F), circle (C), elipse(E)~~ **postponed to version v4.1**
- [x] Fixed the bug on tree refresh when ***Type*** is missing
- [x] To make the widget store the selected object info data

### Parameter Table --> Finished and tested for AD / WD
A table was adjusted to new airfoil format. It now updates and populates the tabele properly with the selected airfoil data.
**ToDo:**
- [x] To clear out the rows after airfoil was deleted
- [x] To repair nominal to stay put untill project open or refresh

### Description Editing --> Finished and tested for AD / WD
Description Widget in Airfoil Designer shows the description of an airfoil in the widget or in the dialog. Clicking Edit button allows to edit the text. To edit an airfoil user must first select an airfoil in the airfoil tree. If an airfoil is deleted the default message is being displayed.
*ToDo:*
- [x] To populate the text area with description of selected airfoil
- [x] To save/reject the changes on user's request
- [x] Bullet proof the widget for possible unwanted events
- [x] To clear out after deleding an airfoil

### Statistics Table --> Finiseh and tested for AD
New widget added to display statistics of the selected airfoil.
**ToDo:**
- [x] To ensure the Table Widget Can work in AirfoilDesigner and in WingDesigner
- [x] Table widget reacts to chaing parameters in Parameters Table
- [ ] ~~To investigate the statistics of interest~~ -->  **postponed to version v4.1**
- [ ] ~~To enlarge the available statistics storage~~ -->  **postponed to version v4.1**

### Home Screen --> Finished
Correct buttons and styling
*ToDo:*
- [x] correct cards in home screen
- [x] ensure proper buttons functions

# Changelog notes

A new airfoil definition was introduced in the 0.4 version. LE, TE, PS and SS are now separated objects, creating whole airofil.
This led to new Tree Layout where Airfoil is created out of respective objects as parents and childrens.
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

#### 1. Logger Console
Console only outputs the data. Updates the log file once the file is updated. The color is adjusted to differenciate between DEBUG, INFO, WARNING, ERROR, CRITICAL.