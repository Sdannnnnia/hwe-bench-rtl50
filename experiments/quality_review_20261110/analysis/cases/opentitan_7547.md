# opentitan_7547

来源：[原PR](https://github.com/lowRISC/opentitan/pull/7547)；源数据第314行；分类 `RTL_INTERFACE`。

保留理由：读改写各阶段的数据和地址语义有实质比较，保留。

本地证据：**原测试待本地实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

## Description
`tlul_sram_byte`, the byte-write helper used by `tlul_adapter_sram` when TileLink Uncached Lightweight (TL-UL) integrity handling is enabled, does not preserve the correct semantics for partial writes. When a `PutPartialData` request updates only part of a 32-bit word, the module performs an internal read-modify-write sequence to regenerate integrity bits. For a sub-word write that targets a byte lane inside the word, the memory-facing transactions are not consistently converted into accesses to the containing aligned word, and the completion returned to the upstream TL-UL host can report the internal full-word transfer size instead of the original request size.

## Expected Behavior
A partial write must be executed internally as a read-modify-write of the containing aligned 32-bit word. The memory-facing read and write should both use the aligned word address, use the full-word access size, and cover all byte lanes of that word. The writeback data should combine the previously stored word with the updated byte lanes from the original request. The TL-UL response returned to the host must preserve the original request size rather than the internal full-word transfer size.

## Actual Behavior
For a partial write, the internal read-modify-write path can retain sub-word request semantics instead of switching fully to aligned full-word semantics. This means the downstream memory-side access can use the incoming byte address or request size instead of the containing word address and full-word size, and the response observed by the TL-UL host can expose the internal full-word size rather than the original partial-write size.

## Affected Function
The affected logic is the integrity-enabled partial-write handling in `tlul_sram_byte`, which is used by the byte-write path of `tlul_adapter_sram`.

## Trigger Condition
The bug is triggered by a `PutPartialData` request whose mask does not cover the entire 32-bit word, especially a single-byte or other sub-word write to a non-word-aligned address within that word.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | 原 PR 修 byte write 及 RAW workaround；题面聚焦 partial write 必须按完整字读改写、host 保留原 size。需绑定 TLUL 原契约作为额外依据。 |
| 触发过程 | byte write addr5/mask0010→读 addr4 fullword→merge AA byte→fullword写回→host Ack size恢复0。 |
| 测试覆盖 | 检查下游 read/write opcode、addr、size、mask、write data，以及上游 Ack opcode/size。 |
| 尚存缺口 | 只有一个 lane/数据和无背压；没有检查 host d_error/source/integrity，也未覆盖 RAW workaround 效果。 |
| 环境真实性 | 真实 tlul_sram_byte/FIFO/ECC encoder；下游 memory responder 手工驱动合法 request-response；无内部 force。 |
| 跨周期价值 | 高，跨 RMW 阶段保存原请求属性。 |
| 题面提示 | 中高：逐阶段应该怎样对齐、保留 size 已明确，未给修改语句。 |
| 原审查后续建议 | 运行双版本，复用正常 fullword、各 byte lane、背压和相邻 RAW 测试。 |

## 原字段证据

`tb_script` 字段内第115–115行：

```text
check_req("read_phase",
```

`tb_script` 字段内第126–126行：

```text
check_req("write_phase",
```

`tb_script` 字段内第142–142行：

```text
fail($sformatf("host response size exp=0 act=%0d", tl_o.d_size));
```

`body` 字段内第5–5行：

```text
This fixes a few bugs in the byte write logic and adds a workaround for potential RAW hazards that can occur when the byte write logic is employed together with `prim_ram_1p_scr`.
```
