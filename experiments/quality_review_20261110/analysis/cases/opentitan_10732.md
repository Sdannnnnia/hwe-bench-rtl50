# opentitan_10732

来源：[原PR](https://github.com/lowRISC/opentitan/pull/10732)；源数据第266行；分类 `RTL_TIMING_SYNC`。

保留理由：时钟消失时 POR 仍要传播，具备明确硬件契约和恢复检查。

本地证据：**原测试待本地实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

## Description
OpenTitan's Reset Manager (rstmgr) generates power-on reset (POR) signals and downstream reset sources for the always-on domain and for non-always-on power domains. There is a bug in the non-always-on reset path: when a non-always-on `por_ni` input drops unexpectedly, the downstream resets for that domain are still effectively dependent on synchronous propagation through the domain's fast clocks.

## Affected Function
The affected logic is rstmgr's reset propagation for a non-always-on power domain, specifically the path from a non-always-on POR event to that domain's POR-generated reset, life cycle reset source, and system reset source.

## Trigger Condition
The bug is triggered when a non-always-on POR asserts unexpectedly, such as during a power instability rather than an intentional low-power transition, while the fast clocks for that domain are stopped or disappear at the same time.

## Expected Behavior
For a non-always-on power domain, asserting `por_ni` must deterministically place that domain in reset even when its fast clocks are unavailable. While `por_ni` remains asserted, rstmgr must keep that domain's POR-generated reset, life cycle reset source, and system reset source asserted. After `por_ni` is released and normal clocking resumes, those reset sources may return inactive.

## Actual Behavior
In the failing case, the non-always-on POR event occurs, but the downstream life cycle reset source and system reset source for that domain do not assert if the fast clocks are absent. As a result, an unexpected POR drop does not fully reset logic on that non-always-on power rail.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #10682 描述非 AON 电源异常伴随 fast clock 停止；PR 明确异步 reset 路径必须生效。 |
| 触发过程 | 系统 active→停所有 fast clocks→非 AON POR 拉低→AON 下游 reset 应低→POR 松开/复钟→reset 释放。 |
| 测试覆盖 | 检查操作前正常、停钟期间 POR/lc/sys reset 拉低，恢复后 reset 拉高，带超时。 |
| 尚存缺口 | pwrmgr/rstmgr intersignal SVA 被关闭；需要解释关闭哪些约束、与“非预期掉电”目标的关系；未做全系统功能恢复。 |
| 环境真实性 | 原 rstmgr UVM，多时钟接口停启与 POR 引脚驱动；没有强行设置 reset 内部寄存器。 |
| 跨周期价值 | 高，多时钟缺失和异步 reset 时序。 |
| 题面提示 | 中高：题面已指出同步传播是原因。 |
| 原审查后续建议 | 跑双版本、审关闭 SVA 列表，复用正常 POR/低功耗 reset 测试。 |

## 原字段证据

`tb_script` 字段内第58–58行：

```text
cfg.pwrmgr_rstmgr_sva_vif.disable_sva = 1'b1;
```

`tb_script` 字段内第37–37行：

```text
task stop_fast_clocks();
```

`tb_script` 字段内第75–75行：

```text
"Expected lc source reset to assert without clk_i")
```

`body` 字段内第7–7行：

```text
even if clocks are killed, the internal nodes are all reset as well.
```
