# benchmark 准备

## HWE 原始 50 例分享仓库（2026-11-10）

本次主评测候选采用原始 HWE 子集，位于 `benchmarks/hwe-bench-rtl50/`，按原仓库组织。50条JSONL记录逐行保留原始字节，原题面、基线、参考补丁、prepare、TB和评分标准保持原样。审查说明与已有日志单列。

**组成：Ibex 12例、CVA6 4例、Caliptra 9例、OpenTitan 25例。** 从上一版49例加入OpenTitan #15269。该例原测试虽未在序列里直接比较返回队列，但固定历史版本的原scoreboard确实按地址比较TPM返回字节；补位依据为源码审查，本轮运行数为0。Ibex #882因原测试采样疑点继续待审，调整后的诊断测试保留在旧审查中。

按上游原标签：逻辑21例、接口16例、时序同步8例、规格4例、配置集成1例。标签保留原定义，跨周期价值看逐例触发链与状态依赖。

### 实测与准备状态

| 证据类型 | 数量 | 当前含义 |
|---|---:|---|
| 原HWE脚本本轮配对 | 6 | buggy行为失败、reference通过；复用本地pr-1735工具镜像，各例固定源码；prepare未重跑 |
| 原HWE脚本历史配对 | 4 | #222/#244/#1735/#377；脚本、补丁和源码对应关系已核验 |
| 仅历史改编测试证据 | 4 | #24771/#1073/#757/#963；原HWE本地配对仍待核验 |
| 其余尚无本地配对 | 36 | 包括新补入#15269；当前依据是原始材料与静态审查 |

**原测试本地配对已有10/50，待完成40/50。** 上游50例均记录F2P，P2P字段均为空。这里的配对只表示原失败场景复现；原测试覆盖面、题面提示程度、环境依赖仍逐例保留。50例均为主评测候选，统一模型输入、完整正常回归与新机器环境校准继续待准备。本次未调用模型、未新增EDA执行。

原HWE题面主要是行为bug report，完整设计spec和协议资料需结合各版本工程查阅。此前的小集六维评分、雷达图及三类实验适用率对应原来的小集；这50例的统一评分与Probe/Directed/Formal组合覆盖率保持待评，不移用旧分数。

### 工具与运行

`datasets/` 保存50例全量文件和4个项目子集；`hwe_bench/` 保留原收集、准备、复现、评分工具；`deps/harbor/` 保留原运行框架；`scripts/`、`docs/`、依赖锁和许可随包保留。顶层上游GitHub发布工作流未启用；`website/` 保留上游展示资料，其417例排行榜属于上游原结果。源码和Docker镜像按原流程获取，分享包包含数据与工具，镜像另行准备。OpenTitan需要本地VCS镜像与许可证环境。

先运行 `python scripts/verify_subset.py` 校验分享包；需与完整原数据比对时使用 `--source <原417例JSONL>`。执行时按项目使用 `datasets/lowRISC__ibex.jsonl` 等子集，镜像准备和评分命令见仓库README。原JSONL同时含评价材料，实际模型输入通过明确清单或原adapter生成任务绑定；原始reference与隐藏TB留在评价侧。

### 逐例清单

| 案例 | 保留理由／功能 | 原分类 | 本地证据 |
|---|---|---|---|
| [ibex_1816](experiments/quality_review_20261110/analysis/cases/ibex_1816.md) | 请求先撤掉，晚一拍写原因时记错；是真正的跨拍信息丢失。 | RTL_TIMING_SYNC | 原测试待本地实测 |
| [ibex_1735](experiments/quality_review_20261110/analysis/cases/ibex_1735.md) | PMP新权限晚一条指令生效，属于有明确安全后果的跨拍问题。 | RTL_LOGIC | 原测试配对（历史） |
| [ibex_1469](experiments/quality_review_20261110/analysis/cases/ibex_1469.md) | 较好的复杂例：前一条分支未解决，后一次预测覆盖了恢复信息。 | RTL_LOGIC | 原测试待本地实测 |
| [ibex_1135](experiments/quality_review_20261110/analysis/cases/ibex_1135.md) | 可保留成取指错误窗口案例，验收范围要写成FIFO局部行为。 | RTL_LOGIC | 原测试配对（本轮） |
| [ibex_475](experiments/quality_review_20261110/analysis/cases/ibex_475.md) | Debug内异常污染先前CSR，适合状态保持问题；现有测试只是最小起点。 | RTL_SPEC | 原测试配对（本轮） |
| [ibex_465](experiments/quality_review_20261110/analysis/cases/ibex_465.md) | 从U态进入Debug仍留在U态，程序可正常触发。 | RTL_SPEC | 原测试配对（本轮） |
| [ibex_377](experiments/quality_review_20261110/analysis/cases/ibex_377.md) | 首响应报错后过早跳异常，后半事务仍控制AGU，属于很好的跨模块时序问题。 | RTL_INTERFACE | 原测试配对（历史） |
| [ibex_293](experiments/quality_review_20261110/analysis/cases/ibex_293.md) | 没有新分支时，已经发出的顺序请求掉了；与#332的新协议讨论可区分。 | RTL_INTERFACE | 原测试配对（本轮） |
| [ibex_222](experiments/quality_review_20261110/analysis/cases/ibex_222.md) | 执行结束后取指停顿，旧写使能继续生效；此前使用过不影响候选资格。 | RTL_LOGIC | 原测试配对（历史） |
| [ibex_244](experiments/quality_review_20261110/analysis/cases/ibex_244.md) | 背靠背CSR开关中断暴露流水线漏响应，有现成完整程序验收。 | RTL_LOGIC | 原测试配对（历史） |
| [ibex_167](experiments/quality_review_20261110/analysis/cases/ibex_167.md) | 真实程序经过halt和DRET，直接验证恢复地址。 | RTL_SPEC | 原测试配对（本轮） |
| [ibex_122](experiments/quality_review_20261110/analysis/cases/ibex_122.md) | 跨字store地址和byte-enable丢失，完整CPU程序可触发。 | RTL_LOGIC | 原测试配对（本轮） |
| [cva6_2170](experiments/quality_review_20261110/analysis/cases/cva6_2170.md) | 真实不缓存store丢写，但随附测试只查cache输出格式，复杂度偏低。 | RTL_INTERFACE | 原测试待本地实测 |
| [cva6_2945](experiments/quality_review_20261110/analysis/cases/cva6_2945.md) | 多个历史TLB条目拼出假命中，已有正反对照，是较整齐的案例。 | RTL_LOGIC | 原测试待本地实测 |
| [cva6_2989](experiments/quality_review_20261110/analysis/cases/cva6_2989.md) | 异常已成立却又触发页表读，适合无多余副作用问题，但测试正对照不足。 | RTL_LOGIC | 原测试待本地实测 |
| [cva6_3168](experiments/quality_review_20261110/analysis/cases/cva6_3168.md) | 可保留作较简单配置交互例；它不是强跨周期主力。 | RTL_CONFIG_INTEG | 原测试待本地实测 |
| [caliptra-rtl_963](experiments/quality_review_20261110/analysis/cases/caliptra-rtl_963.md) | 多拍事务内错误被后续成功覆盖，原PR明确支持；需要补成功路径以防“永远报错”。 | RTL_LOGIC | 仅历史改编证据；原测试待实测 |
| [caliptra-rtl_1033](experiments/quality_review_20261110/analysis/cases/caliptra-rtl_1033.md) | 有真实安全需求，测试通过总线启动完整ECC签名，再篡改KeyVault选择，最终检查签名，值得优先保留。 | RTL_LOGIC | 原测试待本地实测 |
| [caliptra-rtl_1073](experiments/quality_review_20261110/analysis/cases/caliptra-rtl_1073.md) | 真实AXI/AHB桥的背靠背读和反压，原始错误可从公开接口观察；原验收只覆盖卡住时。 | RTL_INTERFACE | 仅历史改编证据；原测试待实测 |
| [caliptra-rtl_747](experiments/quality_review_20261110/analysis/cases/caliptra-rtl_747.md) | AHB错误响应的两拍时序与内部请求完成脱节，原测试同时检查正常发起、等待、报错和恢复。 | RTL_INTERFACE | 原测试待本地实测 |
| [caliptra-rtl_757](experiments/quality_review_20261110/analysis/cases/caliptra-rtl_757.md) | 从停住的读到竞争写再到读写先后完成都测到了，接口层复现较干净。 | RTL_INTERFACE | 仅历史改编证据；原测试待实测 |
| [caliptra-rtl_725](experiments/quality_review_20261110/analysis/cases/caliptra-rtl_725.md) | manual START前后都有检查，能防止用“永远不启动”糊弄；属于AES控制问题，不等于完整GCM运算评测。 | RTL_LOGIC | 原测试待本地实测 |
| [caliptra-rtl_786](experiments/quality_review_20261110/analysis/cases/caliptra-rtl_786.md) | 触发链清楚，真实SHA运算前后都有标准digest比较，是这组里最值得优先保留的案例之一。 | RTL_LOGIC | 原测试待本地实测 |
| [caliptra-rtl_594](experiments/quality_review_20261110/analysis/cases/caliptra-rtl_594.md) | PR明确允许启动后改变输入，8位缩参仍在测试真实流水寄存；适合短时序子集，难度不宜算高。 | RTL_LOGIC | 原测试待本地实测 |
| [caliptra-rtl_506](experiments/quality_review_20261110/analysis/cases/caliptra-rtl_506.md) | 溢出保持和清空后恢复都检查了，软件可见状态有原PR和寄存器文档支持。 | RTL_LOGIC | 原测试待本地实测 |
| [opentitan_24771](experiments/quality_review_20261110/analysis/cases/opentitan_24771.md) | 真实 SHA 计算/停止相遇导致卡死，已有本项目改编运行证据；原 HWE 仍按原口径审。 | RTL_LOGIC | 仅历史改编证据；原测试待实测 |
| [opentitan_23432](experiments/quality_review_20261110/analysis/cases/opentitan_23432.md) | 原issue报告真实HMAC上下文切换卡死，定向测试保留状态机自然演进；SHA完成由TB模拟，须限制结论范围。 | RTL_LOGIC | 原测试待本地实测 |
| [opentitan_22906](experiments/quality_review_20261110/analysis/cases/opentitan_22906.md) | 非法命令之后还要完成合法INS/UNI并检查成功状态，具有实质恢复验收；关闭scoreboard使覆盖较窄。 | RTL_LOGIC | 原测试待本地实测 |
| [opentitan_22049](experiments/quality_review_20261110/analysis/cases/opentitan_22049.md) | NAK后暂停、软件清除后恢复都有观察，适合协议恢复；原PR也带新功能，按NAK暂停子问题定义范围。 | RTL_LOGIC | 原测试待本地实测 |
| [opentitan_20884](experiments/quality_review_20261110/analysis/cases/opentitan_20884.md) | 原issue提供128拍超时契约和现成回归，近阈值故障跨时钟丢失，很适合因果调试。 | RTL_TIMING_SYNC | 原测试待本地实测 |
| [opentitan_20437](experiments/quality_review_20261110/analysis/cases/opentitan_20437.md) | 两个真实FSM都测abort后回idle和再启动，局部恢复有验收；完整TL未返回响应的恢复尚未覆盖。 | RTL_INTERFACE | 原测试待本地实测 |
| [opentitan_20304](experiments/quality_review_20261110/analysis/cases/opentitan_20304.md) | 禁用后命令队列残留有明确原PR依据，新增检查会直接读真实队列深度；scoreboard是适配而非关闭。 | RTL_LOGIC | 原测试待本地实测 |
| [opentitan_20293](experiments/quality_review_20261110/analysis/cases/opentitan_20293.md) | 启动流程结束后交还软件控制，触发和验收链清楚，值得保留。 | RTL_SPEC | 原测试待本地实测 |
| [opentitan_15269](experiments/quality_review_20261110/analysis/cases/opentitan_15269.md) | 补查固定历史版本的原UVM scoreboard，确认按地址低位比较TPM返回字节；原测试具备数据检查，纳入候选。 | RTL_TIMING_SYNC | 原测试待本地实测 |
| [opentitan_15117](experiments/quality_review_20261110/analysis/cases/opentitan_15117.md) | 外部慢上升引发误中断，既验无误报又等正常读完成，保留。 | RTL_TIMING_SYNC | 原测试待本地实测 |
| [opentitan_12988](experiments/quality_review_20261110/analysis/cases/opentitan_12988.md) | 短事件跨慢时钟丢失，激励、捕获和复位清除均可观察。 | RTL_TIMING_SYNC | 原测试待本地实测 |
| [opentitan_12724](experiments/quality_review_20261110/analysis/cases/opentitan_12724.md) | 前一次事务的通知污染后一次事务，测试确实读两次 opcode 验身份。 | RTL_TIMING_SYNC | 原测试待本地实测 |
| [opentitan_12473](experiments/quality_review_20261110/analysis/cases/opentitan_12473.md) | 真实接口相互等待，测试同时验请求到达和完成，保留。 | RTL_INTERFACE | 原测试待本地实测 |
| [opentitan_11904](experiments/quality_review_20261110/analysis/cases/opentitan_11904.md) | 关钟期间两次事件互相抵消，测试保留了真实 CDC 核心，保留。 | RTL_TIMING_SYNC | 原测试待本地实测 |
| [opentitan_11833](experiments/quality_review_20261110/analysis/cases/opentitan_11833.md) | 通过SPI读出的实际字节与预置SRAM逐字比较，跨模块脉冲/电平问题有原PR证据，优先保留。 | RTL_INTERFACE | 原测试待本地实测 |
| [opentitan_10732](experiments/quality_review_20261110/analysis/cases/opentitan_10732.md) | 时钟消失时 POR 仍要传播，具备明确硬件契约和恢复检查。 | RTL_TIMING_SYNC | 原测试待本地实测 |
| [opentitan_10097](experiments/quality_review_20261110/analysis/cases/opentitan_10097.md) | SPI上传数据跨时钟进入共享SRAM，延迟grant后仍要交付opcode/address，测试有数据核对和超时。 | RTL_INTERFACE | 原测试待本地实测 |
| [opentitan_9343](experiments/quality_review_20261110/analysis/cases/opentitan_9343.md) | 输入保持时间造成重复采样，测试同时验“别提前做”和“之后真的完成”，质量较好。 | RTL_INTERFACE | 原测试待本地实测 |
| [opentitan_8366](experiments/quality_review_20261110/analysis/cases/opentitan_8366.md) | 软件改配置打断进行中握手，真实控制器和正常完成数据都有检查。 | RTL_INTERFACE | 原测试待本地实测 |
| [opentitan_7547](experiments/quality_review_20261110/analysis/cases/opentitan_7547.md) | 读改写各阶段的数据和地址语义有实质比较，保留。 | RTL_INTERFACE | 原测试待本地实测 |
| [opentitan_7034](experiments/quality_review_20261110/analysis/cases/opentitan_7034.md) | 低功耗进入失败后残留状态，原目标与测试一致，保留。 | RTL_LOGIC | 原测试待本地实测 |
| [opentitan_8724](experiments/quality_review_20261110/analysis/cases/opentitan_8724.md) | 这里实际测完整 SPI core 的串行输出，七字节顺序和 CS 连续性都查，优先保留。 | RTL_LOGIC | 原测试待本地实测 |
| [opentitan_17054](experiments/quality_review_20261110/analysis/cases/opentitan_17054.md) | 真实回归中的read/RMA交叠，题面主要讲症状，根因藏在更下层buffer控制，调试价值很高。 | RTL_INTERFACE | 原测试待本地实测 |
| [opentitan_18941](experiments/quality_review_20261110/analysis/cases/opentitan_18941.md) | 真实 suspend/resume 后新包被误当重传，局部测试比较了提交而不只是 ACK。 | RTL_INTERFACE | 原测试待本地实测 |
| [opentitan_23807](experiments/quality_review_20261110/analysis/cases/opentitan_23807.md) | 被拒绝事务污染下一笔事务，现有测试同时查协议响应和后续数据，很适合。 | RTL_INTERFACE | 原测试待本地实测 |

逐例审查、补位源码与已有原测试日志都采用仓库内相对路径。来源与字段哈希见 `provenance/selection.json`，上游工具哈希见 `provenance/upstream_files.json`。


## 原则

**包含内容**

1. 模型prompt
   1. 原始 Buggy RTL（必要时包含完整工程）。
   2. Specification、接口协议、合法输入约束：重点在有足够的信息支持实验判定
   3. 初始失败测试及运行方式。
   4. 初始失败 Log、波形或 Formal Counterexample。
   5. 可用的编译、仿真、Formal 等工具环境：可复现。
2. 检验材料
   1. 原始失败测试和已有回归测试。
   2. Reference RTL / Ground Truth Patch / 独立 Checker 或验证性质。
   3. 根因位置、错误机制和关键时序信息。
   4. 必要时的额外测试及形式验证结果。

**评价维度**（雷达图）

- 时间复杂度：涉及多个周期、状态保持、流水线延迟
- 结构复杂度：多模块信号依赖、跨模块握手
- 诊断歧义：多种合理根因能够解释初始失败
- 修复复杂度：是否只需改一两行控制条件，是否需要多模块协同修改，是否容易过拟合局部测试，是否需要保持其他路径不变
- 实验可操作性：存在合法输入激励、可观测信号或受控干预
- 结果可判定性：有 Checker、Reference 或形式性质判断实验结果

### 评分规则（v2，2026-11-09）

每维取 1–5 分，证据不足记 `null / 待评`。前四维越高表示诊断或修复更复杂；后两维越高表示实验条件更充分。雷达图采用相同轴序、相同量程，分别标注这两组轴，不计算面积排名或总分。

| 维度 | 1 分 | 2 分 | 3 分 | 4 分 | 5 分 |
|---|---|---|---|---|---|
| 时间复杂度 | 同拍组合关系即可解释 | 单个前拍状态或一次握手保持 | 两级以上寄存传播、多个状态阶段或状态间循环等待 | 完整事务跨多个阶段，需联合计数、流水或历史事件才能解释 | 多个交叠事务/状态机历史共同决定错误，需跟踪阶段、请求身份与完成顺序 |
| 结构复杂度 | 单模块、单个局部逻辑锥 | 单模块内两个以上状态/数据通道耦合 | 错误传播实际跨两个 RTL 实例的接口 | 跨三个以上 RTL 实例，或跨模块且跨时钟域 | 多级子系统、多个接口或时钟域共同参与，局部替换会改变目标机制 |
| 诊断歧义 | 初始材料直接指出错误位置/修改 | 至少两种局部假设，用一个观测即可区分 | 至少三种合理假设，涉及不同机制，需比较两个以上观测 | 三种以上假设跨模块，至少两步实验才能排除 | 存在遮蔽/等效观测，多种干预仍需联合历史和规格才能区分 |
| 修复复杂度 | 局部常数/位选择/运算符修改，影响范围单一 | 一个条件或寄存使能修正，需保持相邻边界行为 | 同模块多个状态/赋值联动，或一个修改同时影响多个协议路径 | 多模块语义修改或接口时序协同，需保持在途事务与恢复行为 | 新状态/存储/协议重构，多个模式与异常路径均需重新建立一致性 |
| 实验可操作性 | 可静态阅读，执行环境待建立 | 原失败可重放，观察或输入控制有限 | 有命名观测点与至少一个合法可变激励，运行边界明确 | 至少两类互补实验有具体执行入口，能区别竞争假设 | 多个合法刺激维度、受控观察/干预与性质检查均可执行，适用范围与成本已校准 |
| 结果可判定性 | 主要靠人工解释输出 | 单一参考轨迹/结果，可判原例，规格或覆盖有限 | 有与接口契约对应的可执行 checker，已区分 buggy/reference | 有独立回归或多场景 oracle，并检查触发/完成，错误与环境失败分离 | 独立回归与有触发覆盖的形式性质相互验证，核心修复义务完整验收 |

逐例记录 `score、reason、evidence、confidence`；置信度分为实测、静态审查和待验证。分数描述当前任务包及已有证据：

- 时间复杂度依据必要状态依赖；仿真总长度、timeout 和时钟分频数单独记录。
- 结构复杂度依据目标错误传播经过的实例；辅助文件数与工程总规模单独记录。测试模型替代的部分显式列出。
- 诊断歧义列出具体候选假设和区分实验；分数是研究者初评，模型实验后另行校准。
- 修复复杂度依据语义义务；开发者 patch 的行数、格式变更和无关功能分开统计。
- 后两维以当前实际材料和验收深度评分。系统级验收待完成时，保持其明确状态。

### 三类实验及统计口径

| 指标 | 逐例判断所需证据 |
|---|---|
| Probe 适用 | 有合法失败重放、可访问的命名信号/状态及采样时刻；增加观测能支持或排除至少一个具体假设 |
| Directed Simulation 适用 | 给出可改变的合法输入维度、具体定向场景及预期可区分结果；checker 能评价该场景 |
| Formal 适用 | 有具体性质、clock/reset、合法环境约束、目标 RTL 范围及触发 cover；状态空间/工具能力的可行性有依据 |
| 实验可判定 | 有独立行为契约对应的 checker、参考结果或性质；编译失败、运行超时、X/未知与行为违规分别记录 |
| 组合覆盖 | 给出最小实验组合、竞争假设和各实验能排除的解释，最终形成可验证的修复义务；单纯存在任意一种工具只计该工具适用 |

适用性逐例取 `VERIFIED`（实际运行证据）、`SUPPORTED`（具体方案与材料审查支持，尚待运行）、`UNKNOWN`（证据/可行性未定）、`NO`（有明确不适用理由）。某次工具超时单列为运行结果，适用性继续按证据判断。

- 以本版冻结的全部案例数 `N` 为共同分母，报告 `适用率=(VERIFIED+SUPPORTED)/N`，同时拆出 `实测确认率=VERIFIED/N`、`待定率=UNKNOWN/N` 和 `不适用率=NO/N`。
- 组合覆盖从 {Probe, Directed Simulation, Formal} 中选择解决本例所需的最小组合，允许 Probe+Directed；按逐例的实验计划和区分能力审查统计，并单列实际完成组合的比例。统计采用案例级权重；同设计家族分布另表报告。
- `实际实验成功率=达到预先定义实验目的的已执行实验数/已执行实验数`；每次执行先记录目的、预期可区分观测和资源边界。编译/环境失败、超时、无有效触发均保留在执行分母并分类。
- 准备阶段的工具校准和后续模型自主实验分别汇总。`buggy FAIL/reference PASS` 是复现校准结果；Formal 的 `PROVEN/FALSIFIED/UNKNOWN`、性质触发 cover、有限仿真通过以及模型修复成功率分别报告。
- 暂无模型实验时，模型实验成功率显示 `N/A，已执行 0`；不以适用率、工具可运行率或参考版本通过率替代。

### 每例交付与版本

每例提供模型可见文件清单（buggy RTL、行为 spec、合法输入、公开失败 TB/log 和运行入口），评价侧保留 reference、独立 checker/性质、根因与评分依据。Prompt 共用 `prompts/` 中的模板；模型输入按显式清单绑定。各例附六维雷达图、Probe/Directed/Formal 实验卡及适用性结论。

同一 benchmark 构建任务继续使用 `experiments/benchmark_intake_20261108/`；本轮材料写入其 `preparation_v2/`，已有来源和运行证据保持冻结。准备完成后生成逐例 JSON、共同分母统计及离线可视化。
