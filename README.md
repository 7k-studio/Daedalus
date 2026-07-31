# Daedalus

This project is a free CAD software whitch allows user to create an airfoil from scratch, or match it with reference, and to create wing out of created airfoils.
Program consists of two modules:
1. Airfoil designer - for airfoil operations
2. Wing Workbench - for wing creation and modification
   
Daedalus implements a 3D OpenGL viewport embedded in a PyQt6 GUI. The application allows for mouse interaction to translate, rotate, and zoom within the 3D space. It features a structured layout with a tree menu for navigation, a dropdown menu for basic functions, and a table widgets for user interaction.

## Project Structure

```
Daedalus
├── main.py                                   # Entry point of the application
├── src
│   ├── settings                              # Store for user settings in JSON based file
│   |                                         
|   ├── assets                                # Storage
|   |   ├── IconPack                      
|   |   |   └── Classic                       # Default set of icons
|   |   └── styles                        
|   |       ├── Daedalus-Dark.css         
|   |       ├── Daedalus-Light.css       
|   |       ├── Dark.css                  
|   |       └── Light.css                     # Default
|   ├── obj
|   |   ├── class_airfoil.py                  # Classes for DDLS Airfoils, v0.3.0 DDLS Airfoils, and cloud-point Airfoils
|   |   ├── class_component.py                # Class for Component
|   |   ├── class_segment.py                  # Class for Segment
|   |   ├── class_skin.py                     # Class for Skin
|   |   ├── curves.py                         # Collection of 2D objects - Curves
|   |   ├── param.py                          # Collection of Parameter, Attribute and Unit
|   |   └── surfaces.py                       # Collection of 3D objects - Surfaces
|   ├── opengl
│   │   ├── tools_lines.py                    # Utils for OpenGL specificaly: line drawing
│   │   ├── tools_opengl.py                   # Utils for OpenGL
|   |   |
│   │   ├── shaders
│   │   |   ├── vertex_shader.glsl            # Vertex shader code
│   │   |   └── fragment_shader.glsl          # Fragment shader code
|   |   ├── viewport2D
│   │   |   ├── camera.py                     # OpenGL viewport for Airfoil Designer
│   │   |   ├── viewport2D.py                 # OpenGL viewport for Airfoil Designer
|   |   |   |
|   |   |   ├── interaction                   # OpenGL 2D viewport interactions
|   |   |   |   ├── pan_tool.py 
|   |   |   |   └── zoom_tool.py
|   |   |   └── renderers                     # OpenGL 2D viewport renderers
|   |   |       ├── airfoil_renderer.py
|   |   |       ├── grid_renderer.py
|   |   |       ├── render_context.py
|   |   |       ├── ruler_renderer.py
│   │   |       └── text_renderer.py
|   |   └── viewport3D
│   │       ├── camera.py                     # OpenGL viewport for Wing Designer
│   │       ├── viewport3D.py                 # OpenGL viewport for Wing Designer
|   |       |
|   |       ├── interaction                   # OpenGL 3D viewport interactions
|   |       |   ├── pan_tool.py 
|   |       |   └── zoom_tool.py
|   |       └── renderers                     # OpenGL 3D viewport renderers
|   |           ├── bckgrd.py
|   |           ├── controlpoints_renderer.py
|   |           ├── coordinate_renderers.py
|   |           ├── grid_renderer.py
|   |           ├── surface_renderer.py
|   |           ├── test_cube.py
│   │           └── wireframe_renderer.py
|   ├── program
|   |   ├── home_screen.py                    # Splash screen on file load-up
|   |   ├── main_window.py                    # Splash screen on file load-up
|   |   ├── preferences.py                    # Loads / Saves / Changes settngs
|   |   ├── program.py                        # Main class for Daedalus program
|   |   ├── project.py                        # Project class to store the data
|   |   |
|   |   └── modules  
|   |       ├── arfdes
|   |       |   ├── airfoil_designer.py       # Main window layout and setup
|   |       |   ├── fit_2_reference.py        # Experimental function for reference matching
|   |       |   ├── menu_bar.py               
|   |       |   ├── tool_bar.py               
|   |       |   ├── tools_airfoil.py          # Utility functions and helpers for airfoils
|   |       |   ├── tools_refeerence.py       
|   |       |   ├── widget_tabele.py          # Tabele for object properties
|   |       |   └── widget_tree.py            # Tree menu for objects store
|   |       └── wngwb
|   |           ├── console_widget.py         # Command-line-like interface for user input
|   |           ├── main_window.py            # Main window layout and setup
|   |           ├── menu_bar.py                
|   |           ├── menu_context.py           # Future pleaceholder for context menu
|   |           ├── tools_wing.py             # Utility functions and helpers
|   |           ├── widget_tabele.py          # Tabele for object properties
|   |           └── widget_tree.py            # Tree menu for objects store    
|   ├── utils                                 # Utility functions and helpers
|   |   ├── dxf.py                            # DXF  export script
|   |   ├── step.py                           # STEP export script
│   |   ├── tools_airfoil.py            
│   |   ├── tools_program.py            
│   |   ├── tools_reference.py          
│   |   └── tools_wing.py               
|   └── widgets
│       ├── about.py                          # Welcome screen on program init
|       ├── splash_screen.py                  # Splash screen on file load-up
|       ├── table_parameters.py               # Tabele for object properties
|       ├── table_statistics.py               # Tabele for object statistics
|       ├── tool_bar.py                       # Quick access to certain tools
|       ├── tree_airfoils.py                  # Tree of airfoils in the project
|       ├── tree_objects.py                   # Tree of comonents in the project 
|       ├── widget_description.py             # Widget to handle description of project
|       ├── widget_log.py                     # Display log to keep track of functions outcomes
|       ├── widget_progress.py                # Widget to track function progress
|       ├── widget_reference.py               # Widget to handle reference airfoils
|       |
|       └── menu_bar                          # Dropdown menu for file operations
|           ├── menu_bar.py
|           |
|           └── utils
|               ├── menu_edit.py         
|               ├── menu_file.py         
|               ├── menu_module.py        
|               ├── menu_program.py      
|               ├── menu_reference.py        
|               ├── menu_view.py         
|               └── menu_window.py           
├── data                                      # Storage for reference and established files
├── .venv
├── requirements.txt                          # Program dependencies
├── LICENSE                                   # Program licence
├── logo.ico                                  # Program logo
└── README.md                                 # Program documentation
```

## Setup Instructions

1. Clone the repository or download the project files.
2. Navigate to the project directory.
3. Install the required dependencies using pip:

   ```
   pip install -r requirements.txt
   ```

4. Run the application:

   ```
   python src/main.py
   ```

## Setup for MAC OS

1. prerequisites: Homebrew
2. `brew install python`
3. `python3 -m venv myenv`
4. `source myenv/bin/activate`
5. `pip3 install -r requirements.txt`
6. `python3 src/main.py`

## Features

- 2D OpenGl viewport with mouse interaction for Airfoil Designer
  - Translation
  - Zoom
- 3D OpenGL viewport with mouse interaction for Wing designer:
  - Translation
  - Rotation
  - Zoom
- Tree menu for easy navigation of application components.
- Dropdown menu with basic file operations (New, Save, etc.).

## Usage

Once the application is running, you can create a parametric airfoil and wing design. Use interactive tabele of parameters to modify the objects. Interact with the 2D/3D viewport using the mouse to preview created objects. Use the tree menu to navigate through different components of the application. Use export functions to save project to standard CAD format like: .dxf and .step. Use save button to save current state of the project within Daedalus program. 

## License

This project is licensed under the GNU License. See the LICENSE file for more details.
