# opentitan_22906

来源：[原PR](https://github.com/lowRISC/opentitan/pull/22906)；源数据第190行；分类 `RTL_LOGIC`。

保留理由：非法命令之后还要完成合法INS/UNI并检查成功状态，具有实质恢复验收；关闭scoreboard使覆盖较窄。

本地证据：**原测试待本地实测**。运行准备状态：待校准。

## 原始 HWE 题面

## Description
OpenTitan's CSRNG (Cryptographically Secure Random Number Generator) accepts application commands through per-interface command staging logic (`cmd_stage`). The affected functionality is the CSRNG software application interface (`SW_APP`) command path in this staging logic. An unsupported application-command opcode can be accepted far enough into that path to leave the interface stuck instead of being rejected cleanly.

## Expected Behavior
If `SW_APP` submits an unsupported application command, CSRNG should treat it as a recoverable error without leaving that interface unusable. After the recoverable alert for the invalid request is handled and cleared, a later valid `instantiate` command followed by a valid `uninstantiate` command on the same interface should still complete normally and report successful completion.

## Actual Behavior
An unsupported command can raise the recoverable alert but still leave the `SW_APP` command staging path wedged. After that happens, later legal commands on the same interface may no longer complete as expected. In particular, a normal `instantiate` followed by `uninstantiate` sequence can stop reaching its completion indication even though both commands are valid.

## Trigger Condition
This is triggered when the software application interface receives an unsupported generate-like application command that also carries extra command words, i.e. a nonzero command-length field (`clen`). The failure is especially visible with a multiword invalid request such as the reserved `GENU` opcode with `clen = 2`.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | PR正文指向commit且说明回归有新增失败；patch把非法命令判断移到cmd_stage，并修改相关alert文档。题面给出明确恢复要求。 |
| 触发过程 | SW_APP发保留GENU/clen=2→等待recov_alert并清除→20拍后合法INS→合法UNI。 |
| 测试覆盖 | 后续两命令都等cmd_req_done，并检查CMD_STS_SUCCESS再清done；有短超时。 |
| 尚存缺口 | en_scb=0且assert_off_alert；未查DRBG状态/输出，也没有确认非法命令只生成一次规定错误；无条件产生done/success可能钻空子。 |
| 环境真实性 | 真实CSRNG经TL CSR命令路径，UVM代理；不强置DUT内部状态。 |
| 跨周期价值 | 高：错误收尾影响后续事务可用性。 |
| 题面提示 | 高：点名cmd_stage和具体非法opcode/长度；未直接指定FSM代码行。 |
| 原审查后续建议 | 原HWE双版本校准；增加INS→GEN已知向量与非法命令计数/状态检查；核实PR依赖#22883的base已包含。 |

## 原字段证据

`body` 字段内第1–7行：

```text
Please see the commit message for a description.

I ran a regression with 0.1 multiplier and a few more tests than usual are failing (~5 more than expected).

I didn't have time to debug all of them but I think this PR is ready to at least be looked at.

depends on #22883
```

`tb_script` 字段内第32–43行：

```text
  task automatic wait_cmd_req_done_short(string step_name);
    `DV_SPINWAIT(
      forever begin
        uvm_reg_data_t act_data;
        csr_rd(.ptr(ral.intr_state.cs_cmd_req_done), .value(act_data));
        if (act_data == 1'b1) break;
      end,
      $sformatf("timeout waiting for cmd_req_done
```

`tb_script` 字段内第49–81行：

```text
    cfg.csrng_assert_vif.assert_off_alert();

    cs_item = csrng_item::type_id::create("illegal_cmd");
    cs_item.acmd = csrng_pkg::GENU;
    cs_item.clen = 'h2;
    cs_item.flags = MuBi4True;
    cs_item.glen = 'h2;
    cs_item.cmd_data_q.push_back(32'h11112222);
    cs_item.cmd_data_q.push_back(
```

`tb_script` 字段内第95–107行：

```text
  function void configure_env();
    super.configure_env();
    cfg.en_scb = 0;
    cfg.otp_en_cs_sw_app_read_pct = 100;
    cfg.otp_en_cs_sw_app_read_inval_pct = 0;
    cfg.lc_hw_debug_en_pct = 0;
    cfg.regwen_pct = 100;
    cfg.enable_pct = 100;
    cfg.sw_app_enable_pct = 100;
    cfg.read_int_
```
