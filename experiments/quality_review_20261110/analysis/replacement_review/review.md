# OpenTitan #15269 补位复核

结论：纳入原始 HWE 50 例子集。此前待补项是序列中 `returned_bytes` 未直接比较，需确认原 UVM scoreboard 是否检查返回值。本次读取与原 `prepare_script` 相同的提交 `2512ca0da80635a4677c522b1f8b8b8d5bc23789`，静态确认完整检查链；本轮仿真执行数为 0。

## 依据

1. 原 issue #15266 明确给出：一字节 RID 位于 `0xF04`，读取 `0xF05` 应返回 `0xFF`，实际误读 `0xF04`。原 HWE 测试写 RID=`0x10`，再读 `0xD4_0F05`，输入与该问题一致。
2. `hw/dv/sv/dv_lib/dv_base_env_cfg.sv`：`en_scb=1`；原 HWE 脚本、TPM 基类和该项目 base test 均未关闭 scoreboard。
3. `hw/ip/spi_device/dv/env/spi_device_env.sv`：启用 scoreboard 时将 SPI monitor 的 `host_analysis_port` 连接到 `scoreboard.upstream_spi_host_fifo`。
4. `hw/dv/sv/spi_agent/seq_lib/spi_host_tpm_seq.sv` 将 `cfg.spi_func_mode` 设为 `SpiModeTpm`；`spi_monitor.sv` 采集并发送 TPM 读取事务。
5. `spi_device_scoreboard.sv` 的 `SpiModeTpm` 分支用请求地址生成期望值，调用 `compare_tpm_hw_reg`；该函数按地址低两位选择期望字节，不匹配时调用 `uvm_error`。
6. `spi_device_env_pkg.sv` 定义 `TPM_RID_OFFSET=0xF04`、`TPM_RID_BYTE_SIZE=1`。`get_reg_val_with_all_1s_padding` 将其余字节填为全 1，所以 RID=`0x10` 时期望字为 `0xFFFFFF10`，`0xF05` 对应字节为 `0xFF`；误读 RID 的 `0x10` 会被上述比较拒绝。

这些证据解决“只有收集返回值、没有数据比较”的缺口，支持保留候选。原始题面、RTL 基线、参考补丁、`prepare_script`、`tb_script` 和评分标准均保持原样。这里的源码审查支持候选资格，本地 buggy/reference 仿真仍为待执行；多地址、多相位和普通路径回归也保持待核验状态。

## 来源

本目录 `source/` 保存通过 GitHub 连接器取得的上述固定提交源码，仅用于审查；路径、Git blob 标识、SHA-256 和原始链接见 `sources.json`。用于执行的源码仍由原 HWE 环境准备流程获取。
