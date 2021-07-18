rotate([0, 0, 180])
translate([10, -30, -10])
import("/Volumes/OrpheusB/brian/Documents/BAM/Projects/2021/MatOPlat/ObjectClasses/STLs/Gripper_text.stl");
rotate([0, 0, 180])
translate([-10, -30, -10])
mirror([1, 0, 0])
import("/Volumes/OrpheusB/brian/Documents/BAM/Projects/2021/MatOPlat/ObjectClasses/STLs/Gripper_text.stl");
sphere(r=10);
// translate([0, 66, -11]) // this is where the grab center is. 
// sphere(r=10);