# opentitan_8366

来源：[原PR](https://github.com/lowRISC/opentitan/pull/8366)；源数据第297行；分类 `RTL_INTERFACE`。

保留理由：软件改配置打断进行中握手，真实控制器和正常完成数据都有检查。

本地证据：**原测试待本地实测**。运行准备状态：待校准。

## 原始 HWE 题面

## Description
The Key Manager (keymgr) obtains fresh reseed entropy from the Entropy Distribution Network (EDN). In the keymgr reseed controller, the EDN request signal is derived from the live software-programmable `reseed_interval_i` value, so changing that interval while a reseed transaction is pending can alter the request in the middle of the EDN handshake.

## Affected Function
This affects the Key Manager IP's reseed controller (`keymgr_reseed_ctrl`), which issues EDN reseed requests for keymgr.

## Expected Behavior
Once keymgr starts an EDN reseed transaction, the EDN request for that transaction must remain asserted until the corresponding EDN acknowledge and entropy data are returned and the reseed completes. Software writes to `reseed_interval_i` should only influence when a future automatic reseed is due; they must not change the state of a request that is already in flight.

## Actual Behavior
Because the request depends on the current `reseed_interval_i`, software can influence EDN request timing by rewriting that interval. In particular, a request that has already been asserted can deassert before the EDN response arrives, violating the EDN handshake protocol.

## Trigger Condition
The failure occurs when keymgr has asserted an EDN reseed request and software updates `reseed_interval_i` before the EDN response returns. One observed case is increasing the interval after the request goes high, which causes the outstanding request to drop before reseeding finishes.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #8360 明确 live reseed_interval 可撤掉未完成 EDN 请求；PR 要求任何软件改写也遵守握手。 |
| 触发过程 | 发 reseed→内部 req 锁定事务→软件改 interval→req 旧逻辑消失→熵握手/seed 完成受影响。 |
| 测试覆盖 | 观察 req 持续到 seed_en、计数器无错误、完成时间、完整 64bit seed 值。 |
| 尚存缺口 | 使用同一时钟连接 clk_i/clk_edn_i；响应立即 ack；未验异步延迟/软件自动周期 reseed 多次。内部 req 路径耦合实现。 |
| 环境真实性 | prim_buf/flop/2sync shims 实际封装上游 prim_generic_*，并非随意简化同步器。接口驱动，无内部 force。 |
| 跨周期价值 | 高，事务状态与软件可变配置交叠；现测试不证明异步 CDC。 |
| 题面提示 | 高：题面指出 req 由 live interval 推导，已经定位机制。 |
| 原审查后续建议 | 双版本运行，保留 generic 原语映射；延迟 ack、独立 EDN 时钟、自动 reseed 回归。 |

## 原字段证据

`tb_script` 字段内第57–57行：

```text
prim_generic_flop_2sync #(
```

`tb_script` 字段内第75–75行：

```text
wire clk_edn_i = clk_i;
```

`tb_script` 字段内第125–125行：

```text
$fatal(1, "edn_req dropped before seed_en_o asserted");
```

`tb_script` 字段内第152–152行：

```text
$fatal(1, "unexpected seed value: %h", seed_o);
```
