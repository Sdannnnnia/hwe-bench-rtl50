# opentitan_20293

来源：[原PR](https://github.com/lowRISC/opentitan/pull/20293)；源数据第214行；分类 `RTL_SPEC`。

保留理由：启动流程结束后交还软件控制，触发和验收链清楚，值得保留。

本地证据：**原测试待本地实测**。运行准备状态：待校准。

## 原始 HWE 题面

## Description
The EDN (Entropy Distribution Network) IP does not cleanly hand control from boot-time request mode back to its normal software command path. After the boot-time sequence finishes, the EDN main state machine reaches `BootDone`; clearing `CTRL.BOOT_REQ_MODE` while keeping the EDN enabled is supposed to exit boot-time request mode and return the block to software-driven operation.

## Expected Behavior
When the boot-time sequence has completed and firmware clears `CTRL.BOOT_REQ_MODE` without disabling the EDN, the EDN main state machine should leave `BootDone`, enter the normal software-port state (`SWPortMode`), and report that the software command interface is ready again so firmware can submit normal post-boot commands through the EDN software port.

## Actual Behavior
After the boot-time sequence completes, clearing `CTRL.BOOT_REQ_MODE` can leave the EDN stuck in `BootDone` instead of transitioning into software-port operation. The software command path therefore does not report ready for normal post-boot commands.

## Affected Function
The affected logic is the EDN main state machine path that handles the handoff from boot-time request mode to the normal software-port mode.

## Trigger Condition
This occurs when the EDN is enabled in boot-time request mode, the configured boot-time sequence runs to completion, firmware clears `CTRL.BOOT_REQ_MODE` while keeping the EDN enabled, and firmware then attempts to use the EDN software command interface.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | 原 issue #19655 引用 EDN 文档允许清 BOOT_REQ_MODE 退出；原 PR 同时补 uninstantiate 与错误态命令门控，题目仅覆盖 boot→SW 子问题。 |
| 触发过程 | boot instantiate/generate 完成→BootDone→软件清 boot_req_mode→硬件 uninstantiate→SWPortMode→软件 INS/UNI。 |
| 测试覆盖 | 显式等待 BootDone、SWPortMode、CMD_RDY，随后发送 INS/UNI；原 EDN DV 仍参与验收。 |
| 尚存缺口 | 新增序列未显式计数退出时的 uninstantiate；要核原 scoreboard 对此及错误态门控的覆盖。把状态直接改成 SWPortMode 的假修复需被拦住。 |
| 环境真实性 | CSR 前门驱动；状态和 CMD_RDY 后门只读，未强设 DUT 状态；CSRNG 响应延迟设零，实际延迟变化尚待回归。 |
| 跨周期价值 | 高，跨 boot/SW 两种工作模式和下游握手。 |
| 题面提示 | 高：题面直接点名 BootDone、SWPortMode 和丢失的状态转换。 |
| 原审查后续建议 | 原测试双版本运行；核 uninstantiate 顺序和非零 ack 延迟，冻结题面时统一是否允许给内部状态名。 |

## 原字段证据

`problem_statement` 字段内第2–2行：

```text
The EDN (Entropy Distribution Network) IP does not cleanly hand control from boot-time request mode back to its normal software command path. After the boot-time sequence finishes, the EDN main state machine reaches `Boo
```

`tb_script` 字段内第92–92行：

```text
wait_for_main_sm_state(SWPortMode, SwModeTimeoutClks, "SWPortMode");
```

`tb_script` 字段内第95–95行：

```text
wr_cmd(.cmd_type(edn_env_pkg::Sw),
```

`fix_patch` 字段内第307–307行：

```text
+          state_d = BootLoadUni;
```
