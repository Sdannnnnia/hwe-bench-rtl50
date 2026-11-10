# ibex_167

来源：[原PR](https://github.com/lowRISC/ibex/pull/167)；源数据第28行；分类 `RTL_SPEC`。

保留理由：真实程序经过halt和DRET，直接验证恢复地址。

本地证据：**原测试配对（本轮）**。运行准备状态：待校准。

## 原始 HWE 题面

When an external debug halt request (`debug_req`) arrives while Ibex is executing a regular instruction, the controller logic that enters debug mode saves the current instruction address in the debug return PC CSR (`dpc`) instead of the address of the following instruction. After the core executes the debug return instruction (`dret`), execution resumes from that saved `dpc`, so the interrupted instruction is executed a second time. For halt-request debug entry, `dpc` must hold the next instruction address, and the first instruction executed after `dret` must be the instruction that would have followed the interrupted one.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #164有同一条指令Debug前后重复执行trace，body明确halt该保存下一PC。 |
| 触发过程 | 执行addi→halt请求→Debug ROM执行DRET→错误恢复到已执行addi。 |
| 测试覆盖 | RVFI看到DRET后第一条指令PC必须NEXT_PC；有超时。 |
| 尚存缺口 | 未计数目标addi是否已完成，也未核对x5最终值；跳过指令而仅恢复PC可能遗漏。仅32位常规指令，未覆盖compressed、branch或EBREAK。 |
| 环境真实性 | 真实core_tracer+RVFI，正常指令/响应；内部pc/debug只用于安排外部请求，无force。 |
| 跨周期价值 | 跨中断式进入/恢复，较好功能案例。 |
| 题面提示 | 强：题面直接说明保存当前而非下条PC。 |
| 原审查后续建议 | 加目标寄存器副作用、compressed和EBREAK保留当前PC对照。 |

## 已有原测试日志

- [buggy.stdout.log](../runtime/ibex_167/buggy.stdout.log)
- [reference.stdout.log](../runtime/ibex_167/reference.stdout.log)

## 原字段证据

`body` 字段内第3–3行：

```text
request instead of the PC of the current instruction (only valid
```

`tb_script` 字段内第209–209行：

```text
end else if (seen_dret_q && !done_o) begin
```

`tb_script` 字段内第211–211行：

```text
pass_o <= (rvfi_pc_rdata == NEXT_PC);
```
