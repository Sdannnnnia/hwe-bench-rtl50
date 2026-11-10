# caliptra-rtl_594

来源：[原PR](https://github.com/chipsalliance/caliptra-rtl/pull/594)；源数据第81行；分类 `RTL_LOGIC`。

保留理由：PR明确允许启动后改变输入，8位缩参仍在测试真实流水寄存；适合短时序子集，难度不宜算高。

本地证据：**原测试待本地实测**。完整主评测准备状态：待校准。

## 原始 HWE 题面

In Caliptra's ECC modular add/subtract helper `ecc_add_sub_mod_alter`, a request is not fully captured when `add_en_i` is pulsed. If software or surrounding logic starts an operation with a single-cycle `add_en_i` pulse and then changes `sub_i`, the operands, or the modulus before `ready_o` asserts, the block can raise `ready_o` while `res_o` reflects the newer input values instead of the original transaction. The correct behavior is that each launched operation is self-contained: after a single `add_en_i` pulse, `ready_o` must indicate that `res_o` is valid for the operation mode, operands, and modulus that were present when the request was accepted, and callers should not need to keep those inputs fixed until completion as long as no new operation is issued before `ready_o`.

## 审查记录

| 项目 | 记录 |
|---|---|
| 行为依据 | PR body L7–8明确只约束add_en单拍且ready前不重发，不再约束操作数稳定。 |
| 触发过程 | 脉冲启动(3+4) mod13→ready前把mode/操作数/modulus都改掉→要求结果仍7且ready只一拍。 |
| 测试覆盖 | ready时刻、结果7及ready脉宽；真实ecc_adder/ecc_add_sub_mod_alter。 |
| 尚存缺口 | 仅REG_SIZE=8，一个加法向量；常量7可过这一条；未覆盖384位、减法、模归约/进位、连续操作和zeroize。 |
| 环境真实性 | 通过合法模块端口，缩参改变算术规模但未替换控制；原PR语义允许输入变化。 |
| 跨周期价值 | 中偏低：一两拍流水输入采样错位，单模块。 |
| 题面提示 | 很高：题面直说请求未完整捕获，并要求锁住mode/operand/modulus。 |
| 原审查后续建议 | 用原宽384位加减边界向量复现，并加入多组不同结果；短窗口案例单独分层。 |

## 原字段证据

`body` 字段内第7–8行：

```text
2) froze adder inputs to fix #194 (found by FPV)
With this PR, there is no more constraints on keeping inputs fixed. The only constraint is having a single pulse add_en_i, and do not enable it again until ready_o.
```

`tb_script` 字段内第19–20行：

```text
module ecc_add_sub_mod_alter_ready_tb;
    localparam int REG_SIZE = 8;
```

`tb_script` 字段内第50–71行：

```text
    task automatic expect_ready_result(input logic [REG_SIZE-1:0] expected);
    begin
        @(posedge clk);
        #1;

        if (!ready_o) begin
            $display("ERROR: ready_o was low when the result should be valid");
            $fatal(1);
        end

        if (res_o !== expected) 
```

`tb_script` 字段内第88–107行：

```text
        @(negedge clk);
        // Launch a single modular-add transaction: (3 + 4) mod 13 = 7.
        add_en_i = 1'b1;
        sub_i = 1'b0;
        opa_i = 8'd3;
        opb_i = 8'd4;
        prime_i = 8'd13;

        @(posedge clk);
        #1;

        add_en_i = 1'b0;

        // Disturb all i
```
