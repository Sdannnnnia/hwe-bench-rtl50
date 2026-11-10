# ibex_475

来源：[原PR](https://github.com/lowRISC/ibex/pull/475)；源数据第16行；分类 `RTL_SPEC`。

保留理由：Debug内异常污染先前CSR，适合状态保持问题；现有测试只是最小起点。

本地证据：**原测试配对（本轮）**。运行准备状态：待校准。

## 原始 HWE 题面

When Ibex takes an exception while the core is already in Debug Mode, the exception-handling path still overwrites machine Control and Status Registers (CSRs) that record trap state. As a result, `mepc`, `mcause`, `mtval`, and `mstatus` can be modified even though the core is already in Debug Mode. The affected functionality is the Debug Mode exception/CSR handling logic. The correct behavior is that an exception taken in Debug Mode must leave those CSRs unchanged; in particular, it must not clear the interrupt-enable state in `mstatus` or replace the existing trap information in `mepc`, `mcause`, and `mtval`. This is triggered whenever an exception is taken after `debug_mode` is already active.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | 补丁明确引用Debug Spec v0.13.2 p39异常不更新CSR；原问题与该规则一致。 |
| 触发过程 | CSR处于旧状态→debug_mode=1→模拟非法指令异常→检查四个machine CSR未变。 |
| 测试覆盖 | 读回mepc、mcause、mtval、mstatus，比较reset值。 |
| 尚存缺口 | 只从reset值验证；没查dpc/dcsr，也没查普通异常应更新。把所有异常写CSR禁掉可能通过。 |
| 环境真实性 | 真实CSR寄存器模块，debug/exception输入由TB直接驱动，未执行真正debug ROM。 |
| 跨周期价值 | 状态保护，触发链较短；可作为中低难度组。 |
| 题面提示 | 中：明确哪些CSR该保持，接近单处条件门控但没有给具体补丁。 |
| 原审查后续建议 | 补非零初值、普通异常会更新和debug进入/返回回归。 |

## 已有原测试日志

- [buggy.stdout.log](../runtime/ibex_475/buggy.stdout.log)
- [reference.stdout.log](../runtime/ibex_475/reference.stdout.log)

## 原字段证据

`fix_patch` 字段内第205–205行：

```text
+          // includes cause, epc, tval, dpc and mstatus." [Debug Spec v0.13.2, p.39]
```

`tb_script` 字段内第202–202行：

```text
top.debug_mode_i = 1;
```

`tb_script` 字段内第222–222行：

```text
(mtval != 0x00000000u) || (mstatus != 0x00000080u)) {
```
