import numpy as np


# Assembly X-coordinate
def xi_coordinate(spans, stretch):
    numS = 1000
    Xt = []
    for i in range(spans):
        Xt.append(np.linspace(0, stretch[i].L, numS))  # 1000 points in each stretch
    return numS, Xt


# X-coordinate
def X_coordinate(spans, stretch, Xt):
    X = []
    temp = 0
    for i in range(spans):
        if i > 0:
            temp += stretch[i - 1].L
        Xprov = Xt[i] + temp
        Xlist = Xprov.tolist()
        X += Xlist
    return X
