// LP097QX1-SPC1 LCD module envelope for case-mount design (EXACT traced lug ears).
// Datum: origin = module-outline CENTER (X right, Y up). Z=0 rear, +Z toward screen. Units mm.
// Sizes from datasheet table; lug ear outlines + holes measured from PDF vector drawing.
// Convert: openscad -o lcd_panel.stl lcd_panel.scad   (FreeCAD imports .scad -> STEP)
OUT_W=167.12; OUT_H=208.88; TH=2.60; HOLE_D=2.40;
ACT_W=147.456; ACT_H=196.608; ACT_CX=-1.305; ACT_CY=-0.885; ACT_D=0.20;
HOLES=[[-85.688,99.493],[78.111,106.583],[-78.533,-105.430],[78.486,-107.317]];
EARS=[
  [[-86.114,101.636],[-82.560,101.636],[-82.560,101.423],[-82.560,94.929],[-82.560,94.716],[-82.560,94.749],[-87.505,98.307],[-87.767,98.766],[-87.898,99.685],[-87.603,100.570],[-86.899,101.308]],
  [[77.864,108.786],[78.486,108.753],[79.108,108.523],[79.435,108.294],[80.008,107.621],[80.303,106.605],[80.303,103.440],[80.090,103.440],[73.544,103.440],[73.331,103.440],[73.331,103.440],[76.784,108.294],[77.341,108.654]],
  [[-81.204,-103.440],[-76.589,-103.440],[-76.377,-103.440],[-76.377,-105.555],[-76.508,-106.145],[-76.868,-106.768],[-77.309,-107.178],[-77.800,-107.440],[-78.422,-107.572],[-79.241,-107.473],[-79.830,-107.145],[-80.533,-106.309],[-81.417,-103.440]],
  [[73.184,-103.440],[80.450,-103.440],[80.663,-103.440],[80.663,-107.555],[80.434,-108.211],[79.795,-108.982],[79.108,-109.375],[78.323,-109.474],[77.472,-109.211],[73.037,-103.440],[72.971,-103.440]]
];
$fn=96;
difference() {
  union() {
    translate([-OUT_W/2,-OUT_H/2,0]) cube([OUT_W,OUT_H,TH]);   // module body
    for (p=EARS) linear_extrude(TH) polygon(p);                 // exact lug ears
  }
  for (h=HOLES) translate([h[0],h[1],-1]) cylinder(d=HOLE_D,h=TH+2);   // mounting holes
  translate([ACT_CX-ACT_W/2,ACT_CY-ACT_H/2,TH-ACT_D]) cube([ACT_W,ACT_H,ACT_D+1]); // active pocket ref
}
