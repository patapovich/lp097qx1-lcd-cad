// Photo-frame brackets for the LP097QX1-SPC1 LCD — parametric OpenSCAD twin of build_brackets.py
// Two L / back-press brackets on the panel's SHORT sides (top + bottom). Friction-fit in the frame.
// No front lip: the screen sits flat on the glass; a rear shelf 'preload' proud of the panel rear is
// pushed by the frame backing -> LCD onto the glass. Centers the VIEW (active) area in the frame.
// Frame coords: origin = frame center, X right, Y up, Z=0 glass -> +Z into cavity.
//   render: openscad -o bracket_top.stl -D part=\"top\" brackets.scad
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
preload = 0.15;       // rear shelf sits this proud of panel rear -> light forward press
lip_y   = 3.0;        // rear-shelf overhang onto the panel border
fit_clr = 0.2;        // friction: length = frame_w - fit_clr
seat_clr = 0.1;       // play, panel edge vs channel web
pocket_clr = 0.3;     // play, panel corner vs X end-stops
ear_clr = 1.5;        // margin around an ear pocket
ear_z   = 2.0;        // front depth cleared for ear tabs
gap     = 0.001;      // tiny boolean overlap

/* ---- ear spans [xmin,xmax,ymin,ymax] from geometry.json ---- */
ear_TL = [-87.787, -83.560,  94.874, 101.639];
ear_TR = [ 73.469,  80.151, 104.440, 108.676];
ear_BL = [-81.242, -76.469,-107.446,-103.480];
ear_BR = [ 73.128,  80.492,-109.360,-104.440];

shift_x = view_center ? -act_cx : 0;   // +1.30
shift_y = view_center ? -act_cy : 0;   // +0.89
hw = panel_w/2; hh = panel_h/2;
hfw = frame_w/2; hfh = frame_h/2;
lx = (frame_w - fit_clr)/2;
flange_z0 = panel_th - preload;   // rear shelf front face (2.45)

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
      boxc(stopL, stopR, llo, lhi, flange_z0, total_z); // rear shelf (preload press)
    }
    for (e = ears) {                                    // ear-clearance pockets
      tipY = (side>0 ? e[3] : e[2]) + shift_y;
      a = min(edgeY - side*2.0, tipY + side*ear_clr);
      c = max(edgeY - side*2.0, tipY + side*ear_clr);
      boxc(e[0]-ear_clr, e[1]+ear_clr, a, c, -gap, ear_z);
    }
  }
}

if (part == "top")    bracket(1);
if (part == "bottom") bracket(-1);
if (part == "both") { bracket(1); bracket(-1); }
