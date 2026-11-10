# opentitan_11833

来源：[原PR](https://github.com/lowRISC/opentitan/pull/11833)；源数据第250行；分类 `RTL_INTERFACE`。

保留理由：通过SPI读出的实际字节与预置SRAM逐字比较，跨模块脉冲/电平问题有原PR证据，优先保留。

本地证据：**原测试待本地实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

## Description
The bug affects the SPI_DEVICE IP's internally handled Read SFDP (Serial Flash Discoverable Parameters, opcode `0x5A`) path, specifically the flash-read datapath between `spi_readcmd` and `spid_readsram` that serves bytes from the SFDP region of the internal dual-port SRAM (DPSRAM).

## Observed Behavior
When an external SPI master performs a multi-byte SFDP read, the byte stream returned by SPI_DEVICE can be shifted relative to the contents stored in the SFDP SRAM region. The memory contents are correct, but the bytes driven on the SPI interface do not match the requested address sequence.

## Expected Behavior
After the 24-bit SFDP address has been accepted, SPI_DEVICE should return the bytes stored at that address and each following address in order, with no skipped, duplicated, or shifted bytes. For example, an 8-byte read starting at address `0x000080` should return the eight bytes stored at `0x000080` through `0x000087` in that same order.

## Trigger Condition
The failure appears when the Read SFDP command transitions from address capture into continuous multi-byte data output. It is observable on sequential SFDP reads, including an aligned 8-byte transfer starting at `0x000080`.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | PR解释spi_readcmd把pulse错作level导致spid_readsram/FIFO字节移位；关联SFDP原direct-test发现返回错误。 |
| 触发过程 | SRAM填可识别字节序列→SFDP opcode0x5A/address0x80→连续读8bytes。 |
| 测试覆盖 | 8字节按地址递增精确比较，timeout明确fatal；修正旧TB payload input为ref以取得真正响应。 |
| 尚存缺口 | 单对齐起点/长度/时钟模式；没覆盖非对齐、跨边界、多次CS及反压。基础pre_dv完整源码未逐文件验证。 |
| 环境真实性 | 复用原pre_dv真实SPI readcmd/readsram通路，软件端口填DPSRAM；未force内部状态。 |
| 跨周期价值 | 高：地址锁存事件驱动FIFO预取和连续串行输出。 |
| 题面提示 | 中：题面给模块边界与症状/期望字节，不直接给addr_latched应改pulse；原body有答案，应与题面分开。 |
| 原审查后续建议 | 优先双版本校准，补非对齐起点和多长度/第二事务；确认payload ref兼容修改在两版完全相同。 |

## 原字段证据

`body` 字段内第3–18行：

```text
    `addr_latched_i` in `spid_readsram` module is expected to be a pulse
    signal. The `spi_readcmd` module generates the signal as a level by
    comparing `addr_cnt_d` with all zero value.

    As a result, the `strb` register in `spid_readsram` follows the
    current address, which is increase
```

`tb_script` 字段内第29–36行：

```text
common = Path("hw/ip/spi_device/pre_dv/tb/spid_common.sv")
common_text = common.read_text(encoding="utf-8")
payload_arg_old = "    input spi_data_t   payload [$]\n"
payload_arg_new = "    ref spi_data_t     payload [$]\n"
if payload_arg_old not in common_text:
    raise SystemExit("missing expected 
```

`tb_script` 字段内第93–108行：

```text
    $display("Sending a SFDP command");
    spiflash_readsfdp(tb_sif, 8'h 5A, SfdpReadAddr, SfdpReadSize, sfdp_data);

    for (int i = 0 ; i < SfdpReadSize ; i++) begin
      automatic spi_data_t exp_byte;
      exp_byte = spi_data_t'(SfdpReadAddr + 24'(i));
      if (sfdp_data[i] !== exp_byte) beg
```

`tb_script` 字段内第144–152行：

```text
    for (int i = 0 ; i < SramSfdpDepth ; i++) begin
      byte_idx = i * 4;
      word_data = {
        spi_data_t'(byte_idx + 3),
        spi_data_t'(byte_idx + 2),
        spi_data_t'(byte_idx + 1),
        spi_data_t'(byte_idx + 0)
      };
      sram_writeword(sw_clk, sw_l2m, sw_gnt, sw_m2l, Sra
```
