# opentitan_11904

来源：[原PR](https://github.com/lowRISC/opentitan/pull/11904)；源数据第249行；分类 `RTL_TIMING_SYNC`。

保留理由：关钟期间两次事件互相抵消，测试保留了真实 CDC 核心，保留。

本地证据：**原测试待本地实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

## Description
The ADC Controller has an interrupt clock-domain crossing bug in the path that carries filter-match events from the always-on clock domain into the gated main clock domain.

## Expected Behavior
If an enabled filter-match event occurs while the main ADC interrupt/register clock is gated off, that event must remain pending until the main clock resumes. Repeated pulses from the same filter-match source during the gated interval must not cancel or clear the pending interrupt. Once the main clock is running again, the corresponding ADC interrupt-status bit and the top-level interrupt pending state must both be asserted.

## Actual Behavior
When the same filter-match source pulses multiple times while the main clock is gated, the current synchronization logic can toggle the pending state on each pulse. After an even number of pulses during one gated interval, the ADC Controller can resume with no pending interrupt, even though an enabled filter-match event occurred.

## Affected Function
ADC Controller interrupt handling for filter-match events that are generated in the always-on clock domain but must update interrupt status and interrupt pending state in the gated main clock domain.

## Trigger Condition
This is triggered when the ADC Controller enters a state where the main clock domain is gated but the always-on ADC logic continues running, and the same enabled filter-match interrupt source fires multiple times before the main clock domain is ungated.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #11759 明确第一事件置位、第二事件清零的 pulse-sync 缺陷；patch 换 req/ack 并保存 pending bits。 |
| 触发过程 | 主域停钟→AON 两次 filter pulse→toggle 偶数次回原值→恢复主钟→状态/中断丢失。 |
| 测试覆盖 | 检查 cc_sink_det 更新被观察到、intr_state pending；shell 依据 pass/fail sentinel 判结果。 |
| 尚存缺口 | top interrupt intr_debug_cable_o 只打印未断言；单 filter、恰好两脉冲、单时钟比。恒置 pending 需无事件对照拦住。 |
| 环境真实性 | 仅 prim_flop 本地普通寄存器模型；pulse_sync/reqack/2sync 均用原 RTL。门控时钟真实停止；无内部 force。 |
| 跨周期价值 | 高，跨时钟事件累积与停钟恢复。 |
| 题面提示 | 高：题面给出偶数脉冲相消机制。 |
| 原审查后续建议 | 核 prim_flop 与 generic 实现等价，双版本运行；补 top IRQ 断言及 0/1/3 次事件、多源对照。 |

## 原字段证据

`tb_script` 字段内第22–22行：

```text
cat > "${TB_DIR}/prim_flop.sv" <<'SV'
```

`tb_script` 字段内第85–85行：

```text
task automatic send_filter_pulse();
```

`tb_script` 字段内第121–121行：

```text
if (!status_seen || !intr_state_i.q) begin
```

`fix_patch` 字段内第61–61行：

```text
+  prim_sync_reqack u_match_sync (
```
