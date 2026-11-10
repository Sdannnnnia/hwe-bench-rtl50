# opentitan_8724

来源：[原PR](https://github.com/lowRISC/opentitan/pull/8724)；源数据第402行；分类 `RTL_LOGIC`。

保留理由：这里实际测完整 SPI core 的串行输出，七字节顺序和 CS 连续性都查，优先保留。

本地证据：**原测试待本地实测**。运行准备状态：待校准。

## 原始 HWE 题面

## Description
The OpenTitan SPI_HOST IP can drop transmitted data in segmented standard-mode write transactions when software queues consecutive segments and uses `CSAAT` (chip-select active after transfer) to keep chip-select asserted across segment boundaries.

## Affected Function
This affects the SPI_HOST finite-state machine and transmit segment-completion logic that determine when a write segment is finished and when the active-low chip-select signal (`CSB`) may be deasserted between segments.

## Expected Behavior
In a multi-segment SPI_HOST write transaction, each segment must transmit exactly its configured number of bytes before the controller advances to the next segment. If a non-final segment has `CSAAT=1`, `CSB` must remain asserted while the next segment starts, and `CSB` may deassert only after the final segment with `CSAAT=0` completes. For a three-segment transfer programmed for 1 byte, then 4 bytes, then 2 bytes, the SPI bus must emit all 7 bytes in order, and `CSB` must rise only once after the seventh byte.

## Actual Behavior
The controller can treat a segmented write transfer as complete one byte too early when handing off between back-to-back segments. In the failing pattern, the first 1-byte segment is transmitted, but the following 4-byte segment loses its fourth byte, so only 6 total bytes are sent before `CSB` is released.

## Trigger Condition
The bug is triggered by back-to-back SPI_HOST standard-mode write segments where a non-final segment sets `CSAAT=1` to keep `CSB` low across the boundary, and a later segment clears `CSAAT`. A concrete failing case is a 1-byte segment followed by a 4-byte segment and then a 2-byte segment.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #8643 原回归发现段尾字节遗漏；PR 修 last_read/last_write 与 CSBSwitch 两处。 |
| 触发过程 | 1字节 CSAAT→4字节 CSAAT→2字节最后段→packer/FSM段结束错位→漏字节或提早CS。 |
| 测试覆盖 | 从 posedge SCK 抽 SD bit 拼字节；验7字节完整值/顺序、CS无早释放且只升一次、active结束。 |
| 尚存缺口 | 只测 CPHA0 standard write、一个时钟分频，未覆盖read/其他speed/CS切换改动。script 优先TB_PASS需保留其完整日志。 |
| 环境真实性 | 真实 spi_host_core，包括 byte merge/select、shift register、FSM、packer；不是孤立FSM。用 core command/TX 接口，无force。 |
| 跨周期价值 | 高，多段边界、计数器与数据打包。 |
| 题面提示 | 中：给出三段长度和具体漏字节症状，内部实现仍需查。 |
| 原审查后续建议 | 双版本运行，扩长度边界并复用 read/CPHA1/不同chip-select回归。 |

## 原字段证据

`tb_script` 字段内第49–49行：

```text
spi_host_core #(
```

`tb_script` 字段内第78–78行：

```text
always @(posedge sck_o) begin
```

`tb_script` 字段内第153–153行：

```text
foreach (expected_bytes[i]) begin
```

`tb_script` 字段内第159–159行：

```text
if (csb_rise_count != 1) begin
```
