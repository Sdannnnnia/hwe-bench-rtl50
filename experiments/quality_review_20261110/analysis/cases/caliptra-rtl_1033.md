# caliptra-rtl_1033

来源：[原PR](https://github.com/chipsalliance/caliptra-rtl/pull/1033)；源数据第72行；分类 `RTL_LOGIC`。

保留理由：有真实安全需求，测试通过总线启动完整ECC签名，再篡改KeyVault选择，最终检查签名，值得优先保留。

本地证据：**原测试待本地实测**。运行准备状态：待校准。

## 原始 HWE 题面

In Caliptra's Elliptic Curve Cryptography (ECC) engine, software can still rewrite the KeyVault private-key read-control register after an ECC signing operation has started. KeyVault is Caliptra's internal key storage interface used by crypto blocks to fetch protected key material. When ECC signing is configured to use a private key from a KeyVault entry, the selected entry must remain fixed for the entire signing operation. If software writes a different value to the ECC KeyVault private-key control register while the ECC engine is busy, that write should be ignored and the signature should still be generated from the key that was selected before the operation began. Instead, the active KeyVault private-key selection can change mid-operation, which changes the ECC signing result.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | PR body与issue #1035明确要求crypto忙时锁住KeyVault控制；fix在ECC/HMAC/SHA等处加入软件写使能。HWE只选ECC私钥控制这一子问题。 |
| 触发过程 | 配置slot 1私钥→启动签名→等busy并延迟50周期→写slot 0控制→等待ready→读R/S签名。 |
| 测试覆盖 | 完整ecc_top计算结果与固定R/S向量相等；busy时篡改导致结果变化会失败。 |
| 尚存缺口 | 只测一个key和一个篡改时刻；未查操作结束后合法改选、seed/写回控制、其他crypto模块。卡死依赖外部执行超时，原脚本自身无timeout。 |
| 环境真实性 | 真实ecc_top和总线接口；KeyVault以按slot/offset返回数据的模型替代，slot 0无效。需核对真实KV拒绝时的时序；未直接改内部状态。 |
| 跨周期价值 | 高：配置锁定跨越长计算，外部寄存器写影响内部密钥及最终签名。 |
| 题面提示 | 高：题面已点名私钥read-control和busy期间写应忽略，基本给出故障边界；未给具体写使能表达式。 |
| 原审查后续建议 | 先跑原HWE双版本；追加空闲时切换有效key及busy不同阶段写入的原有回归，核对KeyVault模型。 |

## 原字段证据

`body` 字段内第1–2行：

```text
Fix for #1035. Keyvault hardening - swwe on keyvault controls to prevent modification during engine operation.
Update adamsbridge submodule to tag 1.0.2
```

`tb_script` 字段内第119–129行：

```text
  always_comb begin : kv_model
    kv_wr_resp_tb = '0;
    pcr_signing_data_tb = '0;
    for (int client = 0; client < 2; client++) begin
      kv_rd_resp_tb[client].error = !slot_valid[kv_read_tb[client].read_entry];
      kv_rd_resp_tb[client].last = (kv_read_tb[client].read_offset == 4'd11);
    
```

`tb_script` 字段内第279–313行：

```text
  task automatic run_test;
    operand_t sign_r;
    operand_t sign_s;
    logic [31:0] tamper_ctrl;
    begin
      wait_ready();
      write_block(`ECC_REG_ECC_MSG_0, MSG);
      write_block(`ECC_REG_ECC_IV_0, IV);

      write_single_word(
          `ECC_REG_ECC_KV_RD_PKEY_CTRL,
          `ECC_RE
```

`fix_patch` 字段内第183–209行：

```text
@@ -487,6 +487,30 @@ module ecc_dsa_ctrl
         hwif_in.ecc_kv_wr_pkey_ctrl.write_en.hwclr = ~kv_write_ready;
     end
 
+    // Software write-enables to prevent KV reg manipulation mid-operation
+    always_comb hwif_in.ecc_kv_rd_pkey_ctrl.read_en.swwe         = !kv_key_data_present && ecc_ready
```
