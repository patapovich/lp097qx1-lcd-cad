// Photo-frame brackets for the LP097QX1-SPC1 LCD — parametric OpenSCAD twin of build_brackets.py
// Two L / back-press brackets on the panel's SHORT sides (top + bottom). Friction-fit in the frame.
// No front lip: the screen sits flat on the glass; the panel slot = panel_th + slot_clr and the rear
// shelf sits BEHIND the panel, so the frame backing pushes the bracket -> LCD onto the glass (push
// from behind). Centers the VIEW (active) area. Lug ears are on the LCD FRONT (recessed ~0.25mm) ->
// shallow ear pockets on the front face, which shape-keys the part (only seats ears-toward-glass).
// Frame coords: origin = frame center, X right, Y up, Z=0 glass -> +Z into cavity.
//   render: openscad -o bracket_top.stl -D part=\"top\" brackets.scad
//   thin test print: add -D total_z=5
part = "both";        // "both" | "top" | "bottom"

/* ---- frame + panel ---- */
frame_w = 182;        // photo-frame inner width
frame_h = 242;        // photo-frame inner height
panel_w = 167.12;     // LCD outline
panel_h = 208.88;
panel_th = 2.60;      // LCD thickness
act_cx  = -1.30;      // active-area offset on the outline
act_cy  = -0.89;
view_center = true;   // center active area (true) or outline (false)

/* ---- bracket / fit ---- */
total_z = 15.0;       // bracket thickness (glass -> frame backing) = cavity depth
slot_clr = 0.15;      // Z clearance: panel slot = panel_th + slot_clr (shelf sits BEHIND the panel)
lip_y   = 3.0;        // rear-shelf overhang onto the panel border
fit_clr = 0.2;        // friction: length = frame_w - fit_clr
seat_clr = 0.1;       // play, panel edge vs channel web
pocket_clr = 0.3;     // play, panel corner vs X end-stops
ear_clr = 1.5;        // margin around an ear pocket
ear_on_back = false;  // lugs on the LCD FRONT (recessed ~0.25mm) -> clear them on the front face
ear_z   = 0.7;        // shallow front pocket depth (clears the ~0.25..0.55 recessed front ear tabs)
mirror_x = true;      // datasheet front view is mirrored vs the physical panel -> flip X to match real part
label = true;         // deboss "BACK" on the flat rear face = orientation key
label_text = "BACK";  // this face -> frame backing; opposite (slot) face -> glass
label_h = 6.0;        // text height
label_depth = 0.6;    // deboss depth
gap     = 0.001;      // tiny boolean overlap

/* ---- ear spans [xmin,xmax,ymin,ymax] from geometry.json ---- */
ear_TL = [-87.787, -83.560,  94.874, 101.639];
ear_TR = [ 73.469,  80.151, 104.440, 108.676];
ear_BL = [-81.242, -76.469,-107.446,-103.480];
ear_BR = [ 73.128,  80.492,-109.360,-104.440];

shift_x = (view_center ? -act_cx : 0) * (mirror_x ? -1 : 1);   // +1.30 (negated if mirror_x)
shift_y = view_center ? -act_cy : 0;   // +0.89
hw = panel_w/2; hh = panel_h/2;
hfw = frame_w/2; hfh = frame_h/2;
lx = (frame_w - fit_clr)/2;
flange_z0 = panel_th + slot_clr;   // rear shelf front face (2.75) - behind the panel

module boxc(x0,x1,y0,y1,z0,z1) translate([x0,y0,z0]) cube([x1-x0,y1-y0,z1-z0]);

module bracket(side) {                 // side = +1 top, -1 bottom
  edgeY     = side*(hh + side*shift_y);
  webInnerY = edgeY + side*seat_clr;
  lipInnerY = edgeY - side*lip_y;
  wallY     = side*hfh;
  stopL = shift_x - hw - pocket_clr;
  stopR = shift_x + hw + pocket_clr;
  wlo = min(webInnerY,wallY); whi = max(webInnerY,wallY);
  llo = min(lipInnerY,webInnerY); lhi = max(lipInnerY,webInnerY);
  ears = side>0 ? [ear_TL,ear_TR] : [ear_BL,ear_BR];
  difference() {
    union() {
      boxc(-lx, lx, wlo, whi, 0, total_z);              // web / gap filler (front on glass)
      boxc(-lx, stopL, llo, lhi, 0, total_z);           // end stop L
      boxc(stopR, lx, llo, lhi, 0, total_z);            // end stop R
      boxc(stopL, stopR, llo, lhi, flange_z0, total_z); // rear shelf (behind the panel)
    }
    for (e = ears) {                                    // ear pockets at the tab's actual frame bbox
      ex0 = (mirror_x ? -e[1] : e[0]) + shift_x;        // ear bbox in frame X (panel shift, mirror-aware)
      ex1 = (mirror_x ? -e[0] : e[1]) + shift_x;
      ay0 = e[2] + shift_y; ay1 = e[3] + shift_y;       // ear bbox in frame Y
      z0 = ear_on_back ? (panel_th-0.6) : -gap;
      z1 = ear_on_back ? total_z+gap : ear_z;
      boxc(ex0-ear_clr, ex1+ear_clr, ay0-ear_clr, ay1+ear_clr, z0, z1);
    }
    if (label)                                          // deboss "BACK" into the flat rear face
      translate([0, (webInnerY+wallY)/2, total_z-label_depth])
        linear_extrude(label_depth+gap)
          text(label_text, size=label_h, halign="center", valign="center");
  }
}

if (part == "top")    bracket(1);
if (part == "bottom") bracket(-1);
if (part == "both") { bracket(1); bracket(-1); }
