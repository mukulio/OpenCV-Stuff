## Motion Detect
- python motion_detect.py --buffer "buffer size"
- Will track any green colored object and determine in, real time, determine whether the object is stationary, moving left, right, up, or down.
- Will draw a line representing the objects motion using the last P points defined by the buffer length. The larger the buffer the longer the line.

## Polygon Detect
- python polygon_detect.py
- Will track mutiple green objects.
- Will draw a line between each object thus constructing the polygon (> 3 objects) represented by the objects.
- Detect the type of polygon created. (Need to implement)
