import math
import numpy as np

def rotate(vec, angle):
    cos = math.cos(angle)
    sin = math.sin(angle)
    rotated = np.zeros(2)
    rotated[0] = vec[0] * cos - vec[1] * sin
    rotated[1] = vec[0] * sin + vec[1] * cos
    return rotated