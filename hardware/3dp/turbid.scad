$fn = 100;

module vent() {
    rotate([0,90,0])
        difference() {
        union() {
            cylinder(h=60,d=33);
            cylinder(h=1,d=34+12);
            translate([0,0,5])
            difference() {
            rotate_extrude(angle=360) {
                translate([19,-5,0])
                circle(4);
            }
            cube([60,60,10],true);
            
        }
        }
        translate([0,0,-0.1])
        difference() {        
            cylinder(h=60.2,d=30);
            for (i=[0:7]) {
                translate([i*5-13.5,-25,-0.1])
                cube([1.5,50,60.2]);
            }    
        }
    }
}


rotate([90,0,0])
{
//translate([0,0,-60]) vent();
//translate([0,0,0]) vent();


difference() {
rotate([0,90,0])
difference() {
    union() {
        cylinder(h=250,d=40); // main tube
        cylinder(h=5,d=46); // end ring
        translate([0,0,245])
        cylinder(h=5,d=46); // end ring
        translate([0,0,(250/2.0)-(75/2)])
        cylinder(h=75,d=46); // middle section

        // fin
        rotate([90,-90,0])
        translate([-5,-309,-1.5])
        linear_extrude(height=3)
        import("fin-export.dxf");
                
    }
    translate([0,0,-0.1])
    cylinder(h=250.2,d=34); // hole     
 
    // logo and text
    translate([55,-1,190])
    rotate([90,-90,0])    
    linear_extrude(height=1) {
        union() {
            scale([0.3,0.3,1]) {
                text("Sonic Kayaks");
                translate([0,-13,0])
                text("Water turbidity sensor");
            }
            translate([0,5,0])
            scale([0.75,0.75,1])
            import("foam-logo-seg.dxf");
        }
    }
}

   // cut away
   union() {
        // sensor locators
        rotate([45,0,0])
        translate([250/2.0,0,25])
        cube([22,12,14],true);
        rotate([-45,0,0])
        translate([250/2.0,0,25])
        cube([22,12,14],true);

        // strap holes
        translate([250/2,0,-25])
        cube([27,10,4],true);
        translate([250/2+(50+25),0,-22])
        cube([27,10,4],true);
        translate([250/2-(50+25),0,-22])
        cube([27,10,4],true);
   }
}

}

//color("red")
//translate([87.5,0,-28.5])
//cube([50,10,10],true);