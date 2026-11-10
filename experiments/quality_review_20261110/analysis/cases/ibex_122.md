# ibex_122

来源：[原PR](https://github.com/lowRISC/ibex/pull/122)；源数据第30行；分类 `RTL_LOGIC`。

保留理由：跨字store地址和byte-enable丢失，完整CPU程序可触发。

本地证据：**原测试配对（本轮）**。完整主评测准备状态：待校准。

## 原始 HWE 题面

Ibex mishandles misaligned 32-bit stores in the load-store unit. When a store address is not 32-bit aligned and the access must be split across two adjacent 32-bit words, the address and byte-enable calculation for the second memory transaction is incorrect, so the split store does not preserve the original byte lanes. In the failing boundary case, a 32-bit store to an address whose two least significant bits are `01` is not performed as the required pair of aligned writes. The correct behavior is to issue two aligned store transactions that together write the same four bytes as the original store: the first transaction writes byte lanes 1-3 of the lower word, and the second transaction writes byte lane 0 of the next word. This affects the load-store unit and the address generation used for the second part of a misaligned store, and it is triggered by a misaligned 32-bit store that crosses a 32-bit word boundary.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | body解释AGU拿到对齐地址导致后半字节位置错误，原语义是保持32位store四个字节。 |
| 触发过程 | 执行sw到地址1→首拍应写地址0 lanes1-3→次拍应写地址4 lane0。 |
| 测试覆盖 | 真实core观察两次store grant的地址和byte-enable。 |
| 尚存缺口 | 写数据全0且checker不比wdata，抓不到旋转错误；第二grant立刻成功，无法检测之后额外写或错误完成。 |
| 环境真实性 | 完整core+响应排队，无force；不是只有替代AGU的LSU小模型。 |
| 跨周期价值 | 跨AGU/LSU两事务，值得保留。 |
| 题面提示 | 中：给出跨字位置和正确lane，但未指定内部变量修法。 |
| 原审查后续建议 | 补非零图案数据、offset2/3、load和响应完成后的额外写监视。 |

## 已有原测试日志

- [buggy.stdout.log](../runtime/ibex_122/buggy.stdout.log)
- [reference.stdout.log](../runtime/ibex_122/reference.stdout.log)

## 原字段证据

`body` 字段内第4–4行：

```text
- The first one is a cleanup of the LSU that also fixes a critical error. Previously, misaligned loads/stores were broken as the byte enable generation and read data alignment for the second transaction part were not wor
```

`tb_script` 字段内第61–61行：

```text
32'h00000088: instr_rom = 32'h0000A023; // sw x0, 0(x1)
```

`tb_script` 字段内第182–182行：

```text
if ((data_addr_o != 32'h0000_0004) || (data_be_o != 4'b0001)) begin
```
