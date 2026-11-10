# HWE-Bench RTL50

从公开HWE-Bench选出的50例原始RTL修复任务。Ibex 12例、CVA6 4例、Caliptra 9例、OpenTitan 25例。题面、代码版本、参考补丁、测试与评分标准保持上游原样；新增内容为筛选记录、中文审查和离线完整性检查。

先看 [50例情况与清单](benchmark_prep.md)，再看 [数据目录](datasets/README.md)。10例有本地原测试配对记录，其余40例待本地原测试校准；50例全量运行环境仍按项目准备。

## 目录

```text
datasets/                 # 50例原始JSONL及4个项目子集
hwe_bench/                # 原HWE收集、准备、执行和评分代码
deps/harbor/              # 原vendored agent运行框架
scripts/                  # 原镜像下载脚本 + verify_subset.py
docs/                     # 原HWE运行、镜像和agent说明
experiments/quality_review_20261110/analysis/
                          # 50例中文审查、10例原测试日志、补位复核
provenance/               # 来源、选择依据和文件校验
benchmark_prep.md         # 案例清单、验证状态与使用说明
pyproject.toml, uv.lock   # 原Python依赖
LICENSE                   # 原Apache-2.0许可；第三方许可随deps保留
```

`website/` 与 [README.upstream.md](README.upstream.md) 保留上游资料，其中417例数据规模和排行榜属于原HWE全量结果。本仓库`datasets/hwe_bench_full.jsonl`仅包含筛选的50例。

## 先浏览和校验

```bash
python scripts/verify_subset.py
# 可选：与完整原始数据逐行比较
python scripts/verify_subset.py --source /path/to/original/hwe_bench_full.jsonl
```

校验脚本只使用Python标准库，Python 3.10+可执行。数据集已经随仓库提供。

## 准备原HWE运行环境

运行原工具需要Linux、Python 3.12+、uv和Docker。使用需要的项目子集准备镜像：

```bash
uv sync
# 使用原Harbor agent流程时再安装
uv tool install --editable ./deps/harbor --force
./scripts/pull_images.sh ibex --dataset datasets/lowRISC__ibex.jsonl
./scripts/pull_images.sh cva6 --dataset datasets/openhwgroup__cva6.jsonl
./scripts/pull_images.sh caliptra --dataset datasets/chipsalliance__caliptra-rtl.jsonl
```

OpenTitan镜像需要本地提供VCS安装与许可证环境，并建立`vcs:minimal`基础镜像，按[构建说明](docs/building-images.md)操作。实际RTL及依赖由原镜像/准备流程获取，JSONL本身是案例资料。

## 运行与评分入口

原adapter会读取已准备镜像中的实际基线版本，生成agent任务：

```bash
uv run python -m hwe_bench.harness.harbor.adapter \
  --input datasets/lowRISC__ibex.jsonl \
  --output tasks/hwe-bench-ibex/
```

agent运行后，将其`patches.jsonl`交给原evaluator。下面的两个占位路径替换为实际绝对路径：

```bash
uv run python -m hwe_bench.harness.evaluator \
  --workdir /absolute/path/to/eval_workdir \
  --patch_files /absolute/path/to/patches.jsonl \
  --dataset_files datasets/lowRISC__ibex.jsonl \
  --output_dir results/ibex/eval \
  --log_dir /absolute/path/to/eval_logs \
  --stop_on_error false --max_workers 1
```

可以使用原Harbor流程，也可以由其他工具生成修复补丁后交给evaluator验收。参考补丁和验收测试随原始数据保留；各使用方根据自己的任务定义输入范围和评价方式。上游[运行说明](docs/agents.md)提供原工具的使用示例。

## 来源

上游代码：[https://github.com/pku-liang/hwe-bench](https://github.com/pku-liang/hwe-bench)，固定提交`10c78a87e1f92695d78d15b1464a6107dcac8837`。数据：[https://huggingface.co/datasets/henryen/hwe-bench](https://huggingface.co/datasets/henryen/hwe-bench)，固定版本`82a42e0a05719366a326e09ddc668ea0d46c91f6`。

逐行来源、未修改工具的文件哈希、#15269补位依据均随仓库保留。研究使用时引用原HWE-Bench，BibTeX见[上游README](README.upstream.md#citation)。
