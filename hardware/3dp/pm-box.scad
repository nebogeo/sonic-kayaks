$fs=0.5; 
$fa=0.5; 

module sensor() {
    color("blue") 
    cube([47.7,36.7,11.7]);

    // plug
    color("black")
    translate([2.85,36.7-10-2.85,12])
    square([6,10]);

    // air out
    color("black")
    translate([4.45,37,11.7-2-8.75])
    rotate([90,0,0])
    square([9.8,2]);

    // air in
    color("black")
    translate([0,37,11.7-4.4-6.45])
    translate([47.7-11-4.45,0,0]) // ???
    rotate([90,0,0])
    square([11,4.4]);
}

module bent_pipe() {
    rotate([0,90,90]) {
        translate([5,0,0])
        rotate([90,0,0])
        difference() {
            cylinder(d=6,h=5);
            translate([0,0,-0.01])
            cylinder(d=4,h=5.02);
        }

        intersection() {
            rotate_extrude(angle=1,convexivity=10) {
                translate([5,0,0])
                difference() {
                    circle(d=6);
                    circle(d=4);
                }
            }
            translate([0,0,-5])
            cube([10,10,10]);
        }
    }
}

module nipple() {
    union() {
        cylinder(h = 10, r1 = 3, r2 = 5);
        translate([5,0,0])
        bent_pipe();
         //cylinder(h = 10, r = 3);
    }
}



module nipples() {
    // in nipple
    translate([69.2,40+10,5])
    rotate([90,30,0])
    nipple();

    // out nipple
    translate([41,40+10,5])
    rotate([90,180-30,0])
    nipple();
}


// translate([31.5,1.5,1.5]) sensor();

// internal space
//translate([0,0,0])
//color([1,1,1,0.5])
//cube([80,40,20]);

// 6-10mm internal pipe diameter

rotate([0,0,0]) {

color([1,0.5,0.2])
translate([0,0,3])
difference() {
    union() {
        // bottom wall
        translate([-3,-3,-3]) cube([86,46,3]);
        // back wall
        translate([0,-3,0]) cube([80,3,22]);
        // back wall
        translate([0,40,0]) cube([80,3,22]);
        // end wall
        translate([-3,-3,0]) cube([3,46,22]);
        // end wall
        translate([80,-3,0]) cube([3,46,22]);
        nipples();
        // bottom spacer
        translate([30,-3,-0.5]) cube([50,46,2]);
        // air separators
        translate([30,38.5,0])
        union() {
            cube([2,2,15]);
            translate([0,0,13])
            cube([50.5,2,2]);
            translate([20,0,0])
            cube([10,2,15]);
        }
        translate([33,43,5])
        rotate([-90,180,0])
        linear_extrude(height=1) {
            union() {
                scale([0.3,0.3,1]) {
                    text("Sonic Kayaks");
                    translate([0,-13,0])
                    text("Air pollution sensor");
                }
                translate([0,5,0])
                scale([0.75,0.75,1])
                import("foam-logo-seg.dxf");
            }
        }
    }

    // cut holes through box and nipples 
    translate([69.2,50.01,5])
    rotate([90,0,0])
    union () {
        cylinder(h=14, r1=1.5, r2=3);
        translate([41-69.2,0,0])
        cylinder(h=14, r1=1.5, r2=3);
    }
}


// lid
translate([-3,-5,3]) 
rotate([180,0,0])
union() {
    cube([86,46,3]);
    translate([3.5,3.5,-2])
    cube([79,39,2]);
}

}