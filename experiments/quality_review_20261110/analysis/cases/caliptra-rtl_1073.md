# caliptra-rtl_1073

来源：[原PR](https://github.com/chipsalliance/caliptra-rtl/pull/1073)；源数据第73行；分类 `RTL_INTERFACE`。

保留理由：真实AXI/AHB桥的背靠背读和反压，原始错误可从公开接口观察；原验收只覆盖卡住时。

本地证据：**仅历史改编证据；原测试待实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

In Caliptra 2.0, the VeeR EL2 RISC-V core's AXI4-to-AHB bridge mishandles back-to-back read requests on the load/store path. If one read is followed immediately by another and the AHB-Lite slave deasserts HREADY while the second request is being presented, the bridge can change that second transfer from a valid AHB NONSEQ read to the wrong transfer type and can lose the low address bits of the buffered request. As a result, the second read can appear on AHB at an aligned or otherwise incorrect address instead of the requested address. The correct behavior is to keep the stalled second read as a valid NONSEQ transfer and preserve its exact requested address, including the low address bits, until the AHB slave accepts it.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | PR引用真实issue #1056与VeeR上游修复；补丁把STREAM_RD的HTRANS从11改成10。 |
| 触发过程 | 第一读0x1000→第二读0x1004恰遇HREADY拉低→检查第二读类型/地址保留。 |
| 测试覆盖 | 首读、次读launch及一次stalled cycle的HTRANS=NONSEQ、HADDR不丢bit2。 |
| 尚存缺口 | 未解除stall、未检查AXI R返回值/ID/重复次数；一直卡住保持地址也可能过。 |
| 环境真实性 | 真实桥和beh_lib，AXI/AHB端口驱动；不含完整CPU，当前测试没有内部force。 |
| 跨周期价值 | 高：连续事务身份与跨协议停顿状态。 |
| 题面提示 | 很高：直接点出NONSEQ和低地址位；属于带定位提示的修复题。 |
| 原审查后续建议 | 复跑原HWE脚本；恢复HREADY并验证两笔响应各一次、地址及数据，区分本项目旧改编TB的历史通过。 |

## 原字段证据

`body` 字段内第1–1行：

```text
Preliminary fix for https://github.com/chipsalliance/caliptra-rtl/issues/1056, but not the final RV upgrade for 2.1 as https://github.com/chipsalliance/Cores-VeeR-EL2/pull/424 is still pending.
```

`tb_script` 字段内第155–183行：

```text
    @(negedge clk);
    axi_arvalid = 1'b1;
    axi_araddr = FIRST_ADDR;
    #1;
    if (ahb_htrans !== 2'b10 || ahb_haddr !== FIRST_ADDR) begin
      $display("First read launch mismatch: htrans=%b haddr=%08x", ahb_htrans, ahb_haddr);
      $fatal(1, "first read launch mismatch");
    end

    @(po
```

`fix_patch` 字段内第23–28行：

```text
@@ -327,7 +327,7 @@ import el2_pkg::*;
                   cmd_done        = buf_state_en & ~master_valid;                     // last one of the stream should not send a htrans
                   bypass_en       = master_ready & master_valid & (buf_nxtstate == STREAM_RD) & buf_state_en;
            
```
