## Motion Detect
- python motion_detect.py --buffer <num-points>
- Will track any green colored object and determine in, real time, determine whether the object is stationary, moving left, right, up, or down.
- Will draw a line representing the objects motion using the last P points defined by the buffer length. The larger the buffer the longer the line.
