# caliptra-rtl_506

来源：[原PR](https://github.com/chipsalliance/caliptra-rtl/pull/506)；源数据第83行；分类 `RTL_LOGIC`。

保留理由：溢出保持和清空后恢复都检查了，软件可见状态有原PR和寄存器文档支持。

本地证据：**原测试待本地实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

In Caliptra's `entropy_src` block, the firmware-override observe FIFO overflow indicator is not held in a stable, software-visible state. The observe FIFO is the buffer that lets firmware read raw entropy samples through `FW_OV_RD_DATA`. When firmware override mode is enabled and new entropy samples keep arriving after that FIFO has become full, `FW_OV_RD_FIFO_OVERFLOW` can appear only as a pulse instead of staying asserted. As a result, firmware can miss the fact that samples were dropped and cannot reliably tell whether the data it reads from `FW_OV_RD_DATA` is still a contiguous stream of samples. The expected behavior is that once the firmware-override observe FIFO overflows, `FW_OV_RD_FIFO_OVERFLOW` remains asserted on repeated reads until the observe FIFO has been completely drained and sampling has restarted with contiguous data again; only then should the status clear.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | PR引用OpenTitan #21640并说明状态要保持到FIFO清空、重新连续采样；包含rw0c改为硬件清除的文档变更。 |
| 触发过程 | FW override采样填满64项→继续采样溢出→停采样反复读overflow→完全drain→重新采样→overflow应清。 |
| 测试覆盖 | FIFO满/空深度、4次溢出状态保持、重启采样后的清除；真实entropy_src经AHB访问。 |
| 尚存缺口 | 未核对读出的样本序列是否连续；可能漏掉仅正确驱动状态位、实际采样仍丢数的假修复。 |
| 环境真实性 | 使用已有physical_rng模型提供输入，真实FIFO/寄存器；没有强行设置FIFO状态。 |
| 跨周期价值 | 高：长期填满、溢出、排空、重启四阶段。 |
| 题面提示 | 高：已指出overflow脉冲与保持期，但给出的基本是软件接口契约。 |
| 原审查后续建议 | 复现双版本；补不溢出时读写和可追踪样本序列；与同源OpenTitan移植案例按bug家族去重。 |

## 原字段证据

`body` 字段内第1–13行：

```text
Keep applying fw_ov_rd_fifo_overflow instead of pulsing. This commit is a manual port of the following Opentitan commit:

b454878f2528b49318ff2b604cb8d59a6e59b0ea

Which is associated with
https://github.com/lowRISC/opentitan/pull/21640.

Original commit description:

This commit applies the fw_ov_r
```

`tb_script` 字段内第228–269行：

```text
    write_single_word(ADDR_CONF, 32'h02649999);
    write_single_word(ADDR_FW_OV_CONTROL, 32'h00000096);
    write_single_word(ADDR_MODULE_ENABLE, 32'h00000006);

    generate_rng = 1'b1;
    wait_for_depth_at_least(7'd64, 4000);
    repeat (64) @(posedge clk_tb);

    generate_rng = 1'b0;
    repea
```

`fix_patch` 字段内第100–116行：

```text
@@ -2336,8 +2336,8 @@ module entropy_src_core
   // contiguous as possible.
   logic sfifo_observe_gate_d, sfifo_observe_gate_q;
 
-  assign sfifo_observe_gate_d = (sfifo_observe_push && sfifo_observe_full) ? 1'b0 :
-                                !sfifo_observe_not_empty                   ? 1'b1 :
```
