# opentitan_23807

来源：[原PR](https://github.com/lowRISC/opentitan/pull/23807)；源数据第416行；分类 `RTL_INTERFACE`。

保留理由：被拒绝事务污染下一笔事务，现有测试同时查协议响应和后续数据，很适合。

本地证据：**原测试待本地实测**。运行准备状态：待校准。

## 原始 HWE 题面

## Description
The bug is in the OpenTitan USB device IP, specifically the full-speed non-isochronous OUT packet engine (`usb_fs_nb_out_pe`) and the receive-side bookkeeping in `usbdev_usbif`. When the USB device responds to a host-to-device OUT transaction with `STALL`, the rejected packet is not rolled back internally. Receive-side state from that rejected OUT transaction can remain allocated even though the USB host was told that the transfer failed.

## Expected Behavior
A `STALL` response to an OUT transaction means the packet was rejected and must not consume receive state. After a stalled OUT transaction, the USB device must discard the rejected packet's bookkeeping, reset the receive-side byte count for that packet, and be ready to accept the next receive transaction. In particular, if control endpoint 0 (EP0) stalls a long OUT transaction, the following SETUP packet must still be acknowledged and its receive FIFO (RX FIFO) entry must match the actual SETUP packet length and payload.

## Actual Behavior
If a non-isochronous OUT transaction is stalled, the receive bookkeeping is not rolled back. For OUT packets 62 bytes or longer, the byte-counting logic in `usbdev_usbif` is left uncleared before the next receive transaction arrives. As a result, the next SETUP packet, or another OUT packet, can be recorded with the wrong length in the RX FIFO and may not be captured correctly; once this happens, the true size of the affected packet cannot be recovered from the RX FIFO entry.

## Trigger Conditions
This occurs when an endpoint is configured to return `STALL` for a non-isochronous OUT transaction, the device receives a long OUT packet (reported starting at 62 bytes, including a 64-byte OUT packet), and another receive transaction follows immediately. The benchmarked case is control endpoint 0 (EP0): a 64-byte OUT packet is stalled, and the very next SETUP packet should still be accepted correctly.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | 原 issue #23806 描述 STALL 后 RX 长度计数未回退；patch 明确 rejected OUT rollback。以 resolved issue 原始描述和 USB 拒收语义为依据。 |
| 触发过程 | EP0 STALL 64字节 OUT→旧内部 bytecount 残留→下一 SETUP→ACK 后 RX FIFO 长度/数据错误。 |
| 测试覆盖 | 显式 STALL、后续 ACK、check_rx_packet(expected payload/buffer)；比仅等完成更强。 |
| 尚存缺口 | check_rx_packet 实现需随原 DV 冻结，确认 length 与 payload 都比较；目前一个长包/endpoint/seed，缺非STALL对照。 |
| 环境真实性 | 真实 usbdev UVM，标准接口和CSR配置；原脚本无 force/替身，prepare为空需准备base。 |
| 跨周期价值 | 很高，跨事务污染和接收缓冲分配。 |
| 题面提示 | 高：题面点名未rollback和 bytecount 残留，但问题仍跨两事务。 |
| 原审查后续建议 | 原测试双版本运行，核 check_rx_packet 的 length 检查并复用短/长 OUT、正常 SETUP。 |

## 原字段证据

`tb_script` 字段内第34–34行：

```text
send_prnd_out_packet(ep_default, PidTypeData0, .randomize_length(1'b0), .num_of_bytes(64));
```

`tb_script` 字段内第35–35行：

```text
check_response_matches(PidTypeStall);
```

`tb_script` 字段内第40–40行：

```text
check_rx_packet(ep_default, .setup(1'b1), .exp_buffer_id(setup_buffer_id),
```

`fix_patch` 字段内第9–9行：

```text
+            rollback_data = 1'b1; // Packet not accepted
```
