# opentitan_12473

来源：[原PR](https://github.com/lowRISC/opentitan/pull/12473)；源数据第243行；分类 `RTL_INTERFACE`。

保留理由：真实接口相互等待，测试同时验请求到达和完成，保留。

本地证据：**原测试待本地实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

## Description
The bug is in OpenTitan's flash controller (`flash_ctrl`), specifically in `flash_phy_core`, the block that arbitrates between an external host-side flash access and an internal controller-initiated flash operation before forwarding a request to the downstream flash macro.

## Expected Behavior
When the controller side issues an erase request while the `flash_phy_core` read stage is idle and there is no competing host-side request, `flash_phy_core` must grant that controller request and forward the corresponding erase request to the flash macro. The flash macro's acknowledge (`ack`) signal may legally remain low while idle and only assert after a request is presented, so controller-side progress must not depend on `ack` already being asserted before the request is sent.

## Actual Behavior
A controller-originated erase request can deadlock inside `flash_phy_core`. The controller request waits for a grant/readiness condition that is itself derived from the downstream flash macro's `ack`, while the flash macro waits to see the erase request before asserting `ack`. As a result, the erase request never reaches the flash macro and the controller operation never completes.

## Affected Function
The affected functionality is the `flash_ctrl` `flash_phy_core` arbitration and request handoff for controller-side erase operations to the downstream flash macro.

## Trigger Conditions
The failure occurs when a controller-side erase operation, including page erase, is issued while the `flash_phy_core` read stage is idle, no host-side request is competing for arbitration, and the downstream flash macro uses a request/acknowledge handshake where `ack` is asserted only after a request is presented rather than being held high while idle.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | 原 closed-source 集成 issue #12381 报 ack 等 req、req 等 ack 循环；PR 明确 downstream ack 空闲可低。 |
| 触发过程 | controller erase→arbiter 依赖 read ready→read ready 依赖 macro ack→macro 等 erase req→互等。 |
| 测试覆盖 | 实际 flash_phy_core/依赖 RTL；macro 模型只在 req 后 ack 并延迟 done；检查 erase req、done、错误输出。 |
| 尚存缺口 | 没验真实 Flash 存储结果、host 竞争及 program/read 回归；脚本失败末尾 exit rc 有可能 rc=0，接入时须同时解析 FAIL marker。 |
| 环境真实性 | 替代的是闭源宏接口 responder，符合该 issue 关心的 ack 合法时序；关闭了两处 security alert SVA，与当前握手目标分开记录。 |
| 跨周期价值 | 高，跨模块流控死锁。 |
| 题面提示 | 高：题面已完整解释 grant/ack circular dependency。 |
| 原审查后续建议 | 运行双版本，保留 FAIL marker 判定；加宏 ack 延迟和 host/controller 正常回归。 |

## 原字段证据

`body` 字段内第12–12行：

```text
the downstream macro does not always keep ack asserted when idle (in
```

`tb_script` 字段内第166–166行：

```text
prim_flash_rsp_i.ack = macro_req;
```

`tb_script` 字段内第242–242行：

```text
if (!saw_erase_done) begin
```

`tb_script` 字段内第154–154行：

```text
defparam dut.u_state_regs.EnableAlertTriggerSVA = 0;
```
