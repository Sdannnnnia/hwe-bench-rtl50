# opentitan_24771

来源：[原PR](https://github.com/lowRISC/opentitan/pull/24771)；源数据第178行；分类 `RTL_LOGIC`。

保留理由：真实 SHA 计算/停止相遇导致卡死，已有历史改编测试证据；原 HWE 测试仍待本地核验。

本地证据：**仅历史改编证据；原测试待实测**。运行准备状态：待校准。

## 原始 HWE 题面

## Description
The OpenTitan Hash-based Message Authentication Code (HMAC) IP can hang while finalizing a SHA-256 hash when software writes the last message word into the HMAC message FIFO, waits briefly, and only then issues `HMAC_CMD_HASH_STOP_BIT`, the command that tells the hardware that no more message data is coming. The affected functionality is the SHA-2 finalization path inside the HMAC IP.

## Expected Behavior
After the last message word has been accepted, issuing `HMAC_CMD_HASH_STOP_BIT` after a short delay must still finalize the pending message block, report that the hash operation is complete, and return the HMAC IP to idle. In software-visible terms, the idle bit in `HMAC.STATUS` (`hmac_idle`) must become set again instead of remaining cleared. This must also hold when the message length is exactly one full 512-bit SHA-256 block.

## Actual Behavior
With a short delay between the final FIFO write and `HMAC_CMD_HASH_STOP_BIT`, the hash operation can remain stuck in a non-idle state. Completion is never reported, `HMAC.STATUS.hmac_idle` stays cleared, and software waiting for the HMAC hardware to become idle can block indefinitely.

## Trigger Condition
This occurs when a block-aligned SHA-256 message is written to the HMAC message FIFO, the final 32-bit word completes the last 512-bit block, no further message words are written, and `HMAC_CMD_HASH_STOP_BIT` is issued only after a small delay such as interrupt latency.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #24767 给软件最后 FIFO write 后短延迟 stop 永久非idle；本地 HMAC guide 亦记录该 bug/workaround，但文档快照含后续 workaround，需固定版本。 |
| 触发过程 | 16个word填满512bit块→SHA轮运算完成/digest更新→稍后stop→FIFO状态遗漏完成→无法done/idle。 |
| 测试覆盖 | 真实 prim_sha2+pad；测试给16word、延迟70拍stop，200拍内要求hash_done曾出现且idle。 |
| 尚存缺口 | 不比较digest值，也不验digest_on_blk/continue/process；固定done/idle假修复需其他模式/known digest拦住。原TB部分握手循环无全局watchdog，运行器要外部超时。 |
| 环境真实性 | 真实运算数据通路，MultimodeEn=0/SHA256；直接prim接口，未覆盖HMAC CSR。历史改编测试增加了观测和延迟参数，其结果与原HWE整脚本运行分开记录。 |
| 跨周期价值 | 很高，数据输入、轮计算和异步软件终止三个阶段。 |
| 题面提示 | 中：给出stop延迟/块对齐症状，没有在题面给具体FIFO状态名。 |
| 原审查后续建议 | 核验原HWE脚本的运行结果；加known digest与continue/process正常回归。 |

## 原字段证据

`tb_script` 字段内第131–131行：

```text
repeat (70) @(posedge clk_i);
```

`tb_script` 字段内第136–136行：

```text
if (saw_hash_done && idle_o) begin
```

`fix_patch` 字段内第20–20行：

```text
+  logic update_digest_q, update_digest_d;
```

`body` 字段内第2–2行：

```text
- Listen to msg_feed_complete when in FifoLoadFromFifo state to move into FifoIdle state.
```
