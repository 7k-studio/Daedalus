# Fit to Reference: Developer Notes

This document records the implementation, objective, empirical defaults, and
validation limits of the **Fit Airfoil to Reference** tool. For the dialog
workflow, see [the user guide](FIT_TO_REFERENCE.md).

Implementation: `src/program/modules/arfdes/fit_2_reference.py`.

## Scope and data flow

`Fit2RefWindow` receives the currently selected airfoil and a reference
airfoil. References may be added from `.arf.ddls`, `.arf`, `.txt`, and `.dat`
files through the Airfoil Designer. The current airfoil is cloned before the
search. `AirfoilFit` updates this clone during optimization; after a successful
run, `_fit_worker_finished` copies the selected parameter values to the
original airfoil and updates its geometry. Cancellation and failed runs do not
apply a partial set of fitted parameters.

Four boundary percentages specify the pressure- and suction-side LE and TE
divisions. They are optimization variables as well as the settings shown in
the dialog:

- Each LE position ranges from `0.0001` chord to its entered initial position.
- Each TE position ranges from its entered initial position to `0.9999` chord.
- The initial validation requires each LE division to precede its matching TE
  division.

These bounds allow the LE cuts to move only toward the nose, and the TE cuts
only toward the tip. Boundary variables influence how contours are divided
and compared; they are not airfoil parameters and are not copied to the
original airfoil when a fit is accepted.

## Contour preparation and distances

`_divide_curves` obtains PS, SS, LE, and TE contours. If the reference exposes
all four spline components, those geometries are used directly. Otherwise, an
ordered XY contour is split at its minimum-X leading edge and maximum-X
trailing edge. Mean Y is used to identify the two sides, then the current
airfoil's pressure-side orientation determines PS versus SS.

The PS and SS surfaces are represented as shape-preserving PCHIP curves over
X. Four chord-percentage cuts create the LE cap, TE cap, and the central PS
and SS regions. For parametric references, their LE and TE splines complete
the caps. The result is four independently compared regions.

The distance calculation is bidirectional and compares points to continuous
PCHIP splines, rather than requiring input vertices to align:

1. Curves are sampled at equal arc-length intervals after duplicate points
   are removed.
2. For each region, the reference curve is resampled to 400 points and the
   current curve to 200 points.
3. Current samples are projected onto a sampled approximation of the
   reference spline; reference samples are projected onto the current spline.
   The closest sampled segment supplies an initial projection, which is
   refined with up to eight Newton steps and clamped to that segment.
4. The two sets of point-to-curve distances are concatenated. The reported
   region minimum, maximum, and average are computed from these distances.

The four regions use the same sampling and distance procedure. The distances
shown in the result table are in the reference's coordinate units. Distances
in the residual plot and objective are divided by the reference chord.

## Objective and weighting

The residual vector is assembled in LE, SS, PS, TE order. For every region,
each normalized point-to-curve distance `d / chord` is multiplied by the
square root of its region weight:

| Residual group | Weight in code | Multiplier on each residual |
|---|---:|---:|
| LE contour distances | 1.0 | 1.0 |
| SS contour distances | 1.0 | 1.0 |
| PS contour distances | 1.0 | 1.0 |
| TE contour distances | 0.35 | about 0.592 |
| TE endpoint X/Y residuals | 8.0 | 8.0 |

The TE endpoint residual vector contains the X and Y difference at each of
the two ends of the TE region, normalized by chord and multiplied directly
by `TE_ANCHOR_RESIDUAL_WEIGHT`. Thus a lower influence for the TE contour
samples does not remove endpoint placement from the objective.

`least_squares` is called with `loss="soft_l1"` and `f_scale=0.002`. The
explicit `_robust_least_squares_cost` used to rank candidates is

```text
cost = f_scale² * sum(sqrt(1 + (residual / f_scale)²) - 1)
```

The soft-L1 form reduces the influence of large individual residuals compared
with a pure sum of squared residuals. It does not remove their influence.
`best_score` is this robust cost, not the unweighted average shown in the
results table.

### Why these weights

The TE contour weight, TE endpoint weight, and robust-loss scale are heuristic
engineering choices. Their intent is to let LE/PS/SS contour shape carry the
main distributed fit, reduce the optimizer's incentive to follow noisy or
isolated TE contour coordinates, and still keep the TE ends placed.

The weights were not determined by a formal global search, statistical
cross-validation, aerodynamic objective, or proof of optimality. The
refinement examples provided qualitative guidance on which geometric regions
and parameter scales needed conservative treatment; they do not establish a
universally optimal weighting. When changing a weight, compare all four
regions, TE endpoint RMS, and the overlaid shape on the same reference set.
Do not judge a weight only by the single scalar `best_score`, since changing a
weight changes that score's definition.

## Parameter bounds and search scales

`_automatic_parameter_bounds` applies two hard safety rules to selected
parameters:

- Every parameter whose path ends in `_slope` is limited to `[-60°, +60°]`.
- Every tangent or curvature length is given a positive minimum of
  `max(chord * 0.0001, 1e-9)` in SI, converted to the parameter's unit.

User-supplied limits are intersected with these automatic limits. A
contradictory interval is rejected before optimization. Other parameters have
no automatic minimum or maximum; their user-entered limits are optional.

`_parameter_search_scale` supplies SciPy's `x_scale`, which controls the
relative step scale used to explore each variable. It is not an additional
residual penalty and does not pull a parameter toward a manual-fit value.

| Parameter family | Search scale |
|---|---:|
| TE tangent/curvature lengths | `0.004 * chord` |
| LE tangent/curvature lengths | `0.015 * chord` |
| PS/SS tangent/curvature lengths | `0.05 * chord` |
| LE/TE thickness | `0.01 * chord` |
| Other non-angle lengths | `0.02 * chord` |
| TE slopes | `5°` |
| Other slopes | `10°` |
| PS/SS angles | `10°` |
| Other angles | `5°` |
| Boundary percentages | `0.01` in normalized chord fraction |

The parameter table initially checks parameters by default and remembers
checkboxes and limits in user settings. Accordingly, users should review the
selection rather than assume only a small set is active.

## Search procedure and candidate selection

`AirfoilFit.optimize` jointly searches the checked airfoil parameters and all
four boundary values. It clamps the starting values to their bounds, applies
finite-bound interior adjustments required by the solver, and passes the
parameter scales to `scipy.optimize.least_squares` with `ftol`, `xtol`, and
`gtol` each set to `1e-9`.

For each objective evaluation, the fitter:

1. Applies the trial values to the working copy and rebuilds the geometry.
2. Rejects self-intersecting contours and geometry that raises a handled
   value, floating-point, or overflow error. Such trials receive a penalty
   residual based on their scaled distance from the last feasible vector.
3. Measures bidirectional distances for all four regions and computes the
   weighted residual vector and robust score for feasible geometry.
4. Stores a feasible candidate when its score is lower than every prior
   feasible score.

The evaluation limit is passed as `max_nfev`; the UI labels it **Maximum
optimizer evaluations**. The fit applies the lowest-scoring feasible
candidate encountered, which need not be SciPy's final trial. If no feasible
candidate is found, the fit fails. The search is bounded and local; it does
not launch automatic multi-start runs.

Residual-history records used for the plot contain the objective evaluation
number, overall average distance, mean max-minus-min spread, anchor RMS, and
minimum/maximum/average distance for each region. The plotted distances are
normalized by chord. The displayed **anchor RMS** is computed from both ends
of all four region comparisons; it is a diagnostic and is not identical to
the TE-only endpoint residual group used by the objective.

The checklist's final condition is true when each region's average distance
is no greater than `0.01 * reference_chord`. This is a progress indicator,
not a fit-acceptance gate or aerodynamic validation.

## Refinement examples and observed baseline

The empirical parameter-scale review used the paired manual airfoils and
coordinate references in `data/refinement`:

| Coordinate reference | Paired manual fit |
|---|---|
| `ah80140.dat` | `ah80140.arf.ddls` |
| `e341.dat` | `e341.arf.ddls` |
| `S1223.txt` | `s1223.arf.ddls` |

Qualitative observations included smaller TE tangent lengths than LE/side
handles, positive observed tangent and curvature lengths, and no slopes near
vertical. These observations informed conservative search scales and guards;
they were not copied as fixed target parameters.

The following are normalized average contour distances measured on the
loaded manual fits before optimization, with the default 7%/93% boundary
positions. Values are in LE/TE/PS/SS order and equal mean point-to-curve
distance divided by reference chord:

| Pair | LE | TE | PS | SS |
|---|---:|---:|---:|---:|
| AH 80-140 | 0.000935 | 0.000881 | 0.000663 | 0.000570 |
| E341 | 0.000388 | 0.000794 | 0.000337 | 0.000474 |
| S1223 | 0.000505 | 0.001566 | 0.002364 | 0.000736 |

These are starting baselines, not post-optimization results or acceptance
thresholds. For example, the relatively larger S1223 PS baseline indicates
that PS behavior deserves inspection on that pair; it does not show that
increasing the global PS weight is the right remedy.

## Regression coverage

`tests/test_fit_2_reference.py` exercises parameter-bound parsing and
validation, continuous spline subdivision, nearest-point projection,
reference resampling, default safe bounds and parameter scales, TE endpoint
residual inclusion, outlier resistance of the robust cost, candidate score
and residual-statistic behavior, and failure when all trial shapes are
invalid. The airfoil wedge tests additionally cover the geometry parameters
used by the fitter.

These are implementation regression tests. The refinement pairs provide a
small empirical calibration set; neither the tests nor these examples
constitute broad airfoil validation or aerodynamic certification.
