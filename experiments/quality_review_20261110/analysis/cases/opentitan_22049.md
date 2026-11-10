# opentitan_22049

来源：[原PR](https://github.com/lowRISC/opentitan/pull/22049)；源数据第197行；分类 `RTL_LOGIC`。

保留理由：NAK后暂停、软件清除后恢复都有观察，适合协议恢复；原PR也带新功能，按NAK暂停子问题定义范围。

本地证据：**原测试待本地实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

## Description
The OpenTitan I2C IP mishandles an unexpected negative acknowledgment (NACK) in host mode when it is acting as a controller-transmitter in Byte-Formatted Programming Mode, where software queues host format commands in the format FIFO through FDATA entries. If the target acknowledges the address byte but then NACKs a transmitted data byte, the controller records the NACK but can still advance to the next queued format entry instead of pausing at the failed byte.

## Expected Behavior
After an unexpected NACK in this host-mode transmit path, the I2C controller must stop consuming additional FDATA / format FIFO entries and keep the active transaction paused until software clears the pending `nak` interrupt. While the NACK is pending, the controller must remain in an active host transaction rather than returning to host-idle state, and queued format entries must remain in the FIFO instead of being drained.

## Actual Behavior
The current implementation raises the `nak` interrupt but continues processing the queued transfer. In the reproduced case where the address phase is ACKed and the first queued data byte is NACKed, later queued bytes can still be consumed and the transfer can continue before software clears the interrupt.

## Affected Function
This affects the OpenTitan I2C IP's host-mode byte-formatting controller finite state machine (FSM), specifically the logic that handles ACK/NACK results after transmitting a byte and decides whether to pop the next format FIFO entry.

## Trigger Condition
The bug is triggered when the I2C block is operating in host mode as a controller-transmitter, software has queued multiple FDATA entries for a write transaction, the target acknowledges the address byte, and the target then NACKs the first queued data byte before software has cleared the pending NACK condition.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #18917要求NAK后等待软件；PR明确W1C解除暂停并补文档，同时新增timeout功能不在当前子测试范围内。 |
| 触发过程 | host写地址被ACK→首data被NAK→等待1000拍→FIFO仍非空且host仍active→软件clear NAK→回idle。 |
| 测试覆盖 | nak中断、fmt_lvl>0/hostidle=0/fmtempty=0以及清除后idle，沿用原UVM环境。 |
| 尚存缺口 | 只要求FIFO还有数据，没有断言NAK期间深度完全不变；若偷偷多消费一个但剩一个可能过。NAKOK、timeout、精确恢复字节序列未由新增checker覆盖。 |
| 环境真实性 | I2C agent新增真实引脚NAK能力；backdoor仅读FIFO深度，未force状态。 |
| 跨周期价值 | 高：外设拒绝、FIFO进度、软件处理中断交叠。 |
| 题面提示 | 高：说明FSM应暂停/何时pop，但主要是外部协议要求。 |
| 原审查后续建议 | 双版本校准；在NAK瞬间与等待期逐次比较FIFO深度、串行字节序列，并跑NAKOK和无NAK回归；单独记录新timeout功能未评测。 |

## 原字段证据

`body` 字段内第1–7行：

```text
If the I2C bus NAKs any of our transfers when operating as a Controller-Transmitter in Byte-Formatted Programming Mode, the current behaviour is to proceed to the next FDATA entry as normal, disregarding the NAK entirely. The only side-effect of this event is the block raising the 'nak' interrupt (t
```

`tb_script` 字段内第124–139行：

```text
    forever begin
      p_sequencer.req_analysis_fifo.get(req);
      if (req.drv_type == RdData) begin
        `DV_CHECK_STD_RANDOMIZE_FATAL(rdata)
        req.rdata = rdata;
      end
      if (req.drv_type == DevAck) begin
        ack_count++;
        if (ack_count == 2) begin
          `uvm_info
```

`tb_script` 字段内第234–248行：

```text
    `DV_WAIT(cfg.intr_vif.pins[Nak], "Expected the DUT to raise the nak interrupt.",
             cfg.long_spinwait_timeout_ns, `gfn)
    cfg.clk_rst_vif.wait_clks(1_000);

    csr_rd(.ptr(ral.host_fifo_status.fmtlvl), .value(fmt_lvl), .backdoor(1'b1));
    csr_rd(.ptr(ral.status.hostidle), .value(h
```
