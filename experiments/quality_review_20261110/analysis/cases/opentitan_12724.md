# opentitan_12724

来源：[原PR](https://github.com/lowRISC/opentitan/pull/12724)；源数据第239行；分类 `RTL_TIMING_SYNC`。

保留理由：前一次事务的通知污染后一次事务，测试确实读两次 opcode 验身份。

本地证据：**原测试待本地实测**。运行准备状态：待校准。

## 原始 HWE 题面

## Description
In the OpenTitan SPI Device IP's flash Passthrough mode, where selected SPI flash commands are forwarded to flash but also uploaded to software, the command upload path does not always preserve transaction boundaries. After software consumes one uploaded command, later bus activity can leave the upload notification associated with the old transaction instead of the next completed uploaded transaction.

## Expected Behavior
Each uploaded SPI flash transaction must be reported exactly once after chip-select (CSb) is deasserted for that transaction. Once software reads an opcode from `UPLOAD_CMDFIFO` and clears the corresponding `upload_cmdfifo_not_empty` interrupt, later non-uploaded transactions such as `READ_STATUS` must not re-assert that interrupt or expose a stale command entry. When the next uploaded transaction completes, software must receive a new `upload_cmdfifo_not_empty` event, and reading `UPLOAD_CMDFIFO` must return the opcode for that new transaction.

## Actual Behavior
If software first consumes an uploaded opcode-only command such as `CHIP_ERASE`, intervening hardware-handled `READ_STATUS` transactions can leave the upload indication tied to the earlier command. The next wait for `upload_cmdfifo_not_empty` may therefore wake on a stale event, and reading `UPLOAD_CMDFIFO` can return `0x00` or the previous opcode instead of the opcode for the next uploaded command. In a later uploaded `PAGE_PROGRAM` transaction, software can therefore miss the new upload or read the stale erase opcode rather than `PAGE_PROGRAM`.

## Affected Function
The affected logic is the SPI Device IP flash command upload path in Passthrough mode, specifically the software-visible command reporting mechanism through `UPLOAD_CMDFIFO` and `upload_cmdfifo_not_empty`.

## Trigger Condition
This occurs when an uploaded command that ends after the opcode phase, such as `CHIP_ERASE`, is followed by one or more non-uploaded `READ_STATUS` polling transactions, and then another uploaded command such as `PAGE_PROGRAM`. The failure depends on software having already read the earlier uploaded command and cleared its interrupt before the later uploaded command arrives.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #11871 要求上传 FIFO/事务边界保持一致；PR 说明清事件依赖软件速度而非 CSb 边界。 |
| 触发过程 | CHIP_ERASE 上传→软件取走清中断→READ_STATUS 轮询→PAGE_PROGRAM 上传→第二次通知/命令身份。 |
| 测试覆盖 | 通过 TL 读 CMDFIFO 并明确比较 ChipErase 和 PageProgram，第二次 wait 可发现漏通知。 |
| 尚存缺口 | 仅打印第一笔取走后 FIFO 非空，未作为失败；完整 host 序列与 TEST PASSED CHECKS 来源需查看 pre_dv 源。未验地址/数据归属。 |
| 环境真实性 | 改写 pre_dv host/SW 测试程序，实际 SPI/TL 接口；无 DUT 内部 force。PR 给出 SYS/SCK 比率约束，应固定合法比率。 |
| 跨周期价值 | 高，跨事务状态、双时钟和软件清中断交叠。 |
| 题面提示 | 中高：题面给出完整复现序列和 stale event 判断。 |
| 原审查后续建议 | 运行原 pre_dv 双版本，核 host 序列和时钟比，扩一组正常 upload/非 upload 对照。 |

## 原字段证据

`body` 字段内第11–11行：

```text
SYS_CLK should not be 3 times slower than the SCK to correctly generate
```

`tb_script` 字段内第59–59行：

```text
if (opcode != spi_device_pkg::CmdChipErase) begin
```

`tb_script` 字段内第100–100行：

```text
if (opcode != spi_device_pkg::CmdPageProgram) begin
```

`tb_script` 字段内第77–77行：

```text
$display("SW: CMDFIFO not empty after fetching: %2d", tl_rdata[4:0]);
```
