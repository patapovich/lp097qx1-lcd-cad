# LP097QX1-SPC1 — LCD mechanical CAD reference

Mounting/mechanical geometry for the **LG Display LP097QX1-SPC1** 9.7" 2048×1536 LCD
panel (as used in iPad 3/4), extracted from the datasheet **FRONT VIEW** drawing for
designing cases, bezels and mounts.

Geometry was pulled from the datasheet PDF's vector drawing and calibrated to the
dimensioned outline. Hole centers were cross-checked two independent ways (vector
path-fit + 2400-DPI raster circle-fit) and agree to **< 0.03 mm**.

![2D overview](images/overview_2d.png)

## Key dimensions (mm)

Datum = module-outline **center**, X → right, Y → up (front view as drawn).

| feature | size (W × H) | center offset | notes |
|---|---|---|---|
| Module outline | 167.12 × 208.88 (±0.5) | (0, 0) | thickness **2.60 max** |
| Bezel / polarizer | 151.608 × 201.01 | (−1.27, −0.86) | visible glass window |
| Active area | 147.456 × 196.608 | (−1.30, −0.89) | **not centered** |

### 4 mounting-lug holes — ⌀2.4 mm

| lug | X | Y | ear |
|---|---|---|---|
| TL | −85.69 | +99.49 | teardrop, points **left** (hole 2.1 outside left edge) |
| TR | +78.11 | +106.58 | gusset, points **up** (hole 2.1 outside top edge) |
| BL | −78.53 | −105.43 | rounded tab, points **down** |
| BR | +78.49 | −107.32 | gusset, points **down** |

> ⚠️ The lug layout is **asymmetric** (not a mirror set). Lugs protrude 3–5 mm past the
> 167.12 × 208.88 outline — your case must clear them.

**Z plane:** the ears split across both faces — **TR & BR** sit on the **front** (screen)
face (Z 2.30–2.60), **TL & BL** on the **rear** face (Z 0–0.30).

![3D model](images/model_3d.png)

![lug planes](images/lug_planes.png)

## Files

| file | description |
|---|---|
| `lcd_panel.step` | 3D solid: body + exact teardrop/gusset lug ears + ⌀2.4 holes + active-area pocket |
| `lcd_panel.stl` | mesh version of the above |
| `lcd_panel.scad` | parametric OpenSCAD source (all dims as variables) |
| `lcd_centerdatum.dxf` | 2D, origin = outline center, Y up |
| `lcd_cornerdatum.dxf` | 2D, origin = outline top-left, Y down (drawing convention) |
| `lcd_lugs.csv` | hole coordinates, both datums |
| `lcd_reference.txt` | full numeric reference |
| `build_step.py` | regenerates the STEP/STL (needs cadquery) |
| `parse_svg.py` | SVG vector-path parser used during extraction |
| `_cal.json`, `_ears.json`, `_rects.json` | extracted geometry consumed by the build scripts |
| `LP097QX1-SPC1.pdf` | source datasheet (© LG Display) |

DXF layers: `OUTLINE`, `BEZEL`, `ACTIVE`, `HOLES`, `HOLE_CENTERS`, `EARS`.

### Lug ear shapes
Traced outlines (magenta) over the datasheet drawing:

![ear TL](images/ear_TL.png) ![ear TR](images/ear_TR.png) ![ear BL](images/ear_BL.png) ![ear BR](images/ear_BR.png)

Lugs are **thin flat sheet-metal tabs (0.30 mm)** — not full-thickness. They sit on
different faces: **TR/BR front** (screen side), **TL/BL rear** (back side).

## Regenerate the 3D model

```bash
python3 -m venv cqenv
cqenv/bin/pip install cadquery
cqenv/bin/python build_step.py      # -> lcd_panel.step + lcd_panel.stl
```

Or render the parametric source with OpenSCAD: `openscad -o lcd_panel.stl lcd_panel.scad`.

## Accuracy

- Rectangle **sizes** = datasheet nominal values.
- Hole positions: ≈ ±0.05 mm relative, ≈ ±0.15 mm absolute (drawing-scale limit).
- Datasheet's own outline tolerance is ±0.5 mm.
- Lug ears are **thin flat sheet-metal tabs (0.30 mm)** split across faces per the
  datasheet side views: **TR/BR front** (Z 2.30..2.60), **TL/BL rear** (Z 0..0.30).

## Source

Datasheet: LG Display LP097QX1-SPC1, mirrored at
<http://mikesmods.com/mm-wp/wp-content/uploads/2013/04/LP097QX1-SPC1.pdf>
(FRONT VIEW, printed page 16/28). The PDF is © LG Display, included here for reference.

Extracted geometry and CAD files in this repo are provided as-is, no warranty — verify
against the datasheet before manufacturing.
