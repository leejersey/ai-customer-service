# 阶段 1：意图识别

在阶段 0 的客服会说话之后，先判断顾客想干什么，再决定用哪一段回复。这一阶段不查数据库。

零基础的读法在 [docs/README.md](docs/README.md)。语法小课仍在 `stage0_basics/python_basics/`，新课从第 24 课开始。

没有密钥时可以运行：

```bash
python stage1_intent/01_rule_classifier.py
python stage1_intent/02_llm_classifier.py
python stage1_intent/03_router.py
python stage1_intent/test_rules.py
python stage1_intent/04_evaluate.py
python stage1_intent/05_cli_with_intent.py
```

`02` 会演示坏 JSON 的兜底，然后说明跳过模型。`05` 会改用规则和写死回复。配好阶段 0 的 `.env` 之后，`02`、`04` 和 `05` 才会调用模型。
