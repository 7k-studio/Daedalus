# Step
### A ###

class AdvancedBrepShapeRepresentation:
    def __init__(self, idx, name, brep_idx, axis_idx, context_idx):
        self.idx = idx
        self.filename = name
        self.brep_idx = brep_idx
        self.axis_idx = axis_idx
        self.context_idx = context_idx

    def export(self):
        return f"#{self.idx} = ADVANCED_BREP_SHAPE_REPRESENTATION ( '{self.filename}', ( #{self.brep_idx}, #{self.axis_idx} ), #{self.context_idx} );"
    
class AdvancedFace:
    def __init__(self, idx, desc=None, fob_idx=None, plane_object=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.face_outer_bound_idx = fob_idx
        self.plane = plane_object
        self.spec = '.T.'

    def export(self):
        return f"#{self.idx} = ADVANCED_FACE ( '{self.desc}', ( #{self.face_outer_bound_idx} ), #{self.plane.idx}, {self.spec} ) ;"

class ApplicationContext:
    def __init__(self, idx, context='configuration controlled 3d designs of mechanical parts and assemblies'):
        self.idx = idx
        self.context = context
    
    def export(self):
        return f"#{self.idx} = APPLICATION_CONTEXT ( '{self.context}' ) ;"

### Application Product Definition
W pliku STEP (ISO 10303) zapis:

#71 = APPLICATION_PROTOCOL_DEFINITION 
( 'international standard', 'config_control_design', 1994, #166 ) ;

to definicja protokołu aplikacyjnego (AP – Application Protocol), czyli informacji jakiego standardu STEP używa dany plik i według jakich zasad jest zorganizowany model danych.

Describes the standard for the product

> #index = APPLICATION_PROTOCOL_DEFINITION ( a, b, c, d ) ;

| Pozycja | Znaczenie                         | Typ           |
| ------- | --------------------------------- | ------------- |
| `a`     | status standardu                  | STRING        |
| `b`     | nazwa protokołu aplikacyjnego     | STRING        |
| `c`     | rok publikacji wersji AP          | INTEGER       |
| `d`     | referencja do APPLICATION_CONTEXT | ENTITY (#...) |


```python
class ApplicationProtocolDefinition:
    def __init__(self, idx, status='international standard', protocol='config_control_design', publication_year='1994', application_context=None):
        self.idx = idx
        self.standard = 'ISO 10303-203'
        self.status = status
        self.protocol = protocol
        self.publication_year = publication_year
        self.application_context = application_context
    
    def export(self):  
        return f"#{self.idx} = APPLICATION_PROTOCOL_DEFINITION ( '{self.status}', '{self.protocol}', {self.publication_year}, #{self.application_context.idx} ) ;"
```        
Szczegóły Twojego wpisu
1. 'international standard'
Status dokumentu STEP
Oznacza, że użyty protokół jest zatwierdzony jako międzynarodowy standard ISO
Inne możliwe wartości:
'draft international standard'
'committee draft'
2. 'config_control_design'
Nazwa protokołu aplikacyjnego (AP)
To jest bardzo istotne — mówi jakiego typu dane zawiera plik

👉 'config_control_design' odpowiada:

ISO 10303-203
Czyli:
klasyczny STEP dla mechaniki
geometria + struktura produktu + kontrola konfiguracji
używany np. w starszych systemach CAD
3. 1994
Rok publikacji tej wersji AP
Dla AP203:
1994 = pierwsza wersja
później były rewizje (np. AP203e2)
4. #166
Referencja do encji:
#166 = APPLICATION_CONTEXT ( 'configuration controlled 3d designs of mechanical parts and assemblies' ) ;
Określa kontekst zastosowania danych
Czyli:
jakie dziedziny obejmuje model
np. mechanika, elektryka, PDM itd.
🔹 Co to oznacza praktycznie?

Ten wpis mówi parserowi STEP:

„Ten plik jest zgodny z AP203 (config_control_design), opublikowanym jako standard ISO w 1994 roku i dotyczy kontrolowanych konfiguracji projektów 3D.”

🔹 Dlaczego to ważne?

Bo różne AP mają różne możliwości:

AP	Zastosowanie
AP203	klasyczna mechanika
AP214	automotive + kolory + warstwy
AP242	nowoczesny standard (PMI, MBD)

Czyli:

ten wpis determinuje jak interpretować resztę pliku
wpływa na:
dostępne encje
semantykę danych
kompatybilność między CAD
🔹 Podsumowanie (w skrócie)
APPLICATION_PROTOCOL_DEFINITION

= deklaracja:

✔ jaki standard STEP
✔ jaka wersja
✔ do czego służy
✔ w jakim kontekście działa
    
class Approval:
    def __init__ (self, idx, status_idx=None, spec='UNSPECIFIED'):
        self.idx = idx
        self.status_idx = status_idx
        self.spec = spec
    
    def export(self):
        return f"#{self.idx} = APPROVAL ( #{self.status_idx}, '{self.spec}' ) ;"
    
class ApprovalStatus:
    def __init__ (self, idx, status='not_yet_approved'):
        self.idx = idx
        self.status = status
    
    def export(self):
        return f"#{self.idx} = APPROVAL_STATUS ( '{self.status}' ) ;"
    
class Axis2Placement3D:
    def __init__(self, idx, desc=None, cp_idx=None, dir1_idx=None, dir2_idx=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.cp_idx = cp_idx
        self.dir1_idx = dir1_idx
        self.dir2_idx = dir2_idx
    
    def export(self):
        return f"#{self.idx} = AXIS2_PLACEMENT_3D ( '{self.desc}', #{self.cp_idx}, #{self.dir1_idx}, #{self.dir2_idx} ) ;"

### B ###

class BsplineWithKnots:
    def __init__(self, idx, desc=None, cartesian_points=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.degree= len(cartesian_points)-1
        self.points = cartesian_points
        self.spline = tools.CreateBSpline_3D([np.array([cp.X for cp in cartesian_points]),np.array([cp.Y for cp in cartesian_points]),np.array([cp.Z for cp in cartesian_points])], len(cartesian_points), 100)
        self.spec1 = '.UNSPECIFIED.'
        self.orientation_flag_1 = '.F.'
        self.orientation_flag_2 = '.F.'
        self.uv_grid_points_number = [len(cartesian_points),len(cartesian_points)]
        self.length = self.calc_the_length()
        self.spec6 = '.UNSPECIFIED.'

    def calc_the_length(self):
        
        if self.spline != None:
            points = np.stack((self.spline), axis=-1)
            distances = np.linalg.norm(np.diff(points, axis=0), axis=1)
            curve_length = np.sum(distances)
        
        length = float(curve_length)
        
        return length

    
    def export(self):
        knots = ', '.join([f'#{obj.idx}' for obj in self.points])
        return f"#{self.idx} = B_SPLINE_CURVE_WITH_KNOTS ( '{self.desc}', {self.degree}, ( {knots} ), {self.spec1}, {self.orientation_flag_1}, {self.orientation_flag_2}, ( {self.uv_grid_points_number[0]}, {self.uv_grid_points_number[1]} ), ( 0, {self.length} ), {self.spec6} ) ;"

class BSplineSurfaceWithKnots:
    def __init__(self, idx, desc, u_degree, v_degree, cp_uv_grid, knots_u, knots_v):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.u_degree = u_degree
        self.v_degree = v_degree
        self.uv_grid = cp_uv_grid
        self.knots_u = knots_u
        self.knots_v = knots_v

    def export(self):

        # --- Create b spline from u direction ---
        u_dir_cp = []
        for j in range(len(self.uv_grid)):
            u_group = ', '.join([f'#{self.uv_grid[j][k].idx}' for k in range(len(self.uv_grid[j]))])
            bracket = f"( {u_group} )"
            u_dir_cp.append(bracket)
        
        spline_group = ', '.join([f'{vec}' for vec in u_dir_cp])

        return (
            f"#{self.idx} = B_SPLINE_SURFACE_WITH_KNOTS ( '{self.desc}', {self.u_degree}, {self.v_degree}, ( "
            f"{spline_group}"
            "),.UNSPECIFIED., .F., .F., .F.,"
            f"( {self.u_degree+1}, {self.u_degree+1} ),( {self.v_degree+1}, {self.v_degree+1} ),"
            f"( {self.knots_u[0]}, {self.knots_u[1]} ),"
            f"( {self.knots_v[0]}, {self.knots_v[1]} ),.UNSPECIFIED. );"
        )
    
### C ###

class CartesianPoint:
    def __init__(self, idx, desc=None, X=None, Y=None, Z=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.X = X
        self.Y = Y
        self.Z = Z
    
    def export(self):
        return f"#{self.idx} = CARTESIAN_POINT ( '{self.desc}', ( {self.X}, {self.Y}, {self.Z} ) ) ;"

class CCDesignAproval:
    def __init__(self, idx, approval_idx, pdfwss_idx):
        self.idx = idx
        self.approval_idx = approval_idx
        self.product_def_for_with_specified_source_idx = pdfwss_idx
    
    def export(self):
        return f"#{self.idx} = CC_DESIGN_APPROVAL ( #{self.approval_idx}, ( #{self.product_def_for_with_specified_source_idx} ) ) ;"

class ClosedShell:
    def __init__(self, idx, face_indices):
        self.idx = idx
        self.face_indices = face_indices

    def export(self):
        faces = ', '.join([f'#{i}' for i in self.face_indices])
        return f"#{self.idx} = CLOSED_SHELL ( 'NONE', ( {faces} ) );"

class CoordinatedUniversalTimeOffset:
    def __init__(self, idx):
        self.idx = idx
        self.a_or_b = '.AHEAD.'
    
    def export(self):
        return f"#{self.idx} = COORDINATED_UNIVERSAL_TIME_OFFSET ( 1, 0, {self.a_or_b} ) ;"

### D ###
    
class DateTimeRole:
    def __init__(self, idx, role='NONE'):
        self.idx = idx
        self.role = role #creation date / classification_date
    
    def export(self):
        return f"#{self.idx} = DATE_TIME_ROLE ( '{self.role}' );"

class DesignContext:
    def __init__(self, idx, application_context_obj):
        self.idx = idx
        self.desc = "detailed design"
        self.application_context = application_context_obj
        self.label = "design"

    def export(self):
        return f"#{self.idx} = DESIGN_CONTEXT ( '{self.desc}', #{self.application_context.idx}, '{self.label}' ) ;"

class Direction:
    def __init__(self, idx, desc=None, vec=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.vec = vec
    
    def export(self):
        return f"#{self.idx} = DIRECTION ( '{self.desc}', ( {self.vec[0]}, {self.vec[1]}, {self.vec[2]} ) );"

### E ###

class EdgeCurve:
    def __init__(self, idx, desc=None, VP1=None, VP2=None, Curv=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.vertex_point_1 = VP1
        self.vertex_point_2 = VP2
        self.curve = Curv
        self.orientation_flag = '.T.'
    
    def export(self):
        return f"#{self.idx} = EDGE_CURVE ( '{self.desc}', #{self.vertex_point_1.idx}, #{self.vertex_point_2.idx}, #{self.curve.idx}, {self.orientation_flag} ) ;"    
    
class EdgeLoop:
    def __init__(self, idx, desc=None, OrientedEdge_list=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.OrientedEdge_list = OrientedEdge_list
    
    def export(self):
        oriented_edges = ', '.join([f'#{obj.idx}' for obj in self.OrientedEdge_list])
        return f"#{self.idx} = EDGE_LOOP ( '{self.desc}', ( {oriented_edges} ) ) ;"
    
### F ###

class FaceOuterBounds:
    def __init__(self, idx, desc=None, edge_loop=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.edge_loop = edge_loop
        self.spec = '.T.'

    def export(self):
        return f"#{self.idx} = FACE_OUTER_BOUND ( '{self.desc}', #{self.edge_loop.idx}, {self.spec} ) ;"
    
### G ###

class GeometricSet:
    def __init__(self, idx, desc=None, group_idx=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.group_idx = group_idx
    
    def export(self):
        return f"#{self.idx} = GEOMETRIC_SET ( '{self.desc}', ( {', '.join([f'#{idx}' for idx in self.group_idx])} ) ) ;"
    
class GeometricRepresentationContext:
    def __init__(self, idx, u_idx, lu_idx, sa_idx, pa_idx):
        self.idx = idx
        self.uncertatnity_idx = u_idx
        self.length_unit_idx = lu_idx
        self.solid_angle_idx = sa_idx
        self.plane_angle_idx = pa_idx
    
    def export(self):
        return f"#{self.idx} = ( GEOMETRIC_REPRESENTATION_CONTEXT ( 3 ) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT ( ( #{self.uncertatnity_idx} ) ) GLOBAL_UNIT_ASSIGNED_CONTEXT ( ( #{self.length_unit_idx}, #{self.plane_angle_idx}, #{self.solid_angle_idx} ) ) REPRESENTATION_CONTEXT ( 'NONE', 'WORKSPACE' ) );"

class GeometricallyBoundedSurfaceShapeRepresentation:
    def __init__(self, idx, desc=None, gs_idx=0, gr_idx=0):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.geometric_set_idx = gs_idx
        self.geom_representation_idx = gr_idx 

    def export(self):
        return f"#{self.idx} = GEOMETRICALLY_BOUNDED_SURFACE_SHAPE_REPRESENTATION ( '{self.desc}', ( #{self.geometric_set_idx} ), #{self.geom_representation_idx} ) ;"
    
### H ###
### I ###
### J ###
### K ###
### L ###

class LengthUnit:
    def __init__(self, idx, length_unit):
        self.idx = idx
        if length_unit == 'm':
            self.unit = ['$', '.METRE.']
        if length_unit == 'mm':
            self.unit = ['.MILLI.', '.METRE.']
    
    def export(self):
        return f"#{self.idx} = ( LENGTH_UNIT ( ) NAMED_UNIT ( * ) SI_UNIT ( {self.unit[0]}, {self.unit[1]} ) );"

class Line:
    def __init__(self, current_idx, cartesian_point_obj, vector_obj, length):
        self.idx = current_idx
        self.desc = 'NONE'
        self.cartesian_point = cartesian_point_obj
        self.vector = vector_obj
        self.length = length
    
    def export(self):
        return f"#{self.idx} = LINE ( '{self.desc}', #{self.cartesian_point.idx}, #{self.vector.idx} ) ;"
    
### M ###

class ManifoldSurfaceShapeRepresentation:
    def __init__(self, idx, desc=None, sbsm_idx=None, a2p3d_idx=None, gp_idx=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.shell_based_surf_model_idx = sbsm_idx
        self.axis2_placement_3d_idx = a2p3d_idx
        self.geom_representation_idx = gp_idx
    
    def export(self):
        return f"#{self.idx} = MANIFOLD_SURFACE_SHAPE_REPRESENTATION ( '{self.desc}', ( #{self.shell_based_surf_model_idx}, #{self.axis2_placement_3d_idx} ), #{self.geom_representation_idx} ) ;"

class MechanicalContext:
    def __init__ (self, idx, desc=None, application_context_obj=None, context='mechanical'):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.app_context = application_context_obj
        self.context = context
    
    def export(self):
        return f"#{self.idx} = MECHANICAL_CONTEXT ( '{self.desc}', #{self.app_context.idx}, '{self.context}' ) ;"
    
### N ###
### O ###

class OpenShell:
    def __init__(self, idx, desc=None, af_obj=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.advanced_face_list = af_obj
    
    def export(self):
        advanced_faces = ', '.join([f'#{obj.idx}' for obj in self.advanced_face_list])
        return f"#{self.idx} = OPEN_SHELL ( '{self.desc}', ( {advanced_faces} ) ) ;"

class OrientedEdge:
    def __init__(self, idx, desc=None, ec_obj=None, orientation=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.var2 = '*'
        self.var3 = '*'
        self.edge_curve = ec_obj
        self.orientation_flag = f'.{orientation}.'

    def export(self):
        return f"#{self.idx} = ORIENTED_EDGE ( '{self.desc}', {self.var2}, {self.var3}, #{self.edge_curve.idx}, {self.orientation_flag} ) ;"
    
### P ###

class Plane:
    def __init__(self, idx, desc=None, ax_idx=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.ax2_placement_idx = ax_idx
    
    def export(self):
        return f"#{self.idx} = PLANE ( '{self.desc}', #{self.ax2_placement_idx} ) ;"

class PlaneAngleUnit:
    def __init__(self, idx, angle_unit):
        self.idx = idx
        if angle_unit == 'rad':
            self.angle_unit = '.RADIAN.' 
    
    def export(self):
        return f"#{self.idx} = ( NAMED_UNIT ( * ) PLANE_ANGLE_UNIT ( ) SI_UNIT ( $, {self.angle_unit} ) );"

class Product:
    def __init__(self, idx, name, mechanical_context_obj):
        self.idx = idx
        self.name = name
        self.mechanical_context = mechanical_context_obj

    def export(self):
        return f"#{self.idx} = PRODUCT ( '{self.name}', '{self.name}', '', ( #{self.mechanical_context.idx} ) );"

class ProductDefinition:
    def __init__(self, idx=None, desc='UNKNOWN', spec1="", prod_def_form_w_spec_source=None, design_context=None):
        self.idx = idx
        self.description = desc
        self.spec1 = spec1
        self.pdfwss = prod_def_form_w_spec_source
        self.des_con = design_context

    def export(self):
        return f"#{self.idx} = PRODUCT_DEFINITION ( '{self.description}', '{self.spec1}', #{self.pdfwss.idx}, #{self.des_con.idx} ) ;"

class ProductDefinitionFormationWithSpecifiedSource:
    def __init__(self, idx, product):
        self.idx = idx
        self.var1 = 'ANY'
        self.var2 = ''
        self.product = product
        self.spec = '.NOT_KNOWN.'
    
    def export(self):
        return f"#{self.idx} = PRODUCT_DEFINITION_FORMATION_WITH_SPECIFIED_SOURCE ( '{self.var1}', '{self.var2}', #{self.product.idx}, {self.spec} ) ;"

class ProductDefinitionShape:
    def __init__(self, idx, product_definition):
        self.idx = idx
        self.spec1 = "NONE"
        self.spec2 = "NONE"
        self.product_definition = product_definition

    def export(self):
        return f"#{self.idx} = PRODUCT_DEFINITION_SHAPE ( '{self.spec1}', '{self.spec2}', #{self.product_definition.idx} );"

### Q ###
### R ###
### S ###

class ShapeDefinitionRepresentation:
    def __init__(self, idx, product_definition_shape, manifold_surf_shape_rep):
        self.idx = idx
        self.product_def_shape = product_definition_shape #pds_idx bez tego zdaje się działać
        self.manifold_surf_shape_rep = manifold_surf_shape_rep
    
    def export(self):
        return f"#{self.idx} = SHAPE_DEFINITION_REPRESENTATION ( #{self.product_def_shape.idx}, #{self.manifold_surf_shape_rep.idx} ) ;"
    
class ShellBasedSurfaceModel:
    def __init__(self, idx, desc=None, os_idx=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.open_shell_idx = os_idx
    
    def export(self):
        return f"#{self.idx} = SHELL_BASED_SURFACE_MODEL ( '{self.desc}', ( #{self.open_shell_idx} ) ) ;"

class SolidAngleUnit:
    def __init__(self, idx, angle_unit):
        self.idx = idx
        if angle_unit == 'rad':
            self.angle_unit = '.STERADIAN.' 

    def export(self):
        return f"#{self.idx} = ( NAMED_UNIT ( * ) SI_UNIT ( $, {self.angle_unit} ) SOLID_ANGLE_UNIT ( ) );"

### T ###
### U ###

class UncertaintyMeasure:
    def __init__(self, idx, lu_idx):
        self.idx = idx
        self.length_unit_idx = lu_idx
    
    def export(self):
        return f"#{self.idx} = UNCERTAINTY_MEASURE_WITH_UNIT (LENGTH_MEASURE( 1.000000000000000082E-05 ), #{self.length_unit_idx}, 'distance_accuracy_value', 'NONE');"
    
### V ###

class Vector:
    def __init__(self, current_idx, direction_obj):
        self.idx = current_idx
        self.desc = 'NONE'
        self.direction = direction_obj
        self.magnitude = format(1.0, '.5f')

    def export(self):
        return f"#{self.idx} = VECTOR ( '{self.desc}', #{self.direction.idx}, {self.magnitude} ) ;"
    
class VertexPoint:
    def __init__(self, idx, desc=None, cp_index=None):
        self.idx = idx
        self.desc = desc if desc != None else 'NONE'
        self.cartesian_point_idx = cp_index
    
    def export(self):
        return f"#{self.idx} = VERTEX_POINT ( '{self.desc}', #{self.cartesian_point_idx} ) ;"
    
### W ###
### X ###
### Y ###
### Z ###
C:\Users\jakub\AppData\Local\DassaultSystemes\CATReport\Formula Student FW.err

Input file: D:\Programy\7kStudio\demo\Formula Student FW.step
Output file: 

============================================
*** = Processing new independent element
  * = Intermediate processing
!!  = Independent element K.O.
!   = Intermediate error
--------------------------------------------
<I> = Information
<W> = Warning
<E> = Error
--------------------------------------------
[0000]  = Message identifier : 0000
[T=xxx] = Entity Type : xxx
[#0000] = Entity identifier number : 0000
============================================
Actual display level : Customer

   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#38] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#29] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#35] The tangent extremity of the BSpline curve is null  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#110] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#101] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#107] The tangent extremity of the BSpline curve is null  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#74] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#65] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#71] The tangent extremity of the BSpline curve is null  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#146] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#137] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#143] The tangent extremity of the BSpline curve is null  
   <W> [0903] [T=OPEN_SHELL] [#447] Surface created with errors; trying to repair  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#38] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#29] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#35] The tangent extremity of the BSpline curve is null  
!! <E> [0002] [T=ADVANCED_FACE] [#41] Element not created  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#38] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#29] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#35] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#29] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#35] The tangent extremity of the BSpline curve is null  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#38] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#29] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#35] The tangent extremity of the BSpline curve is null  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#38] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#29] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#35] The tangent extremity of the BSpline curve is null  
   <I> [0060] [T=ADVANCED_FACE] [#41] Bad face/surface orientation. Problem fixed  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#110] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#101] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#107] The tangent extremity of the BSpline curve is null  
!! <E> [0002] [T=ADVANCED_FACE] [#113] Element not created  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#110] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#101] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#107] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#101] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#107] The tangent extremity of the BSpline curve is null  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#110] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#101] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#107] The tangent extremity of the BSpline curve is null  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#110] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#101] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#107] The tangent extremity of the BSpline curve is null  
   <I> [0060] [T=ADVANCED_FACE] [#113] Bad face/surface orientation. Problem fixed  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#74] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#65] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#71] The tangent extremity of the BSpline curve is null  
!! <E> [0002] [T=ADVANCED_FACE] [#77] Element not created  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#74] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#65] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#71] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#65] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#71] The tangent extremity of the BSpline curve is null  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#74] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#65] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#71] The tangent extremity of the BSpline curve is null  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#74] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#65] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#71] The tangent extremity of the BSpline curve is null  
   <I> [0060] [T=ADVANCED_FACE] [#77] Bad face/surface orientation. Problem fixed  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#146] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#137] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#143] The tangent extremity of the BSpline curve is null  
!! <E> [0002] [T=ADVANCED_FACE] [#149] Element not created  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#146] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#137] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#143] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#137] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#143] The tangent extremity of the BSpline curve is null  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#146] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#137] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#143] The tangent extremity of the BSpline curve is null  
   <W> [0224] [T=B_SPLINE_SURFACE_WITH_KNOTS] [#146] The tangent extremity of the BSpline surface is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#137] The tangent extremity of the BSpline curve is null  
   <W> [0166] [T=B_SPLINE_CURVE_WITH_KNOTS] [#143] The tangent extremity of the BSpline curve is null  
   <I> [0060] [T=ADVANCED_FACE] [#149] Bad face/surface orientation. Problem fixed  
!! <E> [0002] [T=ADVANCED_FACE] [#188] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#188] Bad face/surface orientation. Problem fixed  
!! <E> [0002] [T=ADVANCED_FACE] [#260] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#260] Bad face/surface orientation. Problem fixed  
!! <E> [0002] [T=ADVANCED_FACE] [#224] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#224] Bad face/surface orientation. Problem fixed  
!! <E> [0002] [T=ADVANCED_FACE] [#296] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#296] Bad face/surface orientation. Problem fixed  
!! <E> [0002] [T=ADVANCED_FACE] [#335] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#335] Bad face/surface orientation. Problem fixed  
!! <E> [0002] [T=ADVANCED_FACE] [#407] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#407] Bad face/surface orientation. Problem fixed  
!! <E> [0002] [T=ADVANCED_FACE] [#371] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#371] Bad face/surface orientation. Problem fixed  
!! <E> [0002] [T=ADVANCED_FACE] [#443] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#443] Bad face/surface orientation. Problem fixed  
   <I> [0776] [T=OPEN_SHELL] [#447] The entity name is Wing from segment
	o~~~~~~~~~~~~~~~~~~~~~~~~~~o
   <W> [0903] [T=OPEN_SHELL] [#579] Surface created with errors; trying to repair  
!! <E> [0002] [T=ADVANCED_FACE] [#479] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#479] Bad face/surface orientation. Problem fixed  
!! <E> [0002] [T=ADVANCED_FACE] [#543] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#543] Bad face/surface orientation. Problem fixed  
!! <E> [0002] [T=ADVANCED_FACE] [#511] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#511] Bad face/surface orientation. Problem fixed  
!! <E> [0002] [T=ADVANCED_FACE] [#575] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#575] Bad face/surface orientation. Problem fixed  
   <I> [0776] [T=ADVANCED_FACE] [#479] The entity name is ps surface
   <I> [0776] [T=ADVANCED_FACE] [#543] The entity name is le surface
   <I> [0776] [T=ADVANCED_FACE] [#511] The entity name is ss surface
   <I> [0776] [T=ADVANCED_FACE] [#575] The entity name is te surface
!! <E> [0002] [T=OPEN_SHELL] [#579] Element not created  
	o~~~~~~~~~~~~~~~~~~~~~~~~~~o
   <W> [0903] [T=OPEN_SHELL] [#711] Surface created with errors; trying to repair  
!! <E> [0002] [T=ADVANCED_FACE] [#611] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#611] Bad face/surface orientation. Problem fixed  
!! <E> [0002] [T=ADVANCED_FACE] [#675] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#675] Bad face/surface orientation. Problem fixed  
!! <E> [0002] [T=ADVANCED_FACE] [#643] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#643] Bad face/surface orientation. Problem fixed  
!! <E> [0002] [T=ADVANCED_FACE] [#707] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#707] Bad face/surface orientation. Problem fixed  
   <I> [0776] [T=ADVANCED_FACE] [#611] The entity name is ps surface
   <I> [0776] [T=ADVANCED_FACE] [#675] The entity name is le surface
   <I> [0776] [T=ADVANCED_FACE] [#643] The entity name is ss surface
   <I> [0776] [T=ADVANCED_FACE] [#707] The entity name is te surface
!! <E> [0002] [T=OPEN_SHELL] [#711] Element not created  
	o~~~~~~~~~~~~~~~~~~~~~~~~~~o
   <W> [0903] [T=OPEN_SHELL] [#843] Surface created with errors; trying to repair  
!! <E> [0002] [T=ADVANCED_FACE] [#743] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#743] Bad face/surface orientation. Problem fixed  
!! <E> [0002] [T=ADVANCED_FACE] [#807] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#807] Bad face/surface orientation. Problem fixed  
!! <E> [0002] [T=ADVANCED_FACE] [#775] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#775] Bad face/surface orientation. Problem fixed  
!! <E> [0002] [T=ADVANCED_FACE] [#839] Element not created  
   <I> [0060] [T=ADVANCED_FACE] [#839] Bad face/surface orientation. Problem fixed  
   <I> [0776] [T=ADVANCED_FACE] [#743] The entity name is ps surface
   <I> [0776] [T=ADVANCED_FACE] [#807] The entity name is le surface
   <I> [0776] [T=ADVANCED_FACE] [#775] The entity name is ss surface
   <I> [0776] [T=ADVANCED_FACE] [#839] The entity name is te surface
!! <E> [0002] [T=OPEN_SHELL] [#843] Element not created  
	o~~~~~~~~~~~~~~~~~~~~~~~~~~o
✅ Great progress - issue identified and there is a clean fix
Excellent news: your CATIA report is directly pointing to a degenerate spline/tangent issue, and the code path is clear. The main problem is not only connection selection in step.py (that’s already fixed) but the actual control-point configuration that feeds those splines.

🔎 What CATIA errors mean
B_SPLINE_CURVE_WITH_KNOTS [...] tangent extremity is null
=> start/end tangent = 0, typically because first two or last two control points are identical (degenerate direction).
ADVANCED_FACE element not created / bad face orientation
=> geometry happened, but boundary edge/surface invalid or degenerate.
In your STEP output:

curves #29, #35, #65, #71, #101, #107, #137, #143 etc are all the 4 “edge” curves used for inter-segment faces.
in the faulty write path, these are B-splines with repeated first/last control points, so CATIA warns.
🛠️ Where to change in step.py
1. connection = [...] line in export_3d_segment_wing
Already fixed:

from [connection = [wing.segments[i].anchor, wing.segments[i].anchor]](http://vscodecontentref/5) (wrong)
to [connection = [wing.segments[i].anchor, wing.segments[i+1].anchor]](http://vscodecontentref/6) (correct)
2. In _write_oriented_edge_from_uv_grid(...), add a duplicate-point guard
Current else and if connection == G0-G0 branches build 4-slot splines by raw control points taken from cp_uv_grid.
If points are repeated:

B_SPLINE with repeated endpoint -> null tangent warnings
surfaces built with these edges can fail.
Recommended step.py hedge:

normalize each edge point list before creating BsplineWithKnots:
remove consecutive duplicates,
if 2 points left → use Line (or degree=1 B-spline),
if <2 → skip / use degenerate abort path.
specifically for G0-G1 and G1-G0: do not let the tangent-control revisit same anchor exactly.
Example sketch in _write_oriented_edge_from_uv_grid:

for edge curve points:
curve_pts = remove_consecutive_duplicates(raw_pts)
if len(curve_pts) == 2: line path
else: BsplineWithKnots(... curve_pts ...)
🧩 Even better: fix in class_wing.build_connection too
This function prepares the control points used by STEP exporter.
In current code:

G0-G1: parent_*_tan_cp = parent_anchor (same as endpoint) → safe? no, this causes null tangent on parent side.
G1-G0: child_*_tan_cp incorrectly uses parent_*_seg_anchor instead of child_*_seg_anchor.
So stronger fix chain:

correct G1-G0 to use child_*_seg_anchor for child tangent points (with +0 not parent coordinate)
avoid copying endpoint as tangent point:
G0-G1 should have tiny offset or valid point, not exact duplicate.
G1-G0 likewise.
Then step exporter outputs better splines and warnings should disappear.
🧾 Summary for “what to do in step.py”
step.py should treat G0-G1 and G1-G0 as spline (already done)
add robust dedup logic before constructing each boundary spline
fallback to Line when spline control points collapse to a straight/duplicate pair
maybe also ensure vector/direction is valid (for degenerate length close to zero)
This will eliminate the “tangent extremity null” warnings and make surfaces valid in CATIA.

🎯 Final note
You’ve already removed the first bug. The remaining CATIA errors are consistent with degeneracy in control points on the boundary splines, which is fixed by:

build_connection math fix, and
step.py guard around repeated control points before writing B_SPLINE_CURVE_WITH_KNOTS.