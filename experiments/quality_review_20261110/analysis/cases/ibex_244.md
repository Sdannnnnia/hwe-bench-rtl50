# ibex_244

来源：[原PR](https://github.com/lowRISC/ibex/pull/244)；源数据第24行；分类 `RTL_LOGIC`。

保留理由：背靠背CSR开关中断暴露流水线漏响应，有现成完整程序验收。

本地证据：**原测试配对（历史）**。完整主评测准备状态：待校准。

## 原始 HWE 题面

When software uses RISC-V Control and Status Register (CSR) instructions to enable interrupts through the `mie` (machine interrupt-enable) and `mstatus` (machine status) CSRs while an interrupt is already pending, Ibex can perform the CSR-related pipeline flush and then resume normal instruction execution instead of entering the interrupt handler. The failing case is a back-to-back sequence that first enables the relevant source in `mie`, then sets the global interrupt-enable bit in `mstatus`, and then immediately clears that bit again: the pending interrupt can be lost and a following non-interrupt instruction can retire. The affected logic is the CSR-related pipeline-flush and interrupt-entry path around updates to `mie` and `mstatus`. Correct behavior is that once those CSR write/set operations make a pending interrupt eligible for service, the core must take the interrupt before normal execution resumes, even if the next instruction would disable interrupts again.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | body说明CSR更新后的中断可见性和flush职责；独立完整体系规范仍可补，但问题/修复意图一致。 |
| 触发过程 | IRQ一直pending→写mie→置mstatus.MIE→紧接清MIE→未在应有边界进入handler。 |
| 测试覆盖 | 完整core分别在handler和普通路径写marker，脚本解析IRQ_HANDLER_STORE，失败路径是FAIL_STORE。 |
| 尚存缺口 | 未查mepc/mcause及中断返回；提前/无条件中断可能碰巧到正确marker；未覆盖无pending和CSR read/clear正常情况。 |
| 环境真实性 | 完整core+按请求返回指令模型，无force，实际CSR指令和外部IRQ。 |
| 跨周期价值 | CSR、controller、取指跨拍相互影响，优先保留。 |
| 题面提示 | 强：题面给三条CSR操作序列和flush/IRQ入口。 |
| 原审查后续建议 | 复用历史原脚本F2P证据并核哈希；补无IRQ及mepc/返回地址检查。 |

## 已有原测试日志

- [buggy.stdout.log](../runtime/ibex_244/buggy.stdout.log)
- [buggy.stderr.log](../runtime/ibex_244/buggy.stderr.log)
- [reference.stdout.log](../runtime/ibex_244/reference.stdout.log)
- [reference.stderr.log](../runtime/ibex_244/reference.stderr.log)

## 原字段证据

`body` 字段内第2–2行：

```text
for enabling interrupts, reads and clears are uncritical for these CSRs), and makes sure the controller is actually able to start handling interrupts while doing a CSR-related pipeline flush.
```

`tb_script` 字段内第112–112行：

```text
$display("IRQ_HANDLER_STORE");
```

`tb_script` 字段内第250–250行：

```text
if grep -q "IRQ_HANDLER_STORE" "$SIM_LOG"; then
```
