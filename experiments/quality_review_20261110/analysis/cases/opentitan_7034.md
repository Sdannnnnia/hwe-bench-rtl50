# opentitan_7034

来源：[原PR](https://github.com/lowRISC/opentitan/pull/7034)；源数据第323行；分类 `RTL_LOGIC`。

保留理由：低功耗进入失败后残留状态，原目标与测试一致，保留。

本地证据：**原测试待本地实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

## Description
The affected logic is the Power Manager (`pwrmgr`) fast clock-domain finite state machine that handles software-requested entry into low power and drives the `low_power_o` status signal to always-on logic.

## Trigger Conditions
A low-power entry attempt starts when software sets `CONTROL.LOW_POWER_HINT` and the CPU sleep indication from wait-for-interrupt (WFI) is sampled. The failure occurs when that entry sequence reaches `FastPwrStateNvmIdleChk` while the Flash Controller is still busy, so the transition is aborted instead of completing low-power entry.

## Expected Behavior
If the low-power entry attempt is aborted in `FastPwrStateNvmIdleChk`, the system must resume normal active execution with `low_power_o` deasserted. `low_power_o` must only remain asserted for a low-power transition that actually completes.

## Actual Behavior
`low_power_o` is asserted during the attempted entry, but when the Flash Controller busy condition aborts the transition, the system resumes execution without clearing `low_power_o`. The signal therefore remains high even though the device never entered low power.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #6819 明确 abort/fallthrough 未清 low_power_o；patch 还改 reset 条件上报，当前目标限定 Flash busy abort。 |
| 触发过程 | 软件 hint+CPU sleep→进入低功耗 low_power置位→Flash busy→abort→回活跃应清 low_power。 |
| 测试覆盖 | 先要求看到 low_power 置位，再等20拍检查清零；避免直接常量0过关。 |
| 尚存缺口 | 测试中没有在 abort 后显式 wait fast FSM active，主要验 low_power；恒定固定延迟清状态仍可能过，需真实成功入睡对照。 |
| 环境真实性 | 原 pwrmgr UVM，通过 CPU/Flash/clock status 接口刺激；未直接设 FSM。 |
| 跨周期价值 | 高，失败路径收尾与外部 busy。 |
| 题面提示 | 高：题面点名 FastPwrStateNvmIdleChk 和待清输出。 |
| 原审查后续建议 | 双版本运行，增加复用成功低功耗/CPU fallthrough、abort 后 active 验证。 |

## 原字段证据

`tb_script` 字段内第46–46行：

```text
cfg.pwrmgr_vif.update_flash_idle(1'b0);
```

`tb_script` 字段内第59–59行：

```text
`uvm_fatal(`gfn, "low_power_o never asserted during aborted low-power entry")
```

`tb_script` 字段内第64–64行：

```text
`uvm_fatal(`gfn, $sformatf("low_power_o stuck high after aborted low-power entry: %0b",
```

`problem_statement` 字段内第5–5行：

```text
A low-power entry attempt starts when software sets `CONTROL.LOW_POWER_HINT` and the CPU sleep indication from wait-for-interrupt (WFI) is sampled. The failure occurs when that entry sequence reaches `FastPwrStateNvmIdle
```
