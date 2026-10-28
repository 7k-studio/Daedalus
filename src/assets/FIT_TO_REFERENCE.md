# Fit an Airfoil to a Reference

This guide explains how to use **Fit Airfoil to Reference** in the Airfoil
Designer to make a Daedalus parametric airfoil follow a coordinate or DDLS
reference.

## Before you start

- Open or create a project and select the airfoil you want to modify in the
  Airfoil Designer tree. The fit starts from this airfoil's current shape.
- Have a reference ready. The tool accepts `.txt`, `.dat`, `.arf`, and
  `.arf.ddls` files. Coordinate files should contain one ordered airfoil
  contour with finite X/Y coordinates.
- Keep in mind that the fit is geometric: it matches contours, not lift,
  drag, stability, or other aerodynamic properties.

## Workflow

1. Open **Fit Airfoil to Reference** for the selected airfoil.
2. Choose a project reference from **Reference airfoil**, or select **Add
   reference…** to load a file. Check that the preview displays the intended
   reference and its four colored regions.
3. Review the four **LE / TE definitions**. They are percentages of chord,
   measured from 0% at the leading edge to 100% at the trailing edge. The LE
   positions define where the leading-edge cap joins the pressure and suction
   surfaces; the TE positions define the corresponding trailing-edge joins.
   Move the divisions if they cut across an important shape feature or leave
   a region empty. The preview updates as you change them.
4. In **Parameter specification**, check the parameters that should be allowed
   to change. Start with only the parameters relevant to the mismatch. Leave
   unrelated parameters unchecked.
5. Optionally enter a minimum and/or maximum for each selected parameter.
   Values use the units shown in the table. Leave a field blank when you do
   not need an additional limit. To keep a parameter fixed, uncheck it; if it
   must remain selected, set equal minimum and maximum values.
6. Keep the automatic safeguards in mind: tangent and curvature lengths must
   stay positive, and spline slopes are restricted to ±60°. User limits must
   be compatible with these safe ranges.
7. Set **Maximum optimizer evaluations**. The default is a practical starting
   budget, not a required number of iterations or a guarantee of convergence.
8. Select **Proceed**. The preview, residual plot, parameter values, and
   region-distance table update while fitting. Use **Cancel** to abandon the
   run.
9. When fitting finishes, inspect the overlaid contours and the LE, TE, PS,
   and SS minimum, maximum, and average distances. Review the residual plot
   for persistent regional errors and the preview connectors for local
   departures.
10. If the result is not satisfactory, close or cancel without accepting it,
    adjust the divisions, parameter selection, or bounds, and try again. If
    the residual pattern suggests a different local solution, start from a
    different plausible airfoil shape.
11. Select **Done** to accept a successful fit. Only the selected airfoil
    parameters are applied to the original airfoil; cancelling or a failed
    run does not apply a partial fit.

Parameter selections, bounds, reference choice, and divisions are remembered
as fitting preferences on this computer. Review them when fitting a different
airfoil; limits that were useful for one shape may be unsuitable for another.

## Best practices

- Begin with the fewest parameters that can explain the visible mismatch.
  For example, correct overall placement or chord/thickness before freeing
  multiple spline handles. Then address the specific LE, pressure-side, or
  suction-side region that remains discrepant.
- Add parameter families in stages. A smaller parameter set is easier to
  interpret and lets the evaluation budget focus on fewer coupled variables.
- Use bounds to encode design knowledge and prevent implausible changes.
  Tighten them around a known feasible range rather than opening very wide
  ranges in the hope that the optimizer will find a good shape.
- Keep trailing-edge tangent and curvature bounds especially deliberate.
  The fit gives TE contour samples less influence than the other regions, but
  explicitly anchors the TE endpoints. This reduces chasing isolated noisy
  tip points; it does not make an unsuitable TE division or unrealistic TE
  shape acceptable.
- Treat the preview and per-region errors as complementary evidence. A low
  average can conceal a localized error, so inspect maximum distance and the
  connector plot as well.
- Increase the evaluation limit only after checking divisions and narrowing
  the parameter set. More evaluations cannot fix a malformed reference,
  incompatible geometry, or an unsuitable set of bounds.
- Save a copy of an important starting airfoil before accepting a fit if you
  want a convenient way to compare alternatives.

## Understanding the results

The results table gives minimum, maximum, and average contour distances for
each of the four regions in the reference's coordinate units. The residual
plot uses distances normalized by reference chord, making its scales more
comparable between differently sized airfoils. These values are geometric
distances, not percentages of aerodynamic performance.

The checklist's average-distance target is a visual aid, not a certification
that the shape is suitable for a particular application. The optimizer is
bounded and local: it returns the best feasible candidate it evaluated for
the selected starting airfoil, divisions, parameters, and bounds. It does not
guarantee a global best fit or aerodynamic equivalence.

## Troubleshooting

| Symptom | What to check |
|---|---|
| No usable surfaces or preview | Check that the coordinate file contains enough finite X/Y points in a single ordered contour. Confirm that the LE and TE divisions are valid. |
| Zero chord or empty region | Check that the reference has nonzero chord and that each LE division is ahead of its corresponding TE division. |
| A bound is rejected | Use finite numeric values in the displayed units. Ensure minimum is no greater than maximum and that the limits allow the automatic slope or positive-length safeguards. |
| Fit cannot find a valid shape | Restore a plausible starting shape, fit fewer parameters, and tighten bounds that permit extreme coupled changes. Self-intersecting candidate contours are rejected. |
| Fit finishes with visible residuals | Inspect which region remains high, verify its divisions, and enable or free only the parameter family that can affect it. Try another plausible starting shape if the fit appears trapped. |
| TE maximum remains high | Inspect the TE division and tip coordinates. A sharp or noisy tip may not be representable by a smooth parametric edge; avoid fitting isolated coordinate noise. |
| Fit stops before the shape is satisfactory | Check whether the evaluation limit was reached. First review the selected parameters and bounds; then increase the limit if a useful search is still underway. |

For implementation details, calibration examples, tests, weighting, and the
optimizer's exact objective, see [Fit to Reference: developer notes](FIT_TO_REFERENCE_DEVELOPER.md).
