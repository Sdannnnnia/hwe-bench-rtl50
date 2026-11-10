# ibex_465

来源：[原PR](https://github.com/lowRISC/ibex/pull/465)；源数据第17行；分类 `RTL_SPEC`。

保留理由：从U态进入Debug仍留在U态，程序可正常触发。

本地证据：**原测试配对（本轮）**。完整主评测准备状态：待校准。

## 原始 HWE 题面

When Ibex takes a debug request while the core is executing in RISC-V User mode (U-mode), it can jump to the debug ROM while still treating the current execution privilege as U-mode instead of RISC-V Machine mode (M-mode). This affects the debug-entry privilege handling in the core's control and CSR logic. The observed consequence is that code running from the debug ROM can raise illegal-instruction exceptions when it accesses debug control and status registers (CSRs), because those accesses are still being checked as if the core were in U-mode. The expected behavior is that once debug mode is entered, all execution in the debug ROM must run with the core's current privilege level set to M-mode, regardless of the privilege level from which debug was entered.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | body明确Debug运行应为M态、DRET恢复；issue #463有debug ROM访问CSR抛非法指令证据。 |
| 触发过程 | 启动设置mepc/mstatus→MRET到U态→外部debug请求→进入Debug时权限仍U。 |
| 测试覆盖 | 真实core执行进入U态程序，检测debug_mode时priv_lvl_q必须M。 |
| 尚存缺口 | 只打印dcsr.prv而不校验；不执行DRET或debug CSR。永久M态或损坏恢复可能通过。 |
| 环境真实性 | 真实core和按请求返回的指令模型；内部信号用于触发与观察，未force。 |
| 跨周期价值 | 跨特权状态与debug入口，值得保留。 |
| 题面提示 | 中：定位debug-entry权限处理，未给具体if分支。 |
| 原审查后续建议 | 增加Debug CSR读写、dcsr保存与DRET恢复U态。 |

## 已有原测试日志

- [buggy.stdout.log](../runtime/ibex_465/buggy.stdout.log)
- [reference.stdout.log](../runtime/ibex_465/reference.stdout.log)

## 原字段证据

`body` 字段内第2–2行：

```text
- Previous priv level is restored from dcsr on DRET
```

`tb_script` 字段内第127–127行：

```text
if (dut.cs_registers_i.priv_lvl_q == 2'b11) begin
```

`tb_script` 字段内第66–66行：

```text
// Remain in debug ROM so the privilege mode can be observed after entry.
```
