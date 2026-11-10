# caliptra-rtl_786

来源：[原PR](https://github.com/chipsalliance/caliptra-rtl/pull/786)；源数据第79行；分类 `RTL_LOGIC`。

保留理由：触发链清楚，真实SHA运算前后都有标准digest比较，是这组里最值得优先保留的案例之一。

本地证据：**原测试待本地实测**。运行准备状态：待校准。

## 原始 HWE 题面

In the Caliptra SHA-512 accelerator, the generate Platform Configuration Register (PCR) hash flow can leave the message-block lock state stuck after the operation finishes. If software runs a generate-PCR-hash command, waits for completion, issues a zeroize, and then starts a normal SHA-512 hash, the SHA-512 block registers can still behave as locked and fail to accept the newly written message block. The following standard SHA-512 command can therefore return an incorrect digest. Zeroize is expected to fully clear any lock state created by the generate-PCR-hash flow so that the next standard SHA-512 command behaves like a fresh operation: newly written block data must be accepted and the digest must match that data. The affected subsystem is the SHA-512 block, specifically the interaction between the generate-PCR-hash path and zeroize recovery.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | 关联原issue #780明确gen hash sticky lock应由zeroize清除；HWE把影响具体化为下一次SHA512。 |
| 触发过程 | 普通abc hash sanity→zeroize→gen PCR hash完成→zeroize→再次写abc并普通hash。 |
| 测试覆盖 | 前后两次SHA512 digest均与abc标准向量比较，有超时与错误计数。 |
| 尚存缺口 | 前后恰好同一输入，可能漏掉复用旧digest的假修复；未验证PCR hash本身正确，PCR响应固定为零。 |
| 环境真实性 | 真实sha512_ctrl/sha512_core和寄存器经AHB访问，PCR端口简化；没有内部force。 |
| 跨周期价值 | 高：跨操作状态残留，错误出现在后续正常计算。 |
| 题面提示 | 高：题面明确锁位未清及zeroize恢复位置；仍需沿状态追查。 |
| 原审查后续建议 | 双版本校准；将前后普通hash改成不同消息作为额外验收，加入正常gen hash回归；原HWE测试另保留。 |

## 原字段证据

`resolved_issues` 字段内第1–1行：

```text
[{"org": "chipsalliance", "repo": "caliptra-rtl", "number": 780, "state": "closed", "title": "gen hash sticky lock bits bugfix", "body": "Fixing sticky lock bits in gen hash operation\r\nZeroize will clear the lock bits after gen hash operation."}, {"org": "chipsalliance", "repo": "caliptra-rtl", "n
```

`tb_script` 字段内第327–339行：

```text
      abc_block = 1024'h6162638000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000018;
      abc_expected
```

`tb_script` 字段内第347–375行：

```text
      write_single_word(`SHA512_REG_SHA512_GEN_PCR_HASH_NONCE_0, 32'h01234567);
      write_single_word(`SHA512_REG_SHA512_GEN_PCR_HASH_NONCE_1, 32'h89abcdef);
      write_single_word(`SHA512_REG_SHA512_GEN_PCR_HASH_NONCE_2, 32'h0badc0de);
      write_single_word(`SHA512_REG_SHA512_GEN_PCR_HASH_NONC
```
