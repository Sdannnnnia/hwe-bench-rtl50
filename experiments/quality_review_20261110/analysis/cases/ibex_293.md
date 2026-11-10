# ibex_293

来源：[原PR](https://github.com/lowRISC/ibex/pull/293)；源数据第20行；分类 `RTL_INTERFACE`。

保留理由：没有新分支时，已经发出的顺序请求掉了；与#332的新协议讨论可区分。

本地证据：**原测试配对（本轮）**。完整主评测准备状态：待校准。

## 原始 HWE 题面

Recent instruction-side logic and prefetch-buffer changes broke the instruction fetch handshake in Ibex. The instruction-side prefetch buffer issues fetches through a request/grant/response interface: `instr_req_o` requests an instruction fetch, `instr_gnt_i` accepts that request, and the returned instruction data arrives later. In the failing behavior, if a fetch request is made and the grant does not arrive immediately, the prefetch buffer can stop treating that fetch as pending and can advance to a different address before the original request has been accepted. This can desynchronize instruction fetches and cause execution to stop early in the tracing example. The affected logic is the instruction-side prefetch buffer and its request/address tracking. When a fetch is pending but has not yet been granted, including the sequential fetch immediately after a granted branch fetch, `instr_req_o` must remain asserted and `instr_addr_o` must remain at the same word-aligned address until `instr_gnt_i` acknowledges that request.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | body明确缺grant资格导致spurious address update，原issue #288有执行trace提前中断。 |
| 触发过程 | branch fetch被grant并返回→发下一个顺序请求但无grant→上层req撤掉→待办请求应保持。 |
| 测试覆盖 | 逐阶段检查req及地址0x100/0x104，包括最终grant。 |
| 尚存缺口 | 未检查返回数据消费、PMP错误或spurious rvalid；常拉req可能过本序列。 |
| 环境真实性 | 真实prefetch和FIFO，无force，req_i撤销属于上层停顿模型。 |
| 跨周期价值 | 多拍请求记忆，适合作中等复杂度。 |
| 题面提示 | 强：题面给出pending tracking和精确触发序列。 |
| 原审查后续建议 | 复现原脚本；补请求完成后停止、分支取消和普通连续返回。 |

## 已有原测试日志

- [buggy.stdout.log](../runtime/ibex_293/buggy.stdout.log)
- [reference.stdout.log](../runtime/ibex_293/reference.stdout.log)

## 原字段证据

`body` 字段内第2–2行：

```text
- Add missing grant qualification to stop spurious address updates
```

`tb_script` 字段内第110–110行：

```text
expect_state(top, "held_request", true, 0x00000104);
```

`tb_script` 字段内第113–113行：

```text
expect_state(top, "grant_held_request", true, 0x00000104);
```
