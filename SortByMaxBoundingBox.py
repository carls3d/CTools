import bpy
from math import sqrt

def main():
    C = bpy.context
    D = bpy.data
    
    include_hidden = False
    
    objects = C.collection.objects
    if not include_hidden:
        objects = [ob for ob in objects if not ob.hide_get()]
    
    amount_sides = sqrt(len(objects)).__ceil__()
    max_bounding_box = max([max(ob.dimensions.x, ob.dimensions.y) for ob in objects]) * 1.1
    
    col:int = -1
    for i, ob in enumerate(objects):
        # Modulo to add new row at end of each column
        row = i % amount_sides
        if row == 0:
            col += 1
        ob.location.x = max_bounding_box * (row % amount_sides)
        ob.location.y = max_bounding_box * (col % amount_sides)
    
    
    
if __name__ == "__main__":
    main()