# opentitan_9343

来源：[原PR](https://github.com/lowRISC/opentitan/pull/9343)；源数据第285行；分类 `RTL_INTERFACE`。

保留理由：输入保持时间造成重复采样，测试同时验“别提前做”和“之后真的完成”，质量较好。

本地证据：**原测试待本地实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

## Description
The ADC Controller (`adc_ctrl`) finite state machine does not enforce a strict four-phase handshake on the ADC data-valid signal during the one-shot channel sequencing flow. After channel 0 has been sampled, the controller can treat the same still-asserted valid level as progress toward channel 1 instead of waiting for the valid signal to return low before looking for the next sample.

## Expected Behavior
In one-shot mode, `adc_ctrl` must complete only after two distinct ADC samples have been accepted: first a channel 0 sample, then a channel 1 sample. One continuous high period of the ADC data-valid signal may acknowledge only one sample. After capturing channel 0, the controller must wait for the data-valid signal to deassert, and only a later reassertion may be used to capture channel 1 and finish the one-shot conversion.

## Actual Behavior
If the ADC data-valid signal stays high for multiple clock cycles after the channel 0 sample, the FSM can reuse that same assertion as the channel 1 handshake. This can cause the one-shot conversion to finish and return to power-down before a second distinct valid pulse arrives, while channel 1 reuses stale data from the first sample instead of waiting for a new channel 1 sample.

## Trigger Condition
The bug is triggered in one-shot mode when the first sample's data-valid indication remains asserted across the channel 0 to channel 1 handoff, rather than dropping low between the two samples.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #9312 明确四相握手要求检查 valid 撤回；PR 实际在多模式过渡处加等待。 |
| 触发过程 | channel0 valid 持续高→跨 channel 过渡→旧 FSM 当作 channel1 新采样→提前 done/错误数据。 |
| 测试覆盖 | 验持续 valid 阶段不能 channel1 write/done；低间隔不能 done；第二 distinct pulse 必须 done、两通道数据正确、回 powerdown。 |
| 尚存缺口 | one-shot 子场景覆盖充分；原 patch 还修改 LP/NP，应复用这两类正常采样回归。 |
| 环境真实性 | 直接实例化真实 adc_ctrl_fsm，驱动模块接口，无 force/替身。 |
| 跨周期价值 | 高，跨通道与四相握手。 |
| 题面提示 | 高：题面已说明必须等 valid 撤回，接近修复方向。 |
| 原审查后续建议 | 双版本运行，改变 valid 保持长度，并跑 LP/NP 对照；题面提示程度统一标记。 |

## 原字段证据

`body` 字段内第2–2行：

```text
- Ensure valid is dropped before moving to ensure we don't accidentally
```

`tb_script` 字段内第107–107行：

```text
$fatal(1, "channel 1 sampled while adc_d_val_i stayed high");
```

`tb_script` 字段内第136–136行：

```text
$fatal(1, "channel 1 captured the wrong sample value");
```

`tb_script` 字段内第143–143行：

```text
$fatal(1, "FSM did not return to power-down after oneshot completion");
```
