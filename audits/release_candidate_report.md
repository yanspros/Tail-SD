# Tail-SD 开源候选仓库审计报告（历史归档）

> **说明**：本文件为 2026-09-15 初始候选仓库生成时的工程审计记录（归档保留）。当前正式论文结果已于 2026-09-18 冻结，涵盖 E13 新文本确认（+4.70 pp [3.20, 6.22]）、E14 位置对照、E16 预算敏感性及十档长度结果，详见 [`reproduction/PAPER_RESULTS.md`](../reproduction/PAPER_RESULTS.md) 与 [`audits/paper_result_consistency.json`](paper_result_consistency.json)。

## 问题 / 目标、方法、最终结果

本轮目标是在不运行、修改任何科研实验的前提下，从现有正式代码与证据中提取一个可人工审查的 Tail-SD 开源候选仓库。方法是先追溯正式 target、mask、训练与评分实现，再将核心合同抽成不依赖内部 Gate、集群路径和私有资产的小型模块，最后执行隔离单元测试、隐私扫描、许可证审计和论文数字一致性检查。最终结果为：候选仓库通过工程 Gate `OPEN_SOURCE_TAILSD_V1_RELEASE_CANDIDATE_READY`。

## 一句话结论

核心 Tail-SD、Random-PR、Full-SD、target selection、masked CE、completion metrics 和 source-level bootstrap 已整理成干净、可测试的小型代码树；17 项 unit test 全部通过，模型 integration test 因不分发模型资产而明确跳过，隐私阻断项为 0。

## 为什么做

科研工程包含正式实验、历史失败、集群调度、邮件通知和受限模型/数据资产，不能整体公开。本次整理把“论文方法代码”和“内部实验基础设施”分开，并把论文数字绑定到已冻结 evidence package 的 SHA，避免公开仓库重新引入过期或不可复现的统计值。

## 做了什么

- 抽取 target construction、Tail-SD/Random-PR/Full-SD masks、masked CE/LoRA、inference manifest、SC/HC/WER/coverage/non-tail metrics 与 paired bootstrap。
- 将服务器路径、GPU、通知和私有 checkpoint 依赖改为 CLI、配置、环境变量或外部 adapter。
- 提供 CV3/CV2 分离配置、placeholder manifest、用户文档及小型 reproduction snapshot。
- 对正式 CV3 123 条 bank 做只读等价核验：Tail-SD 与 Random-PR M0 均为 123/123 核心位置与预算一致。
- 在隔离 PATH 下运行 17 项 unit test、5 个 CLI help、8 个 YAML parse 和三种 toy manifest 构造。
- 扫描隐私、secret、大型资产和废弃 Full-SD CI。

## 结果

- Unit tests：17/17 PASS。
- Integration tests：0 PASS、0 FAIL、1 SKIPPED；原因是用户尚未提供可公开配置的 CosyVoice checkout/checkpoint/prompt assets。
- Tail-SD 正式 mask 等价：123/123。
- Random-PR M0 正式 mask 等价：123/123。
- 隐私/secret blocking findings：0。
- 大型或受限资产：0。
- 论文数字：CV3 primary、Random-PR repeats 和 CV2 transfer 与冻结 evidence authority 一致；Tail-SD−Full-SD 为 +0.40 pp、95% CI [-1.90,+2.70]，不可复现的正下界版本未进入 release。

## 已解决

公开代码不再依赖 `current_state.yaml`、历史 Gate、邮件通知或私有绝对路径；CV3 与 CV2 sampling/cap 配置被明确分开；Random-PR 的 per-record matching、one-draw/no-redraw 和 full-history 合同具有直接测试。

## 未解决

项目原始代码没有可确认的开源许可证 authority；`CITATION.cff` 的作者、最终论文标题与仓库地址仍为 TODO；端到端模型训练/推理需要用户提供并审核官方 CosyVoice adapter。

## 修改情况

只创建并修改 `exports/tailsd_open_source_v1/`。没有修改科研实验、历史 Gate、checkpoint 或 frozen evidence package，也没有运行训练、生成、ASR 或科学评分。

## 主要产物

- 核心包：`tailsd/`
- 命令入口：`scripts/`
- 正式代码映射：`audits/open_source_code_inventory.json`
- 隐私审计：`audits/public_release_privacy_scan.json`
- 依赖/许可证：`audits/dependency_audit.json`、`audits/third_party_license_audit.json`
- 论文数字：`reproduction/paper_results.json`、`reproduction/PAPER_RESULTS.md`
- Release Gate：`audits/formal_gate.json`

## 下一步

1. 项目所有者确认许可证与版权归属。
2. 填写 `CITATION.cff`，并人工复核 README 与第三方 attribution。
3. 在不纳入私有资产的独立环境中接入并审查官方 CosyVoice adapter 后，再决定是否公开 GitHub。
