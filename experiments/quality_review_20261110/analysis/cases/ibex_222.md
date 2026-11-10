# ibex_222

来源：[原PR](https://github.com/lowRISC/ibex/pull/222)；源数据第23行；分类 `RTL_LOGIC`。

保留理由：执行结束后取指停顿，旧写使能继续生效；此前使用过不影响候选资格。

本地证据：**原测试配对（历史）**。完整主评测准备状态：待校准。

## 原始 HWE 题面

When a single-cycle instruction such as `addi` completes in Ibex and the next instruction fetch is stalled because the instruction-fetch grant signal (`instr_gnt_i`) stays low, the core can remain in the instruction-decode (ID) stage with the register-file write-enable signal (`regfile_we`) still asserted. During those stalled cycles, the destination register of the completed instruction may be written again even though no new instruction has arrived. The affected functionality is the ID-stage logic that determines when the current instruction has finished and whether register-file writes remain enabled while the instruction-fetch interface is stalled. Once the single-cycle instruction has committed its result, `regfile_we` must be deasserted on every cycle while the core waits for the next instruction-fetch grant, and the destination register must retain its committed value throughout that stall.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #216有重复累加破坏x13的波形和trace；body明确单周期指令误用multicycle_done。 |
| 触发过程 | 单周期addi完成→下一fetch延迟grant→ID残留指令→重复写寄存器。 |
| 测试覆盖 | 先确认x13写成1，再连续4拍检查stall期间regfile_we为0。 |
| 尚存缺口 | 使用addi x13,x0,1，重复写同值不会破坏架构值；只查内部使能，没查释放stall后正常执行、多周期操作仍能写回。 |
| 环境真实性 | 完整core；IF正常只返回首次请求，后续无grant；data_rvalid恒1但本场景无数据事务。 |
| 跨周期价值 | 跨完成/停顿的生命周期边界，值得保留。 |
| 题面提示 | 强：题面明确ID、regfile_we、完成后每拍要求；原body甚至给instr_multicycle_done。 |
| 原审查后续建议 | 补自增操作及恢复取指后的最终寄存器结果，兼顾load/mul回归。 |

## 已有原测试日志

- [buggy.stdout.log](../runtime/ibex_222/buggy.stdout.log)
- [buggy.stderr.log](../runtime/ibex_222/buggy.stderr.log)
- [reference.stdout.log](../runtime/ibex_222/reference.stdout.log)
- [reference.stderr.log](../runtime/ibex_222/reference.stderr.log)

## 原字段证据

`tb_script` 字段内第56–56行：

```text
32'h00000080: get_instr = 32'h00100693; // addi x13, x0, 1
```

`tb_script` 字段内第117–117行：

```text
if (bad_stall_cycles_q != 32'd0 || ibex_i.id_stage_i.regfile_we) begin
```

`fix_patch` 字段内第25–25行：

```text
+  assign instr_executing = instr_new_i | (instr_multicycle & ~instr_multicycle_done_q);
```
