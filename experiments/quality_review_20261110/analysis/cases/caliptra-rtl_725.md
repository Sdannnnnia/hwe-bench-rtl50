# caliptra-rtl_725

来源：[原PR](https://github.com/chipsalliance/caliptra-rtl/pull/725)；源数据第78行；分类 `RTL_LOGIC`。

保留理由：manual START前后都有检查，能防止用“永远不启动”糊弄；属于AES控制问题，不等于完整GCM运算评测。

本地证据：**原测试待本地实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

In Caliptra's AES control finite-state machine, AES-GCM manual operation is not correctly enforced during the GCM TAG phase. When AES-GCM is configured for manual start, the controller is in the TAG phase, and software has already written a complete input block for tag processing, the block can leave its idle state and begin the GHASH (Galois hash) side of tag handling before software issues the explicit START command. The correct behavior is that manual mode must keep the AES-GCM TAG phase idle until START is asserted; loading the full tag input block alone must not consume that input or begin tag processing. This bug affects the AES subsystem's GCM control path under the trigger condition of manual operation plus a fully loaded TAG-phase input block.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | PR正文概述AES模式验证，具体TAG契约来自HWE题面及RTL既有manual start注释/对应修复；独立原规格段落尚未核对。 |
| 触发过程 | GCM TAG+manual→逐字写满4字→等待仍idle→发START→捕获数据并启动GHASH。 |
| 测试覆盖 | START前无数据消费/无GHASH valid且idle；START后清trigger、捕获input并在4拍内发valid。 |
| 尚存缺口 | 未检查最终TAG、完整GCM阶段切换、自动模式和GHASH反压；固定接口tieoff使算术数据通路退出测试。 |
| 环境真实性 | 真实aes_control_fsm及状态寄存器、原始primitive；GHASH/AES端口由TB提供ready/status，未实例化完整加密核；无内部force。 |
| 跨周期价值 | 中：多次寄存器写形成ready状态，再与手动启动交互。 |
| 题面提示 | 高：明确指TAG阶段manual gating及GHASH，不是只给外部错误。 |
| 原审查后续建议 | 校准双版本并定位原AES manual-operation规格；沿用上游GCM已知向量回归和自动模式，避免将控制级通过写成算法通过。 |

## 原字段证据

`tb_script` 字段内第237–271行：

```text
    write_data_word(0);
    write_data_word(1);
    write_data_word(2);
    write_data_word(3);

    check_or_fail(input_ready_o === 1'b0, "input block did not become full");
    check_or_fail(idle_o === 1'b1, "module left IDLE before manual START");
    check_or_fail(start_we_o === 1'b0, "manual ST
```

`fix_patch` 字段内第73–75行：

```text
   // If set to start manually, we just wait for the trigger. Otherwise, check common as well as
   // mode-specific start conditions.
   assign start = cfg_valid & no_alert &
```

`fix_patch` 字段内第149–155行：

```text
+  // For the tag phase of GCM, we also need the input data.
+  assign start_gcm_tag = gcm_tag & cfg_valid & no_alert &
+      // Manual operation has priority.
+      (manual_operation_i ? start_i : hash_subkey_ready_q & s_ready_q & data_in_new);
+
+  // The restore, AAD, save and tag phases use th
```
