import numpy as np


def find_index_quantile(xs, q):
    if q == 0:
        return 0
    if q == 1:
        return -1
    return np.searchsorted(xs, v=np.quantile(xs, q), side="left")


def find_index(xs, n_segments):
    qs = np.linspace(0, 1, n_segments + 1)
    return [find_index_quantile(xs, q) for q in qs]


xs = [1, 2, 3, 4, 5]
find_index(xs, 2)
