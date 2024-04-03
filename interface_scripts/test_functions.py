import bpy

def test_loop(layout_function:bpy.types.UILayout, columns:int=5):
    col = layout_function.column(align=True).box()
    col.label(text="Test Loop")
    for i in range(columns):
        col.label(text=f"Column {i}")