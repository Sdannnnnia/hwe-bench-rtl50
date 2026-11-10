# opentitan_18941

来源：[原PR](https://github.com/lowRISC/opentitan/pull/18941)；源数据第412行；分类 `RTL_INTERFACE`。

保留理由：真实 suspend/resume 后新包被误当重传，局部测试比较了提交而不只是 ACK。

本地证据：**原测试待本地实测**。运行准备状态：待校准。

## 原始 HWE 题面

## Description
In the OpenTitan USB device (USBDEV) IP, the receive-side data-toggle state for non-control OUT endpoints is cleared when the USB link becomes inactive during suspend. This state is used by the USB device OUT packet engine to distinguish a new packet from a retransmission. As a result, after suspend and resume, the first new OUT packet can be acknowledged but not committed to the endpoint buffer.

## Expected Behavior
Suspend and resume, without a USB bus reset, must preserve the current data-toggle value for each non-control OUT endpoint. If an endpoint successfully accepts a DATA0 packet before suspend, it must still expect DATA1 after resume. A valid DATA1 packet received after resume must be treated as new data, written into the endpoint buffer, and advance the endpoint's data-toggle state.

## Trigger Condition
The failure occurs on a non-control OUT endpoint after it has already accepted a DATA0 packet, the USB link then enters the inactive/suspended state, and the link later resumes without a bus reset. In that scenario, a host that correctly continues with DATA1 can have the first post-resume OUT packet acknowledged by the device but effectively dropped.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #18940 有 Linux/libusb 实际丢流量复现及 DATA toggle 保持解释；PR 只修 suspend，deep sleep 保存恢复另议。 |
| 触发过程 | 先提交 DATA0→link_active低模拟suspend→resume不reset→DATA1应提交→旧实现回退丢数据。 |
| 测试覆盖 | 验 token选endpoint、payload值、DATA0和DATA1的 commit/rollback/ACK；足以区分“ACK但丢弃”。 |
| 尚存缺口 | send_out_transfer 具备 expect_commit=false 分支却未调用；恒接收新包的假修复需 duplicate DATA1/real reset 对照拦住。 |
| 环境真实性 | 真实 OUT packet engine，绕过 PHY/CRC用已解析合法包接口；2 endpoint/32byte 参数、当前1字节 payload。 |
| 跨周期价值 | 高，跨事务状态保持；修复很短不降低触发价值。 |
| 题面提示 | 高：题面直接揭示 suspend 清 data toggle，容易定位单行条件。 |
| 原审查后续建议 | 双版本运行，增加重传应回退、USB bus reset应清toggle对照，标明只覆盖suspend而非deep sleep。 |

## 原字段证据

`body` 字段内第1–1行：

```text
The link_active_i term was misplaced, and data toggles should not be cleared in suspended state. In fact, they should be retained, and usbdev will need to give software greater visibility and control, so it can save / re
```

`tb_script` 字段内第220–220行：

```text
send_out_transfer(UsbPidData0, 1'b1);
```

`tb_script` 字段内第234–234行：

```text
send_out_transfer(UsbPidData1, 1'b1);
```

`tb_script` 字段内第186–186行：

```text
if (expect_commit) begin
```
