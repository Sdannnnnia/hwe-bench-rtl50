# caliptra-rtl_747

来源：[原PR](https://github.com/chipsalliance/caliptra-rtl/pull/747)；源数据第74行；分类 `RTL_INTERFACE`。

保留理由：AHB错误响应的两拍时序与内部请求完成脱节，原测试同时检查正常发起、等待、报错和恢复。

本地证据：**原测试待本地实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

In Caliptra's `ahb_slv_sif` block, which bridges the AMBA Advanced High-performance Bus (AHB) to an internal client request interface, the downstream request-valid signal `dv` remains asserted for one extra clock after an outstanding transfer receives an error response. The bug is triggered when an AHB transfer has already been accepted, the internal client holds the request for at least one cycle, and then the client reports an error during the first AHB error-response cycle while the AHB bus is still not ready. The observed incorrect behavior is that `dv` stays high on that error cycle instead of clearing. The expected behavior is that as soon as the outstanding request completes with an error, `dv` must deassert in that same cycle and remain low until a new valid AHB transfer is accepted.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | 原issue #746解释hreadyout低且hresp高时请求会被重发；PR明确修dv多保持一拍。 |
| 触发过程 | 发起写→client hold→client释放并报错但AHB未ready→下一拍恢复。 |
| 测试覆盖 | 请求地址/方向、hold保活、AHB错误可见、dv清除及第二错误周期释放。 |
| 尚存缺口 | 未发后续新请求，未数实际外设写次数；测试驱动hready_i/hld而非接真实slave反馈。 |
| 环境真实性 | 真实ahb_slv_sif，通过模块端口模拟总线和client；内部err_f仅打印观察。 |
| 跨周期价值 | 中：短窗口协议与双接口握手，具有时序价值，规模较小。 |
| 题面提示 | 高：题面直接给dv、hready及要求清除的周期。 |
| 原审查后续建议 | 双版本复现后补错误后的正常读写及连续交易；保留正常请求断言以防直接压低dv。 |

## 原字段证据

`body` 字段内第5–6行：

```text
* Resolves #746
  * Fixes a bug in ahb_slv_sif that causes dv to remain asserted for an extra clock cycle after receiving an error. 
```

`resolved_issues` 字段内第1–1行：

```text
[{"org": "chipsalliance", "repo": "caliptra-rtl", "number": 745, "state": "closed", "title": "uds_seed/field_entropy hw-load is able to bypass CPTRA_FUSE_WR_DONE", "body": null}, {"org": "chipsalliance", "repo": "caliptra-rtl", "number": 746, "state": "closed", "title": "Bug: ahb_slv_sif continues t
```

`tb_script` 字段内第129–150行：

```text
    step(1'b1, 1'b1, 2'b10, 1'b1, 32'h0000_0040, 32'hCAFE_BABE, 1'b0, 1'b0);
    show_state("request");
    check_or_die(dv == 1'b1, "request was not presented to the component");
    check_or_die(write == 1'b1, "write qualifier was not latched");
    check_or_die(addr == 32'h0000_0040, "address was
```

`fix_patch` 字段内第57–65行：

```text
@@ -126,6 +126,11 @@ endgenerate
             if (hready_i) begin
                 dv <= hsel_i & htrans_i inside {2'b10, 2'b11};
             end
+            // Clear dv as soon as the component responds
+            // (in case of error, hready_i will still be 0 due to hreadyout_o == 0)
+        
```
