# -*- coding: utf-8 -*-
"""向量交给 FAISS 之前要过的两道手续：float32，以及每一行长度变成 1。

FAISS 的 IndexFlatIP 算的是点积。每一行先变成单位长度，点积才等于余弦。
忘了归一化时，字数多的那段会只因为数字大而排到前面。
"""

import numpy as np


def as_float32_matrix(vectors) -> np.ndarray:
    """收成连续的 float32 二维表。一行向量会补成只有一行的表。

    numpy 用 Python 小数做出来的默认类型是 float64。
    索引内部按 float32 存。这里先转好，不把结果押在某一版 FAISS 会不会好心帮你转。
    """
    array = np.asarray(vectors, dtype=np.float32)
    if array.ndim == 1:
        array = array.reshape(1, -1)
    if array.ndim != 2:
        raise ValueError("向量要是一行，或很多行组成的表")
    if array.shape[1] < 1:
        raise ValueError("向量至少要有一格")
    return np.ascontiguousarray(array, dtype=np.float32)


def l2_normalize(vectors) -> np.ndarray:
    """每一行除以自己的长度。全零的行保持全零，避免除以 0。"""
    matrix = as_float32_matrix(vectors)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    safe = np.maximum(norms, np.float32(1e-12))
    unit = matrix / safe
    # 长度本来是 0 的行，上面为了不除以 0 用了一个很小的数。结果仍应是全零。
    for row_index, norm in enumerate(norms.reshape(-1)):
        if float(norm) == 0.0:
            unit[row_index] = np.float32(0.0)
    return np.ascontiguousarray(unit, dtype=np.float32)


def cosine(left, right) -> float:
    """两行向量的余弦。没有方向（全零）时记 0，不让除法把程序摔碎。"""
    left_row = as_float32_matrix(left).reshape(-1)
    right_row = as_float32_matrix(right).reshape(-1)
    if left_row.shape != right_row.shape:
        raise ValueError("两条向量的格数要一样，才能算余弦")
    left_norm = float(np.linalg.norm(left_row))
    right_norm = float(np.linalg.norm(right_row))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return float(np.dot(left_row, right_row) / (left_norm * right_norm))
