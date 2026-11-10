# opentitan_20884

来源：[原PR](https://github.com/lowRISC/opentitan/pull/20884)；源数据第207行；分类 `RTL_TIMING_SYNC`。

保留理由：原issue提供128拍超时契约和现成回归，近阈值故障跨时钟丢失，很适合因果调试。

本地证据：**原测试待本地实测**。运行准备状态：待校准。

## 原始 HWE 题面

## Description
OpenTitan's Power Manager (pwrmgr) contains escalation clock-timeout logic that is supposed to detect when the alert escalation path stops responding while the system is in its normal active state. If the escalation clock remains inactive for more than 128 pwrmgr clock cycles, pwrmgr must treat that as an escalation fault and initiate a local escalation reset.

## Expected Behavior
A stall shorter than the 128-cycle timeout threshold must not trigger an escalation reset. Once the escalation clock has been inactive long enough to exceed that threshold, the timeout condition must persist until reset handling takes effect. Even if the escalation clock starts toggling again shortly after the threshold is crossed, pwrmgr must still disable CPU fetch and issue the escalation reset request.

## Actual Behavior
The timeout condition is not persistent. If the escalation clock stops for only slightly more than the timeout threshold and then restarts soon afterward, pwrmgr can lose the fault indication before the reset path reacts to it. In that case, CPU fetch remains enabled and no escalation reset request is generated even though the timeout threshold was exceeded.

## Trigger Condition
This bug is triggered in the pwrmgr escalation timeout path when the escalation clock is halted just over the 128-cycle limit and then restarted before the fault has been latched as a persistent reset condition. Very long stalls still trigger the reset reliably, so the failure is most visible in near-threshold cases.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #20516引用原theory_of_operation，超时要持续到reset；PR说明clk_i检测、clk_lc使用。 |
| 触发过程 | active→停止escalation clock略超128拍→136拍后恢复→timeout应持续并触发reset。 |
| 测试覆盖 | 脚本仅启用原pwrmgr_escalation_timeout_vseq里已存在但注释的136拍分支，固定seed=2；完整checker函数在base源码，字段本身未包含。 |
| 尚存缺口 | 本地未核查check_stopped_esc_clk完整实现，准确检查reset/fetch哪些信号unknown；单时钟相位不能概括所有CDC边界。 |
| 环境真实性 | 原UVM完整pwrmgr环境，改的是测试调用而非RTL或内部force；数字CDC测不到模拟亚稳态概率。 |
| 跨周期价值 | 高：近阈值事件、跨时钟同步、reset响应延迟。 |
| 题面提示 | 高：题面已告诉timeout非持久及128阈值，但跨域保持点仍待定位。 |
| 原审查后续建议 | 取base现有checker函数核对并双版本运行，保存短于阈值/136/长停钟分支结果；追加相位变化而保持同一契约。 |

## 原字段证据

`body` 字段内第1–3行：

```text
The escalation timeout needs to persist until reset. The timeout is detected by clk_i, but the timeout is used to drive a flop clocked by clk_lc. This change adds a synchronizer from clk_i to clk_lc, and a clk_lc flop reset by rst_lc_n. The output of this flop is used to set the fault_status and as 
```

`resolved_issues` 字段内第1–1行：

```text
[{"org": "lowRISC", "repo": "opentitan", "number": 20516, "state": "closed", "title": "[rtl,pwrmgr] escalation timeout should persist", "body": "### Description\r\n\r\nIf the escalation network stops for more than 128 cycles, pwrmgr should request an escalation reset, per https://opentitan.org/book/
```

`tb_script` 字段内第25–38行：

```text
paths = [
    Path("hw/top_earlgrey/ip_autogen/pwrmgr/dv/env/seq_lib/pwrmgr_escalation_timeout_vseq.sv"),
    Path("hw/ip_templates/pwrmgr/dv/env/seq_lib/pwrmgr_escalation_timeout_vseq.sv"),
]
old = "    // check_stopped_esc_clk(136, 1'b1);\n"
new = "    check_stopped_esc_clk(136, 1'b1);\n"

for pat
```

`fix_patch` 字段内第30–57行：

```text
+  prim_flop_2sync #(
+    .Width(1),
+    .ResetValue('0)
+  ) u_esc_timeout_sync (
+    .clk_i(clk_lc),
+    .rst_ni(rst_lc_n),
+    .d_i(esc_timeout),
+    .q_o(esc_timeout_lc_d)
+  );
+
+  always_ff @(posedge clk_lc or negedge rst_lc_n) begin
+    if (!rst_lc_n) begin
+      esc_timeout_lc_q <= 
```
