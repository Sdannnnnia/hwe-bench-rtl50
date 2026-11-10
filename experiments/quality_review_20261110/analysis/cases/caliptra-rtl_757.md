# caliptra-rtl_757

来源：[原PR](https://github.com/chipsalliance/caliptra-rtl/pull/757)；源数据第76行；分类 `RTL_INTERFACE`。

保留理由：从停住的读到竞争写再到读写先后完成都测到了，接口层复现较干净。

本地证据：**仅历史改编证据；原测试待实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

In Caliptra's AXI subordinate arbiter (`axi_sub_arb`), overlapping read and write traffic can be arbitrated incorrectly when a read request has already been selected but is still blocked by downstream backpressure. If a write request becomes valid in the same cycle that the downstream hold is released, the arbiter can switch to the write too early and the pending read can be lost. This affects the AXI block that merges read and write requests onto a shared downstream request interface. The expected behavior is testable: once a read or write beat has won arbitration, that winner must remain selected until the downstream interface actually accepts that beat; only after the accepted transfer completes may the arbiter apply its normal write-over-read priority to choose the next request. Under this trigger condition, the stalled read must complete first, and the write may be issued only afterward.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | PR明确AXI subordinate arb修复并引用issue #753；原TB引用arbiter关于hold期间winner持有的设计注释。 |
| 触发过程 | 读获仲裁但下游hold→继续hold→释放hold同拍写到来→读先接收→下拍写接收。 |
| 测试覆盖 | 每阶段dv/write/address/r_hld/w_hld及最后wdata；有正向进展而非单检查保持。 |
| 尚存缺口 | 固定C_LAT=0与单beat；未验证burst、不同ID/size、C_LAT变化和错误返回。 |
| 环境真实性 | 真实axi_sub_arb端口级测试，无替身/内部force；prepare只对非目标integration文件做CRLF归一。 |
| 跨周期价值 | 高：跨周期仲裁所有权与新竞争者交叠。 |
| 题面提示 | 很高：已告诉winner需保持到接受及read先write后。 |
| 原审查后续建议 | 原HWE双版本校准，追加write被hold、burst及C_LAT配置的已有回归；与本项目B07改编记录分开。 |

## 原字段证据

`body` 字段内第1–2行：

```text
AXI Sub Arb fix. 
* Resolves #753 
```

`tb_script` 字段内第164–217行：

```text
    // Cycle 0: a single-beat read has already won arbitration, but the downstream
    // component is holding the transfer off. The arbiter comment explicitly says the
    // current winner must keep priority when granted during a hold.
    @(negedge clk);
    drive_cycle(1'b1, 3'd2, 1'b1, 1'b0, 3'
```

`prepare_script` 字段内第21–23行：

```text
# Normalize the one CRLF source file touched by fix.patch so the runtime-mounted
# LF patch applies cleanly inside the harness.
perl -0pi -e 's/\r\n/\n/g' src/integration/rtl/caliptra_top.sv
```
