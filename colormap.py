"""
Start creating on Tue. Fri. 3, 2020
author: koharite

Function of convert value to heatmap color value
"""

import numpy as np

def sigmoid(x, gain=1, offset_x=0):
    return ((np.tanh(((x + offset_x) * gain) / 2) + 1) / 2)


def colorBarRGB(x, offset_x, offset_green, gain):
    x = (x * 2) - 1
    red = sigmoid(x, gain, -1 * offset_x)
    blue = 1 - sigmoid(x, gain, offset_x)
    green = sigmoid(x, gain, offset_green) + (1 - sigmoid(x, gain, -1 * offset_green))
    green = green - 1.0
    return (red * 255, green * 255, blue * 255)