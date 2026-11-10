# opentitan_15269

来源：[原PR](https://github.com/lowRISC/opentitan/pull/15269)；源数据第231行；分类 `RTL_TIMING_SYNC`。

保留理由：补查固定历史版本的原UVM scoreboard，确认按地址低位比较TPM返回字节；原测试具备数据检查，纳入候选。

本地证据：**原测试待本地实测**。运行准备状态：待校准。

## 原始 HWE 题面

## Description
A bug exists in the SPI Device IP's Trusted Platform Module (TPM) read path for TPM hardware-returned registers. When the SPI Device is configured in TPM FIFO mode and the SPI host performs an unaligned TPM read, the device can use the previous byte address instead of the requested byte address.

## Affected Function
The affected functionality is the SPI Device IP's TPM hardware-register read handling in TPM FIFO mode, including reads of hardware-returned registers such as `TPM_RID`.

## Expected Behavior
The SPI Device must return data for the exact byte address requested by the SPI host. For the 1-byte `TPM_RID` register at offset `0xF04`, a 1-byte TPM read from address `0xD4_0F05` must return `0xFF`, because that byte is outside the implemented width of `TPM_RID`.

## Actual Behavior
A 1-byte TPM read from address `0xD4_0F05` can be interpreted as a read from `0xD4_0F04`, so the SPI Device returns the `TPM_RID` value instead of `0xFF`.

## Trigger Condition
This failure occurs when the SPI Device is operating in TPM FIFO mode, TPM hardware registers are returned directly by hardware, and the SPI host issues an unaligned TPM read to a hardware-returned register. The reported failing example is a 1-byte read of `TPM_RID` at address `0xD4_0F05`.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #15266 指明读 f05 应为 ff，实际误读 f04；PR 说明正反时钟域采地址早半周期。 |
| 触发过程 | SPI TPM FIFO mode→串行发送地址 f05→最后地址位跨半周期→错误选择 f04→回 RID 值而非 ff。 |
| 测试覆盖 | 设置 RID=0x10，发送 1 字节 D4_0F05 read；returned_bytes 收集在队列中。 |
| 尚存缺口 | 新序列没有对 returned_bytes 作显式比较；需查 spi_host_xfer_tpm_item 和原 scoreboard 是否确实比对 ff。 |
| 环境真实性 | 实际 SPI Device 原 UVM，经 SPI/TL 接口驱动，未见 force 或 RTL 替换。 |
| 跨周期价值 | 高，串行位计数与双沿采样。 |
| 题面提示 | 中：精确 failing address/expected byte 已给出；没有在题面给出补丁语句。 |
| 原审查后续建议 | 定位原 scoreboard 的 TPM 期望值计算；运行 f04/f05 邻接读和不同相位数据。 |

原审查“底层checker尚未核到”的缺口已由[补位复核](../replacement_review/review.md)解决；本地运行继续待执行。

## 原字段证据

`body` 字段内第5–5行：

```text
fifoaddr is latched with the counter being `'h1F`. The counter, however, runs on SPI_CLK, while the latching logic is running on inverted SPI_CLK domain.
```

`tb_script` 字段内第25–25行：

```text
bit [7:0] returned_bytes[$];
```

`tb_script` 字段内第34–34行：

```text
.addr(24'hD4_0F05),
```

`problem_statement` 字段内第8–8行：

```text
The SPI Device must return data for the exact byte address requested by the SPI host. For the 1-byte `TPM_RID` register at offset `0xF04`, a 1-byte TPM read from address `0xD4_0F05` must return `0xFF`, because that byte 
```
