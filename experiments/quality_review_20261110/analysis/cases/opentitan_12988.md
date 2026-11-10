# opentitan_12988

来源：[原PR](https://github.com/lowRISC/opentitan/pull/12988)；源数据第237行；分类 `RTL_TIMING_SYNC`。

保留理由：短事件跨慢时钟丢失，激励、捕获和复位清除均可观察。

本地证据：**原测试待本地实测**。运行准备状态：待校准。

## 原始 HWE 题面

## Description
The OpenTitan Power Manager (`pwrmgr`) has a clock-domain crossing (CDC) bug in its escalation-reset handling path. The affected function is the logic that takes an escalation-reset request on `esc_rst_tx_i`, transfers it into the slow clock domain, and turns it into the escalation-triggered reset request path that drives the life-cycle reset request output (`rst_lc_req`).

## Expected Behavior
If `pwrmgr` observes an escalation-reset request on `esc_rst_tx_i`, it must capture that request even when the input is only a brief, non-permanent pulse that begins and ends between consecutive slow-clock sampling edges. After the request has been captured, the slow-domain escalation reset request must assert, `rst_lc_req` must assert, and the captured escalation request must remain asserted until reset clears it.

## Actual Behavior
When `esc_rst_tx_i` is only asserted briefly, `pwrmgr` can lose the request while synchronizing it into the slow clock domain. The escalation receiver can observe the pulse, but the slow-domain escalation reset request never asserts, `rst_lc_req` does not assert, and the escalation reset is effectively dropped.

## Affected Function
This affects `pwrmgr`'s escalation-reset CDC and request-latching logic between the escalation input and the slow-domain reset-request path.

## Trigger Condition
The bug is triggered when `esc_rst_tx_i` is a transient pulse asserted for fewer than two slow-clock cycles, so the pulse can occur entirely between slow-clock sampling edges instead of remaining continuously asserted.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #12981 明确少于两慢周期会丢 esc reset；PR 要求捕获并保持至系统 reset。 |
| 触发过程 | 快域 escalation 短脉冲→receiver 检出→慢域同步→rst_lc_req→reset 清除→回 active。 |
| 测试覆盖 | 检查 receiver 请求、慢域请求、复位请求、reset 后请求清除和回 active。 |
| 尚存缺口 | 只有一个相位/脉宽；永久拉高请求会被清除检查拦住，假造请求仍需无事件/多脉宽回归。 |
| 环境真实性 | 原 UVM 接口刺激；新增 internal debug hooks 仅观察；真实 CDC RTL，数字仿真不涉及模拟亚稳态。 |
| 跨周期价值 | 高，跨时钟事件生命周期。 |
| 题面提示 | 高：题面已指出 latch/hold 和具体丢失域。 |
| 原审查后续建议 | 双版本运行并复用无 escalation、长短脉冲和不同慢时钟相位回归。 |

## 原字段证据

`body` 字段内第5–5行：

```text
- capture and hold escalate request until the system resets.
```

`tb_script` 字段内第47–47行：

```text
// Place a short escalation pulse entirely between slow clock edges.
```

`tb_script` 字段内第56–56行：

```text
`DV_SPINWAIT(wait(cfg.pwrmgr_vif.slow_esc_rst_req == 1'b1);,
```

`tb_script` 字段内第64–64行：

```text
`DV_SPINWAIT(wait(cfg.pwrmgr_vif.pwr_rst_req.rst_lc_req == '0);,
```
