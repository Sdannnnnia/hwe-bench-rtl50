# opentitan_20437

来源：[原PR](https://github.com/lowRISC/opentitan/pull/20437)；源数据第212行；分类 `RTL_INTERFACE`。

保留理由：两个真实FSM都测abort后回idle和再启动，局部恢复有验收；完整TL未返回响应的恢复尚未覆盖。

本地证据：**原测试待本地实测**。运行准备状态：待校准。

## 原始 HWE 题面

## Description
OpenTitan's mailbox (mbx) IP carries request and response traffic between the SoC and the Root of Trust (RoT). The inbound mailbox accepts request data written by the SoC, and the outbound mailbox presents response data for the SoC to read. After a communication failure or timeout on this path, RoT firmware must be able to acknowledge the abort condition and use that acknowledgement as a firmware-driven reset of the mailbox control logic, even when the SoC cannot complete the normal abort handshake first.

## Affected Function
The affected logic is the mbx IP's inbound and outbound mailbox control state machines, including the outbound Ready indication during abort recovery.

## Expected Behavior
When RoT firmware acknowledges the abort condition, the mailbox must immediately return to its idle state regardless of which mailbox FSM state is currently active. This must work while the inbound mailbox is already in its write phase and while the outbound mailbox is already in its read/response phase. For an outbound transaction, the same abort acknowledgement must also clear the Ready indication for the aborted response. After that reset, the mailbox must be able to start a new inbound or outbound transaction normally.

## Actual Behavior
In the current implementation, an abort acknowledgement from RoT firmware is not honored once the mailbox FSM has already left idle. If the inbound mailbox is already accepting write data, or the outbound mailbox is already in its read/response phase, the FSM can remain in its active state instead of returning to idle. On the outbound side, Ready can also remain asserted for an aborted response. As a result, the aborted transaction is not fully cleared and the mailbox does not reliably recover for the next transaction.

## Trigger Condition
This bug is triggered when a mailbox transaction is already active and RoT firmware acknowledges the abort condition during recovery from a communication failure or timeout. It also occurs when that acknowledgement is used as a firmware-driven reset without a preceding SoC-side abort request, which is needed when the SoC is stalled and cannot complete the explicit abort sequence.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | PR body详细说明FW强制abort复位需求；resolved_issues误链到opentitan#708（HMAC命名），真实链接为opentitan-integrated#708，不能引用错链作为依据。 |
| 触发过程 | inbound进入write→host abort ack→idle→重新write；outbound进入read→host abort ack→清ready→重新read。 |
| 测试覆盖 | 两FSM活动/空闲输出及outbound ready更新；FAIL用display+finish，但shell检查PASS且无FAIL，因此有有效失败传播。 |
| 尚存缺口 | 只实例化mbx_fsm；补丁涉及pending、outstanding计数、迟到TL响应均未测试；FSM状态恢复不等于完整mailbox可用。 |
| 环境真实性 | 通过FSM端口驱动、真实primitive，SYNTHESIS使部分断言关闭；没有TL总线和存储数据路径。 |
| 跨周期价值 | 中：局部状态恢复清晰；完整跨总线bug复杂度大于现测。 |
| 题面提示 | 高：题面说任意状态优先处理ack回idle；原body本身给设计方案。 |
| 原审查后续建议 | 校准原HWE两版，再用完整mbx带未完成请求及迟到响应验收，保留正常交易；元数据注明跨repo issue误解析。 |

## 原字段证据

`body` 字段内第20–32行：

```text
**Commit 1:** Introduces a reset of the following internal state when the RoT FW ('host') acknowledges an Abort condition.

- u_ombx.u_req_state <- TL-UL read request
- u_ombx.u_pop_entry <- ditto
- u_ombx.u_pending <- SoC side Write Data Register stall
- u_imbx.u_req_state <- TL-UL write request
- 
```

`resolved_issues` 字段内第1–1行：

```text
[{"org": "lowRISC", "repo": "opentitan", "number": 708, "state": "closed", "title": "[hmac] Revise localparams to have unique and meaningful names", "body": "The issue #701 is reported by @imphil\r\n\r\nProblem:\r\n\r\n    Previous version of `hmac_pkg.sv` has duplicated names `k`. `k` is\r\n    use
```

`tb_script` 字段内第170–218行：

```text
    ib_writer_write_valid = 1'b1;
    step();
    ib_writer_write_valid = 1'b0;

    if (ib_mbx_write !== 1'b1 || ib_mbx_empty !== 1'b0) begin
      fail("Inbound FSM did not enter write state");
    end

    ib_hostif_abort_ack = 1'b1;
    step();
    if (ib_mbx_empty !== 1'b1 || ib_mbx_write !== 1
```

`tb_script` 字段内第239–246行：

```text
"${TB_DIR}/simv" -l "${RUN_LOG}"
sim_rc=$?

if [[ "${sim_rc}" -eq 0 ]] && grep -Eq '^TB_STATUS: PASS$' "${RUN_LOG}" &&
   ! grep -Eq '^TB_STATUS: FAIL:' "${RUN_LOG}"; then
  run_rc=0
else
  run_rc=1
```
