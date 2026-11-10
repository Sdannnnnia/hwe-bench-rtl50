# opentitan_23432

来源：[原PR](https://github.com/lowRISC/opentitan/pull/23432)；源数据第185行；分类 `RTL_LOGIC`。

保留理由：原issue报告真实HMAC上下文切换卡死，定向测试保留状态机自然演进；SHA完成由TB模拟，须限制结论范围。

本地证据：**原测试待本地实测**。运行准备状态：待校准。

## 原始 HWE 题面

## Description
During save-and-restore or context-switching use of the OpenTitan HMAC IP, software may stop one HMAC stream, save its state, and then start a different stream. In the reported flow, Stream A is stopped, Stream B is started, and after roughly 1000 bytes Stream B stops making forward progress: the message input FIFO (`MSG_FIFO`) fills and the operation eventually times out. In this failure mode, the HMAC core still behaves as if the previous context is active when the second `start` command arrives.

## Affected Function
The bug is in the HMAC IP's `hmac_core` main state machine, specifically the logic that handles a `stop` request, returns the core to an idle state, and accepts a later `start` during save-and-restore or context-switch flows.

## Expected Behavior
After software issues `stop` for an active HMAC context, the core should finish the current message block, become idle once that block's hash operation completes, and then accept a later `start` for a different context. In that situation, the new `start` must raise the internal `sha_hash_start_o` start pulse and processing of the new stream must begin so that `MSG_FIFO` continues to drain.

## Actual Behavior
If `stop` is issued near the end of a later message block while the first context is still in the inner HMAC message-processing phase, the core may fail to return to its idle state after the current block completes. A subsequent `start` for another context then does not raise `sha_hash_start_o`, so the new stream never actually begins and its `MSG_FIFO` stops draining.

## Trigger Condition
This occurs in HMAC save-and-restore or context-switching flows that stop one stream and start another while the first stream is still processing the inner part of a non-first SHA-2 message block. Reported examples include interleaving HMAC-384 and HMAC-256 streams, and the failure is reproducible in a long SHA-256/HMAC message when `stop` is asserted close to the end of a later block.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #23352明确A stop/B start后FIFO满；PR讨论SAR FSM idle/start修改，原作者注明仍待充分回归。 |
| 触发过程 | 启动HMAC→第二块近结束txcount=992→stop→模拟SHA done→等待Idle→新start应发sha_hash_start。 |
| 测试覆盖 | 自然到达指定停止窗口、限时回Idle、重新发start脉冲。 |
| 尚存缺口 | 没有真实SHA运算/digest、上下文保存恢复、不同digest_size；checker直接依赖st_q编码，等价重编码可能被误判。 |
| 环境真实性 | 只实例化真实hmac_core及原package，SHA/FIFO端口由TB模型驱动；无内部force；done时序固定，真实性需对照完整SHA。 |
| 跨周期价值 | 高：跨message block与上下文切换；当前验收为控制级。 |
| 题面提示 | 很高：题面点出hmac_core FSM、停止后回idle及sha_hash_start_o，原issue本身也有定位。 |
| 原审查后续建议 | 双版本复现，并用原SAR回归补真实SHA与两种上下文；将idle输出/新数据进展作为补充验收，减少对状态编码的约束。 |

## 原字段证据

`body` 字段内第1–3行：

```text
This implements RTL changes to the HMAC FSM to handle context switching (transitions to `StDone` to wait on hash result, and then `StIdle` from where every context ought to start/continue) and aligns triggering of idle and done. With this change, the SAR smoke test passes on @martin-velay's SAR DV b
```

`resolved_issues` 字段内第1–1行：

```text
[{"org": "lowRISC", "repo": "opentitan", "number": 23352, "state": "closed", "title": "[hmac, rtl] Reset hmac_core FSM to Idle after stop", "body": "### Description\n\nI am trying to interleave two HMAC streams. Namely:\r\n\r\n- Stream A (HMAC-384) starts and feeds some of its messages.\r\n- Stream 
```

`tb_script` 字段内第112–145行：

```text
  task automatic pulse_sha_done;
    sha_hash_done_i = 1'b1;
    #1;
    @(posedge clk_i);
    #1;
    sha_hash_done_i = 1'b0;
  endtask

  task automatic wait_for_pre_stop_point;
    int cycles;
    cycles = 0;
    while (!(dut.st_q == 3'd2 && dut.round_q == 1'b0 && dut.txcount == 64'd992)) begin
 
```

`tb_script` 字段内第172–194行：

```text
    pulse_start();
    wait_for_pre_stop_point();
    $display("INFO pre-stop point: st=%0d txcount=%0d idle=%0b", dut.st_q, dut.txcount, idle_o);

    pulse_stop();
    $display("INFO stop observed: st=%0d txcount=%0d idle=%0b", dut.st_q, dut.txcount, idle_o);

    tick(1);
    pulse_sha_done();
  
```
