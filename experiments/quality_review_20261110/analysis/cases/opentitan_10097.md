# opentitan_10097

来源：[原PR](https://github.com/lowRISC/opentitan/pull/10097)；源数据第271行；分类 `RTL_INTERFACE`。

保留理由：SPI上传数据跨时钟进入共享SRAM，延迟grant后仍要交付opcode/address，测试有数据核对和超时。

本地证据：**原测试待本地实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

## Description
In the SPI Device upload path, command and address entries are stored in a shared dual-port SRAM and later exposed to software through the command FIFO (CmdFifo) and address FIFO (AddrFifo) in the system clock domain. The affected logic is the `spid_upload` path that issues the system-side SRAM accesses for those two FIFOs after an upload-enabled SPI flash transaction captures an opcode and address.

## Expected Behavior
If the shared SRAM arbiter delays the system-side CmdFifo or AddrFifo request, the pending entry must be held until the grant arrives. After the grant and SRAM response complete, software must still be able to read the uploaded command byte and captured address from the corresponding FIFO outputs in the same order they were recorded.

## Actual Behavior
The upload path can treat a system-side CmdFifo or AddrFifo SRAM request as accepted before the arbiter actually grants it. When the grant is delayed, the read side can advance too early, causing the uploaded command or address entry to disappear or never become visible to software. Software can then miss the upload record or wait indefinitely for FIFO data that should be present.

## Trigger Condition
The bug is triggered during an upload-enabled SPI flash transaction that records both a command byte and an address, when the system-clock-domain SRAM request for CmdFifo or AddrFifo is not granted immediately and remains stalled for one or more system clock cycles.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | issue #10065与PR明确共享SRAM竞争时必须用grant；patch给upload增加grant输入并连至原arbiter。 |
| 触发过程 | SPI字节输入上传命令及3字节地址→SYS域读请求被延迟2拍→grant→读出命令与地址。 |
| 测试覆盖 | CmdFIFO与AddrFIFO各自等待valid并精确比较值，最后消费，双时钟运行。 |
| 尚存缺口 | 固定2拍grant和单命令/地址，未验证多entry排序、重复read、FIFO满或真正SW竞争；地址期望为接口内部打包格式DEAD_BE00。 |
| 环境真实性 | 真实spid_upload，字节级输入替代串行解码，共享SRAM/arbiter用可延迟grant存储模型；非完整SPI设备。新增port前后用.*适配。 |
| 跨周期价值 | 高：CDC FIFO与共享资源接受时序，局部测试仍保留核心链条。 |
| 题面提示 | 高：题面指出把req误作accepted和grant等待。 |
| 原审查后续建议 | 校准双版本，确认原版确为数据丢失而非端口编译差异；补多命令+不同grant延迟及真实SRAM仲裁集成回归。 |

## 原字段证据

`body` 字段内第1–5行：

```text
Issue was discussed in #10065.
    
This commit opens grant ports for CmdFifo/AddrFifo in the upload module.
The grant signals come from the SYS SRAM arbiter. With the change, the
module and the SW wait until the request is acked.
```

`tb_script` 字段内第102–155行：

```text
  always_comb begin
    sck_sram_i = '0;
    sys_cmdfifo_sram_i = '0;
    sys_addrfifo_sram_i = '0;
    sys_cmdfifo_sram_i.rvalid = cmd_rsp_rvalid_q;
    sys_cmdfifo_sram_i.rdata = cmd_rsp_rdata_q;
    sys_addrfifo_sram_i.rvalid = addr_rsp_rvalid_q;
    sys_addrfifo_sram_i.rdata = addr_rsp_rdata_q;

```

`tb_script` 字段内第198–240行：

```text
  task automatic expect_cmd();
    int unsigned cycles;
    begin
      cycles = 0;
      while (!sys_cmdfifo_rvalid_o && (cycles < TimeoutSysCycles)) begin
        @(posedge sys_clk_i);
        cycles++;
      end
      if (!sys_cmdfifo_rvalid_o) begin
        $fatal(1, "Timed out waiting for cmdfi
```

`fix_patch` 字段内第70–95行：

```text
@@ -66,8 +66,10 @@ module spid_upload
   // Arbiter among these + SW access is in the SPID top module
   output sram_l2m_t sys_cmdfifo_sram_o,
   input  sram_m2l_t sys_cmdfifo_sram_i,
+  input             sys_cmdfifo_gnt_i, // from arbiter
   output sram_l2m_t sys_addrfifo_sram_o,
   input  sram_m2l
```
