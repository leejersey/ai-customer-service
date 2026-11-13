# 阶段 6：合规审核（输入与输出的安全护栏）

阶段 5 能检索、能记住偏好，也能把退款写成工单。这些能力会把一句话说给顾客，或写进数据库。说错、记错、乱答应，比「没答上来」更难收回。这一阶段在三处加检查：进模型之前、调用会写库的工具之前、回复离开之前。每一轮追加一行审计日志，日志里的号码是打过码的。

零基础的读法在 [docs/README.md](docs/README.md)。新语法在 [基础课](../00_python_basics/README.md) 第 58 到 62 课，导读第一次用到时会叫停。不在本目录里再讲一遍。

## 本阶段需要的基础课

- 👉 不懂 findall 和 sub？先看 [基础课 · 正则替换](../00_python_basics/58_regex_sub.md)
- 👉 不懂 any / all？先看 [基础课 · any 和 all](../00_python_basics/59_any_all.md)
- 👉 不懂枚举？先看 [基础课 · 枚举](../00_python_basics/60_enum.md)
- 👉 不懂追加和 JSON Lines？先看 [基础课 · JSON Lines](../00_python_basics/61_json_lines.md)
- 👉 不懂把函数交进去？先看 [基础课 · 函数作为参数](../00_python_basics/62_pass_function.md)

导读里每次用到时还会再写一次。完整清单在 [导读目录](docs/README.md)。

`rules.json` 是词表。改短语不用改 Python，保存后重新运行对应示例。不要把单个「垃圾」或单个「忽略」写进去，误报会很多。示例 2 和示例 4 会演示过宽的词会伤到什么句子。

没有密钥时可以运行：

```bash
python stage6_compliance/01_why_compliance.py
python stage6_compliance/02_sensitive_words.py
python stage6_compliance/03_mask_pii.py
python stage6_compliance/04_prompt_injection.py
python stage6_compliance/05_llm_judge.py
python stage6_compliance/06_output_policy.py
python stage6_compliance/07_risk_and_audit.py
USE_FAKE_EMBEDDING=1 python stage6_compliance/08_cli_with_compliance.py
python stage6_compliance/09_offline_demo.py
```

示例 1 到 4、示例 6、示例 7 不联网。示例 5 没有密钥时只演示解析，并说明跳过模型。示例 8 没有密钥时，政策题复述资料，裁判不调用模型；它会用到阶段 5，所以没装嵌入模型时加上 `USE_FAKE_EMBEDDING=1`。示例 9 在进程里使用假裁判，不读密钥，不联网，最后一行是「离线演示通过」。

示例 7 和示例 9 会在 `stage6_compliance/data/` 写下 `audit_demo.jsonl` 和 `offline_audit.jsonl`。示例 8 写下 `cli_audit.jsonl`。这些文件已在 `.gitignore` 里，不要提交。练习用的手机号、证件号和卡号都是假的，日志里也不留明文。

退款仍然只会写成工单，不会打款。句子里如果要求直接打款，工具不会被调用。

## 文件一览

| 文件 | 你要它做什么 | 教程 |
| --- | --- | --- |
| `rules.json` | 辱骂、竞品诋毁、绝对化承诺、提示注入、政策用语 | [第 2 课](docs/02_rules.md) |
| `rules.py` | 读词表，按输入或输出挑短语 | [第 2 课](docs/02_rules.md) |
| `01_why_compliance.py` | 三个座位各走一遍，还不读词表 | [第 1 课](docs/01_why.md) |
| `pii.py` | 手机号、身份证、银行卡、邮箱、口令打码 | [第 3 课](docs/03_pii.md) |
| `03_mask_pii.py` | 看见分组、误伤订单号、漏掉带空格的号码 | [第 3 课](docs/03_pii.md) |
| `04_prompt_injection.py` | 常见注入短语，以及它挡不住的改写 | [第 4 课](docs/04_injection.md) |
| `judge.py` | 裁判只交 JSON；解析失败默认拒绝 | [第 5 课](docs/05_judge.md) |
| `05_llm_judge.py` | 坏文本和可选的真实调用 | [第 5 课](docs/05_judge.md) |
| `policy.py` | 赔钱、索要密码、系统提示、别人的号码 | [第 6 课](docs/06_policy.md) |
| `06_output_policy.py` | 改写、转人工、拦截各看一句 | [第 6 课](docs/06_policy.md) |
| `result.py` | `ComplianceResult`、等级和动作谁更严重 | [第 7 课](docs/07_risk.md) |
| `audit.py` | 追加 JSON Lines，写入前再打一次码 | [第 7 课](docs/07_risk.md) |
| `07_risk_and_audit.py` | 等级决策，并确认日志里没有明文号码 | [第 7 课](docs/07_risk.md) |
| `pipeline.py` | 输入、工具前、生成、输出、记日志 | [第 8 课](docs/08_cli.md) |
| `08_cli_with_compliance.py` | 套在阶段 5 客服外面的命令行 | [第 8 课](docs/08_cli.md) |
| `09_offline_demo.py` | 假裁判，覆盖每一条规则 | [第 9 课](docs/09_offline.md) |

阶段关系在 [docs/stage_summary.md](docs/stage_summary.md)。客服用词在 [docs/glossary.md](docs/glossary.md)。
