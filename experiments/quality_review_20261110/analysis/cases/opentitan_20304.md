# opentitan_20304

来源：[原PR](https://github.com/lowRISC/opentitan/pull/20304)；源数据第213行；分类 `RTL_LOGIC`。

保留理由：禁用后命令队列残留有明确原PR依据，新增检查会直接读真实队列深度；scoreboard是适配而非关闭。

本地证据：**原测试待本地实测**。运行准备状态：待校准。

## 原始 HWE 题面

## Description
The bug is in the Entropy Distribution Network (EDN) auto request shutdown path. In auto request mode, EDN stores the programmed `GENERATE_CMD` and `RESEED_CMD` sequences in replay FIFOs so it can resend them to the Cryptographically Secure Random Number Generator (CSRNG). When firmware disables EDN by clearing `CTRL.EDN_ENABLE` while auto request mode is still configured, the EDN main state machine can return to `Idle` without clearing those replay FIFOs.

## Expected Behavior
Disabling EDN must fully terminate the current auto request session. Once the disable transition completes and the EDN main state machine reaches `Idle`, both auto-command replay FIFOs for `GENERATE_CMD` and `RESEED_CMD` must be empty, just as they are after `CTRL.CMD_FIFO_RST`, after boot-time completion, or after leaving auto request mode by clearing `CTRL.AUTO_REQ_MODE`. No command words from the previous auto request session should remain queued after the block has been disabled.

## Actual Behavior
If EDN is disabled directly from an active auto request state, stale generate and reseed command words can remain queued even after the block returns to `Idle`. The disable path does not leave the EDN in a clean disabled state.

## Affected Function
The affected logic is the EDN auto request control path, specifically the EDN main state machine and the replay FIFOs that hold automatic `generate` and `reseed` commands for CSRNG traffic.

## Trigger Condition
Program EDN for auto request mode, populate the `GENERATE_CMD` and `RESEED_CMD` replay FIFOs, and then disable EDN by clearing `CTRL.EDN_ENABLE` without first leaving auto request mode through `CTRL.AUTO_REQ_MODE`. The bug appears when the disable path forces the EDN main state machine back to `Idle` from an active auto request state.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | PR body明确disabled后清auto cmd FIFOs，RTL main_sm_done_pulse在disable路径置1；题面与此一致。 |
| 触发过程 | auto模式装reseed/generate→活跃期间disable→等Idle→查两FIFO和cmd_fifo_cnt清零→后续重启。 |
| 测试覆盖 | 三个真实DUT计数均为零，并继续原disable-auto UVM流程；script更新scoreboard清队列并移除TB主动CMD_FIFO_RST兜底。 |
| 尚存缺口 | 原序列可frontdoor/backdoor disable，固定seed究竟走哪条unknown；只看队列深度不能防“auto从不装入/不工作”，需保留发送和重新使能正常检查。 |
| 环境真实性 | backdoor可能写CTRL寄存器以对齐时机；只是读取内部深度，不强置FIFO；scoreboard被修改同步预期，未见en_scb=0。 |
| 跨周期价值 | 高：配置模式、命令重放队列、shutdown/重启的状态残留。 |
| 题面提示 | 很高：指出FIFO和done后的清空时点；patch目标一行，但作用跨多队列。 |
| 原审查后续建议 | 跑两版并记录实际disable路径；增加通过TL写CTRL的frontdoor重复以及重启后新命令序列验收，检查旧命令未重放。 |

## 原字段证据

`body` 字段内第1–4行：

```text
This PR clears the auto cmd FIFOs after the edn is disabled.
For more precise information check out the individual commit messages.

This PR resolves #19653 
```

`tb_script` 字段内第120–130行：

```text
replace_once(
    "/home/opentitan/hw/ip/edn/dv/env/edn_scoreboard.sv",
    """        // reset fifos if cmd_fifo_rst is true
        if (write && (edn_ctrl.cmd_fifo_rst.q == MuBi4True)) begin
""",
    """        // Reset fifos if cmd_fifo_rst is true or if EDN is being disabled.
        if (write &
```

`tb_script` 字段内第240–284行：

```text
    """  task disable_edn(bit backdoor);
    bit [TL_DW-1:0] ctrl_val;

    // Write EDN's control CSR.
    ctrl_val = {MuBi4False, MuBi4True, MuBi4False, MuBi4False};

    if (!backdoor) begin
      wait_no_outstanding_access();
    end else begin
      cfg.backdoor_disable = 1'b1; // Notify scoreb
```

`tb_script` 字段内第337–343行：

```text
remove_once(
    vseq_path,
    """        // TODO: Remove the following lines resetting the FIFOs based on decision in #19653.
        // Reset cmd FIFO to prevent FIFO from overflowing after re-enabling EDN.
        csr_wr(.ptr(ral.ctrl.cmd_fifo_rst), .value(MuBi4True));
        csr_wr(.ptr(ral.ct
```

`fix_patch` 字段内第162–168行：

```text
@@ -239,7 +239,7 @@ module edn_main_sm import edn_pkg::*; #(
       send_gencmd_o          = 1'b0;
       capt_rescmd_fifo_cnt_o = 1'b0;
       send_rescmd_o          = 1'b0;
-      main_sm_done_pulse_o   = 1'b0;
+      main_sm_done_pulse_o   = 1'b1;
     end
```
