# LP097QX1-SPC1 — LCD mechanical CAD reference

Mounting/mechanical geometry for the **LG Display LP097QX1-SPC1** 9.7" 2048×1536 LCD
panel (as used in iPad 3/4), extracted from the datasheet **FRONT VIEW** drawing for
designing cases, bezels and mounts.

Geometry was **re-traced from a colour-cleaned render** of the FRONT VIEW: the
datasheet page is rasterized and every non-geometry marking (dimension lines,
dash-dot centerlines, green active-area reference, page header) is stripped *by
colour*, leaving only the black/grey object outline. The outline, 4 lug ears and
holes are then traced from that clean image and self-calibrated to the
167.12 × 208.88 outline. Hole centers cross-check against an independent
dimension-line calibration to **< 0.1 mm**.

![2D overview](images/overview_2d.png)

## Key dimensions (mm)

Datum = module-outline **center**, X → right, Y → up (front view as drawn).

| feature | size (W × H) | center offset | notes |
|---|---|---|---|
| Module outline | 167.12 × 208.88 (±0.5) | (0, 0) | thickness **2.60 max**; corners **R0.5**; **bottom-left non-square**: bottom edge raised to Y=−103.48 for X∈[−83.56,−65.8], ramps to full bottom (−104.44) by X=−62.7 |
| Bezel / polarizer | 151.608 × 201.01 | (−1.27, −0.86) | visible glass window |
| Active area | 147.456 × 196.608 | (−1.30, −0.89) | **not centered** |

### 4 mounting-lug holes — ⌀2.4 mm

| lug | X | Y | ear |
|---|---|---|---|
| TL | −85.71 | +99.55 | teardrop, points **left** (hole outside left edge) |
| TR | +78.07 | +106.59 | gusset, points **up** (hole outside top edge) |
| BL | −78.55 | −105.50 | teardrop, points **down** |
| BR | +78.48 | −107.34 | teardrop, points **down** |

> ⚠️ The lug layout is **asymmetric** (not a mirror set). Lugs protrude 3–5 mm past the
> 167.12 × 208.88 outline — your case must clear them.

**Z plane:** all 4 ears sit on the **front** (screen) face, Z 2.30–2.60 (thin 0.30 mm tabs).
The **rear FPC connector** is a keep-out boss on the **right long edge** (Y ≈ +26..+44),
protruding **~1.2 mm behind** the rear face (Z −1.20..0) — footprint approximate.

![3D model](images/model_3d.png)

![lug planes](images/lug_planes.png)

## Files

| file | description |
|---|---|
| `lcd_panel.step` | 3D solid: body + exact teardrop/gusset lug ears + ⌀2.4 holes + active-area pocket |
| `lcd_panel.stl` | mesh version of the above |
| `lcd_panel.scad` | parametric OpenSCAD source (all dims as variables) |
| `lcd_centerdatum.dxf` | 2D top view, origin = outline center, Y up |
| `lcd_cornerdatum.dxf` | 2D top view, origin = outline top-left, Y down (drawing convention) |
| `lcd_sideprofile.dxf` | side (Z) section: thickness 2.60, lug front plane, active recess |
| `lcd_lugs.csv` | hole coordinates, both datums |
| `lcd_reference.txt` | full numeric reference |
| `geometry.json` | **single source of truth** — clean-traced outline, ears, holes, bezel, Z, connector |
| `build_step.py` | builds the STEP/STL from `geometry.json` (needs cadquery) |
| `make_clean.py` | strips markings by colour + rasterizes the clean render |
| `trace2..6.py`, `geom.py` | trace pipeline (silhouette → edges → ears → holes → `geometry.json`) |
| `make_outputs.py` | regenerates the DXF/SCAD/CSV/reference/images |
| `verify.py` | overlays `geometry.json` back on the clean render |
| `bracket_top.step` / `.stl` | top photo-frame mounting bracket (3D print) |
| `bracket_bottom.step` / `.stl` | bottom photo-frame mounting bracket (3D print) |
| `bracket_top_thin.stl` / `bracket_bottom_thin.stl` | 5 mm-thick test-print variants (same XY/fit) |
| `build_brackets.py` | builds the two brackets from `geometry.json` + frame params (cadquery) |
| `brackets.scad` | parametric OpenSCAD source for the brackets |
| `verify_brackets.py` | assembly + side-section check images for the brackets |
| `LP097QX1-SPC1.pdf` | source datasheet (© LG Display) |

DXF layers: `OUTLINE`, `BEZEL`, `ACTIVE`, `HOLES`, `HOLE_CENTERS`, `EARS`, `CONNECTOR`.

### Lug ear shapes
Traced silhouettes (red) + ⌀2.4 holes (green) over the colour-cleaned drawing:

![ear TL](images/ear_TL.png) ![ear TR](images/ear_TR.png) ![ear BL](images/ear_BL.png) ![ear BR](images/ear_BR.png)

Lugs are **thin flat sheet-metal tabs (0.30 mm)** — not full-thickness — all on the
**front** (screen-side) face.

## Regenerate the 3D model

```bash
python3 -m venv cqenv
cqenv/bin/pip install cadquery cairosvg opencv-python-headless scipy
cqenv/bin/python build_step.py      # geometry.json -> lcd_panel.step + lcd_panel.stl
cqenv/bin/python make_outputs.py    # -> DXF / SCAD / CSV / reference / images
```

Re-trace from the PDF: `make_clean.py` → `trace2..6.py` → `geom.py` (writes `geometry.json`),
then `verify.py` overlays the result on the clean render. Or render the parametric source with
OpenSCAD: `openscad -o lcd_panel.stl lcd_panel.scad`.

## Photo-frame mounting brackets

Two **3D-printable back-press brackets** that hold the panel **centered in a photo frame** whose
inner cavity is **182 (W) × 242 (H) mm**. They sit on the panel's **short sides** (top + bottom),
friction-fit between the frame side walls. There is **no lip in front of the panel** — the screen
sits **flat on the frame glass**; the panel slides into a **2.75 mm slot** (2.60 LCD + 0.15) with the
rear shelf **behind** it, and the frame backing pushes the bracket so the shelf presses the LCD onto
the glass.

They **center the VIEW (active) area, not the outline.** The active area is offset from the
outline center by (−1.30, −0.89), so the panel is shifted (+1.30, +0.89) and the brackets are
sized to suit — the image lands in the frame center.

| | value |
|---|---|
| Frame inner cavity | 182 × 242 mm |
| Top-bracket gap (Y-depth) | **15.67 mm** |
| Bottom-bracket gap (Y-depth) | **17.45 mm** |
| Left / right gap (open, no bracket) | 8.74 / 6.14 mm |
| Bracket length (X, friction) | 181.8 mm (182 − 0.2) |
| Total thickness (Z) | 15.0 mm (screen on glass; rear shelf 2.75 → 15) |
| Panel slot (Z) | 2.75 mm = 2.60 LCD + 0.15 clearance; shelf sits **behind** the LCD |
| Rear shelf overhang onto border | 3.0 mm (clear of the active area) |

Check: 15.67 + 208.88 + 17.45 = 242.0 ✓. The lug ears are on the LCD **front** (recessed ~0.25 mm),
so each bracket's **ear-clearance pockets are cut on the front (glass) face** (top: TL+TR, bottom:
BL+BR). This **shape-keys** the part — it only seats with the ears in the front pockets (glass side),
which keeps the rear shelf behind the LCD, pressing it **from behind onto the glass**. The two
brackets are **different parts** (gaps and ear pockets differ).

**Thin test-print variants** (`bracket_top_thin.stl`, `bracket_bottom_thin.stl`, Z = 5 mm) have the
same XY/fit/slot/ear pockets — print one fast/cheap to check fit + orientation before the full 15 mm
part. Ear pockets are placed at each tab's **actual** position (the asymmetric layout: TL left-edge,
TR top-edge, BL/BR bottom-edge), with **1.5 mm clearance** all round — see the coverage check below.
If a panel is handed the other way, set `MIRROR_X=True` to flip the pockets in X.

Each bracket's total depth into the cavity is the end-gap **plus** the 3 mm shelf overhang behind the
LCD border (top 15.67+3.0, bottom 17.45+3.0), all behind the screen — the active area stays clear.

![bracket assembly](images/brackets_assembly.png)
![ear pocket coverage](images/brackets_ear_coverage.png)
![bracket section](images/brackets_section.png)

**Print:** PLA/PETG, lay flat — no supports. **Tune the fit** at the top of `build_brackets.py` /
`brackets.scad`: `FIT_CLR` (frame friction), `SEAT_CLR`/`POCKET_CLR` (panel play), `SLOT_CLR`
(panel slot Z — lower for tighter glass contact, raise if the LCD is tight), `EAR_Z` (front ear-pocket
depth), `LIP_Y` (rear-shelf grip), `MIRROR_X` (flip handedness). `VIEW_CENTER=False` centers the
outline instead (equal 16.56 mm gaps).

**Assemble:** lay the frame face-down on the glass, drop the panel in screen-first (it rests on the
glass). Push the top + bottom brackets into the end gaps **ear-pockets toward the glass** (the front
ears only fit that way) so each rear shelf sits behind a short edge, then close the frame back — its
clamping pushes the shelves and seats the LCD on the glass.

```bash
cqenv/bin/python build_brackets.py     # -> bracket_top/bottom .step + .stl
cqenv/bin/python verify_brackets.py    # -> images/brackets_assembly.png + brackets_section.png
# or parametric: openscad -o bracket_top.stl -D 'part="top"' brackets.scad
```

## Accuracy

- Outline = datasheet nominal (167.12 × 208.88); model self-calibrated to it.
- Hole centers: ≈ ±0.05 mm relative, ≈ ±0.1 mm vs the independent dimension-line calibration.
- Ear silhouettes are traced from the clean render (≈ ±0.1 mm, drawing-scale limit).
- Datasheet's own outline tolerance is ±0.5 mm.
- Lug ears are **thin flat sheet-metal tabs (0.30 mm)**, all on the **front** (screen) face
  (Z 2.30..2.60), confirmed against the physical part.

## Source

Datasheet: LG Display LP097QX1-SPC1, mirrored at
<http://mikesmods.com/mm-wp/wp-content/uploads/2013/04/LP097QX1-SPC1.pdf>
(FRONT VIEW, printed page 16/28). The PDF is © LG Display, included here for reference.

Extracted geometry and CAD files in this repo are provided as-is, no warranty — verify
against the datasheet before manufacturing.
