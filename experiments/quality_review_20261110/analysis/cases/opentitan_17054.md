# opentitan_17054

来源：[原PR](https://github.com/lowRISC/opentitan/pull/17054)；源数据第410行；分类 `RTL_INTERFACE`。

保留理由：真实回归中的read/RMA交叠，题面主要讲症状，根因藏在更下层buffer控制，调试价值很高。

本地证据：**原测试待本地实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

## Description
The bug affects the OpenTitan flash controller (`flash_ctrl`) during the handoff between a controller-initiated flash read and a life cycle RMA (Return Merchandise Authorization) request. If an RMA request arrives while a controller read is still active, the controller read path can fail to retire cleanly and block forward progress of the RMA sequence.

## Trigger Condition
A controller-initiated flash read is already in progress, and an RMA request is asserted before that read operation has completed.

## Expected Behavior
When an RMA request is issued during an active controller read, the flash controller must allow the in-flight read to complete, and the RMA flow must advance into its erase phase without hanging.

## Actual Behavior
In the failing scenario, issuing an RMA request during a controller read leaves the controller read path stuck. The controller read does not complete, and the RMA sequence fails to advance into its erase phase, so the operation times out.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #16979含原seed及读未完时RMA卡死证据；PR解释buffer enable变更同拍接新read导致已命中buffer无法响应。 |
| 触发过程 | 初始化flash→控制器读FIFO_DEPTH数据→active后10拍发RMA→要求读完成且RMA进入erase wait。 |
| 测试覆盖 | read_done和rma_progressed，超时限制；在原完整flash_ctrl UVM环境运行。 |
| 尚存缺口 | 只确认进入StRmaEraseWait，未确认整个擦除完成/读数据正确；依赖基类scoreboard是否仍检查数据，静态片段未证实。单seed不保证各种buffer碰撞。 |
| 环境真实性 | backdoor只初始化flash存储，RMA与read走真实控制路径；等待内部状态为观测/对齐，无force状态。 |
| 跨周期价值 | 高：read流水、buffer状态、RMA三方交互。 |
| 题面提示 | 中：给IP与交叠场景，未给flash_phy_rd buf_en根因。 |
| 原审查后续建议 | 优先校准原HWE并恢复原issue seed对照；检查波形确实命中buffer-enable切换窗口，运行正常read及RMA完整流程。 |

## 原字段证据

`body` 字段内第1–3行：

```text
- fixes #16979
- In the previou design, the buffer enable was allowed to change whenever the read pipeline was idle.  This however does not account for the scenario where on the same cycle there is a new flash read request.  In the buffer enable were changed from 1->0, it would allow a new request t
```

`tb_script` 字段内第34–76行：

```text
    init_flash_regions();

    `DV_CHECK_RANDOMIZE_FATAL(this)
    flash_op.op = FlashOpRead;
    flash_op.partition = FlashPartData;
    flash_op.num_words = FIFO_DEPTH;

    cfg.flash_mem_bkdr_init(flash_op.partition, FlashMemInitInvalidate);
    cfg.flash_mem_bkdr_write(.flash_op(flash_op), .sche
```

`fix_patch` 字段内第18–40行：

```text
+  // When buffer enable changes, we want to hold off new requests
+  // until the request is absorbed.  buf_en_q is allowed to change
+  // only when the entire read pipeline is idle, however, during that
+  // same cycle there could be a new incoming request.
+  //
+  // We back pressure here inst
```
