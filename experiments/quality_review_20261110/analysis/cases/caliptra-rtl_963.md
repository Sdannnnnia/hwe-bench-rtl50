# caliptra-rtl_963

来源：[原PR](https://github.com/chipsalliance/caliptra-rtl/pull/963)；源数据第71行；分类 `RTL_LOGIC`。

保留理由：多拍事务内错误被后续成功覆盖，原PR明确支持；需要补成功路径以防“永远报错”。

本地证据：**仅历史改编证据；原测试待实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

In Caliptra's KeyVault read client (`kv_read_client`), the status for a multi-beat read transaction can be overwritten by a later beat instead of preserving an earlier failure. If a KeyVault read stays active across multiple beats and one non-final beat reports a read error, a subsequent successful beat, including the final beat, can incorrectly make the overall transaction appear successful. `kv_read_client` is the block that returns KeyVault data to Caliptra hardware consumers. The expected behavior is that once any beat in a read transaction reports a KeyVault read failure, that failure remains latched for the rest of the transaction and the completed read reports failure rather than success.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | PR正文明确KV错误应寄存并保留，而非采用最后beat状态；patch同时修read/write client，HWE只测read。 |
| 触发过程 | 保持read_en→四拍读中间一拍error→最后两拍success→结束应KV_READ_FAIL。 |
| 测试覆盖 | 最终error_code；shell同时要求TB_PASS且无TB_FAIL。 |
| 尚存缺口 | 没有断言read_done、数据、每拍status、全成功或下一笔清错；返回常量FAIL可过。 |
| 环境真实性 | 真实read_client/rule_check/fsm，128位配置4beats，KV响应端口按拍驱动；未模拟完整KV权限变化和真实发起端，存在posedge驱动需校准竞态。 |
| 跨周期价值 | 中：多beat状态归约，单事务几拍。 |
| 题面提示 | 很高：题面直接给错误应sticky及所属client。 |
| 原审查后续建议 | 原HWE双版本运行，再加全成功、末拍错误、错误后下一笔成功、read_done/数据验收；与B09旧改编校准分开。 |

## 原字段证据

`body` 字段内第1–8行：

```text
## RTL
Update KeyVault clients to register and preserve error status on kv access instead of using the status from the final beat of the transfer
Update AES Caliptra wrapper to clear (with zeroes) the intermediate key registering stage when reading a new key from keyvault
Include needed header files
```

`tb_script` 字段内第72–113行：

```text
    // Keep read_en asserted through the transfer, matching the sticky CSR-style usage.
    read_ctrl_reg.read_en = 1'b1;
    read_ctrl_reg.read_entry = 5;
    read_metrics.ocp_lock_in_progress = 1'b0;
    read_metrics.kv_read_dest = '0;
    read_metrics.kv_key_entry = 5;

    // Cycle 1: rule check
```

`fix_patch` 字段内第234–243行：

```text
@@ -110,7 +110,11 @@ always_ff @(posedge clk or negedge rst_b) begin
         error_code <= KV_SUCCESS;
     end
     else begin
-        error_code <= validated_read_en & ~read_allow ? KV_READ_FAIL :
+        // On first beat of kv read, latch any error conditions.
+        // On subsequent beats o
```
