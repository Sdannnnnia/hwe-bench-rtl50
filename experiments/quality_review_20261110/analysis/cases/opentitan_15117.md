# opentitan_15117

来源：[原PR](https://github.com/lowRISC/opentitan/pull/15117)；源数据第233行；分类 `RTL_TIMING_SYNC`。

保留理由：外部慢上升引发误中断，既验无误报又等正常读完成，保留。

本地证据：**原测试待本地实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

## Description
The affected functionality is the OpenTitan I2C IP host-side finite state machine (FSM) that raises the `sda_interference` event/interrupt when the host controller believes SDA (Serial Data) is being held low by another device. In I2C, driving a logical 1 on SDA means releasing the open-drain line so an external pull-up can bring it high. Because the sampled SDA input (`sda_i`) passes through an input synchronizer and the bus has non-zero rise time, the sampled value is allowed to remain low for a short time after the host releases SDA.

## Expected Behavior
When the host releases SDA and expects it to be high, the controller must allow enough time for a legal SDA rise to propagate through the bus and input synchronizer before declaring interference. On an uncontended bus, a clean host transaction, including a host read transaction, must not raise `sda_interference` just because SDA is still low for a few cycles immediately after release; the transfer should continue and complete normally.

## Actual Behavior
The host-side FSM checks for SDA interference in the same cycle that it changes SDA from driven low to released high. As a result, the controller can compare its newly released output against a stale synchronized low sample on `sda_i` and falsely conclude that another device is holding SDA low. This raises `sda_interference` during an otherwise valid transaction.

## Trigger Condition
This occurs in host mode whenever the controller transitions SDA from driven low to released high and the synchronized SDA input still reflects the old low level for one or more cycles because of normal rise-time and synchronization delay. One observable case is a clean host read transaction on an uncontended bus: after the host releases SDA, the line is briefly sampled low, and the design incorrectly flags `sda_interference` instead of allowing the read transaction to complete.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #15067 明确 open-drain 上升时间和输入同步延迟；原 PR 等 rise+sync 后再判 interference。 |
| 触发过程 | 释放 SDA→外部仍低 3 拍→同步器稍后看到高→原 FSM 过早比对→误报 interference。 |
| 测试覆盖 | 监控误中断，确认收到读字节、hostidle、RX 空；循环和 fatal 有界。 |
| 尚存缺口 | 未增加真正长时间干扰必须报警的对照；恒定屏蔽 interference 的假修复可能过此单例。 |
| 环境真实性 | force 在 tb.cio_sda_i 外部输入线上，模拟慢上升；不是强设 DUT FSM。需与配置 t_r=4 的合法窗口核对。 |
| 跨周期价值 | 高，物理接口数字建模、同步延迟和 FSM 观察时点。 |
| 题面提示 | 高：题面说明同拍比较 stale synchronized sample 的原因。 |
| 原审查后续建议 | 双版本跑此 UVM，追加复用原真实干扰测试；记录 force 仅用于引脚驱动。 |

## 原字段证据

`tb_script` 字段内第144–144行：

```text
if (!uvm_hdl_force("tb.cio_sda_i", 1'b0)) begin
```

`tb_script` 字段内第147–147行：

```text
cfg.clk_rst_vif.wait_clks(3);
```

`tb_script` 字段内第189–189行：

```text
`DV_CHECK_FATAL(got_rx_byte, "Timed out waiting for read data")
```

`body` 字段内第2–2行：

```text
- instead of checking the input value immediately after changing sda, we instead wait through the rise time and sychronization delays.
```
