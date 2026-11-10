# ibex_377

来源：[原PR](https://github.com/lowRISC/ibex/pull/377)；源数据第18行；分类 `RTL_INTERFACE`。

保留理由：首响应报错后过早跳异常，后半事务仍控制AGU，属于很好的跨模块时序问题。

本地证据：**原测试配对（历史）**。完整主评测准备状态：待校准。

## 原始 HWE 题面

The Ibex load-store unit mishandles a store whose address is not naturally aligned and therefore has to be split into two internal memory transactions. If the first transaction returns a memory fault, the unit can report the store as complete and raise the store fault immediately, even though the second half of the split access is still outstanding. The expected behavior is that the second transaction is still issued and allowed to finish, and the store fault is reported only after responses for both halves of the split access have been received.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #374描述异常handler的jump被LSU残留增址污染；body解释等待两笔完成以避免不同步。 |
| 触发过程 | 跨字store发两笔→首响应error→过早完成/异常→次响应后才真正排空。 |
| 测试覆盖 | 真实LSU检查两笔地址/BE、首响应不complete、不store_err、第二响应才complete+store_err，最终busy清零。 |
| 尚存缺口 | 没运行完整controller/handler，也没查mtval与下一条jump；仅首拍错、第二拍成功一种组合。 |
| 环境真实性 | 模块级端口激励，TB按addr_incr_req更新AGU结果，无内部force。 |
| 跨周期价值 | 异常排空很合项目；与#276相邻演化，报告分同一家族。 |
| 题面提示 | 很强：题面直接给出“必须等第二响应后报错”的修复约束。 |
| 原审查后续建议 | 保留既有原脚本F2P证据；补完整核异常handler及错误组合回归。 |

## 已有原测试日志

- [buggy.stdout.log](../runtime/ibex_377/buggy.stdout.log)
- [buggy.stderr.log](../runtime/ibex_377/buggy.stderr.log)
- [reference.stdout.log](../runtime/ibex_377/reference.stdout.log)
- [reference.stderr.log](../runtime/ibex_377/reference.stderr.log)

## 原字段证据

`body` 字段内第7–7行：

```text
- This prevents strange behaviour caused by the lsu and controller
```

`fix_patch` 字段内第2–2行：

```text
index c959ce2ddb..2c08892e0e 100644
```

`tb_script` 字段内第111–111行：

```text
check(top->store_err_o == 0, "store_err asserted before second response", error_count);
```

`tb_script` 字段内第124–124行：

```text
check(top->store_err_o == 1, "store_err missing on second response", error_count);
```
