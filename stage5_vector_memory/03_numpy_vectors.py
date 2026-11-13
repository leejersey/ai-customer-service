# -*- coding: utf-8 -*-
"""阶段 5 · 示例 3：向量要用到的那一点 numpy。

不下载模型，也不建索引。下一课才把这种表交给 FAISS。

    python stage5_vector_memory/03_numpy_vectors.py

导读：stage5_vector_memory/docs/03_numpy.md
"""

import numpy as np


def main() -> None:
    print("Python 列表可以装小数，但 FAISS 要的是一块类型统一的连续数字，也就是 numpy 数组。")
    row = np.array([3.0, 4.0])
    print("np.array([3.0, 4.0])")
    print(f"  形状 shape = {row.shape}    一行、两格。形状是元组。")
    print(f"  类型 dtype = {row.dtype}    从 Python 小数来的默认是 float64。")
    narrow = row.astype(np.float32)
    print(f"  astype(float32) 之后 dtype = {narrow.dtype}")
    print()

    wide = np.array([1.0, 2.0])
    print("如果有人把 float64 的内存直接当成 float32 来读，数字会乱：")
    print("  原来：", wide, wide.dtype)
    print("  按 float32 去看同一块内存：", wide.view(np.float32))
    print("  astype 才是真的换成窄格子：", wide.astype(np.float32))
    print("写入索引之前用 astype 或 np.asarray(..., dtype=np.float32)，不要靠 view。")
    print()

    table = np.array([[3.0, 4.0], [0.0, 0.0], [1.0, 0.0]], dtype=np.float32)
    print(f"三行向量的形状是 {table.shape}。axis=1 表示按每一行算长度。")
    norms = np.linalg.norm(table, axis=1, keepdims=True)
    print("  每行长度：", norms.reshape(-1))
    print("  keepdims=True 让长度仍是一列，才能和原来的表逐行相除。")
    safe = np.maximum(norms, np.float32(1e-12))
    unit = table / safe
    for row_index, norm in enumerate(norms.reshape(-1)):
        if float(norm) == 0.0:
            unit[row_index] = np.float32(0.0)
    print("  归一化之后：")
    print(unit)
    print(f"  第一行长度变成 {float(np.linalg.norm(unit[0])):.4f}，全零那行仍然是 0。")
    print()
    print("3 和 4 的长度是 5。除完是 0.6 和 0.8。方向没变，长度变成 1。")
    print("IndexFlatIP 的点积在单位向量上等于余弦。忘了这一步，长文本会占便宜。")
    print()
    print("numpy 这一课看完了")


if __name__ == "__main__":
    main()
