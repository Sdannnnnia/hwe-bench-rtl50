---
language:
  - en
license: apache-2.0
pretty_name: HWE-bench
size_categories:
  - n<1K
task_categories:
  - text-generation
tags:
  - benchmark
  - code
  - hardware
  - verilog
  - systemverilog
  - chisel
  - llm-agents
  - program-repair
  - arxiv:2604.14709
configs:
  - config_name: full
    data_files:
      - split: test
        path: hwe_bench_full.jsonl
  - config_name: ibex
    data_files:
      - split: test
        path: lowRISC__ibex.jsonl
  - config_name: cva6
    data_files:
      - split: test
        path: openhwgroup__cva6.jsonl
  - config_name: caliptra-rtl
    data_files:
      - split: test
        path: chipsalliance__caliptra-rtl.jsonl
  - config_name: rocket-chip
    data_files:
      - split: test
        path: chipsalliance__rocket-chip.jsonl
  - config_name: xiangshan
    data_files:
      - split: test
        path: OpenXiangShan__XiangShan.jsonl
  - config_name: opentitan
    data_files:
      - split: test
        path: lowRISC__opentitan.jsonl
---

# HWE-bench

HWE-bench is a benchmark for evaluating LLM agents on real-world hardware bug repair tasks. It contains 417 cases from six open-source hardware repositories covering Verilog, SystemVerilog, and Chisel projects.

Each case is a fail-to-pass task: the provided test fails on the buggy baseline and passes after the ground-truth fix. Evaluation scripts, Docker image instructions, and agent-running code are available in the [project repository](https://github.com/pku-liang/hwe-bench).

## Files

The dataset is provided both by repository and as a merged file. Use the repository-specific files when running evaluations, because Docker images and Harbor task directories are prepared per repository. Use `hwe_bench_full.jsonl` for analysis, statistics, or leaderboard-style loading.

| File | Repository | Cases |
|------|------------|------:|
| `lowRISC__ibex.jsonl` | `lowRISC/ibex` | 35 |
| `openhwgroup__cva6.jsonl` | `openhwgroup/cva6` | 35 |
| `chipsalliance__caliptra-rtl.jsonl` | `chipsalliance/caliptra-rtl` | 16 |
| `chipsalliance__rocket-chip.jsonl` | `chipsalliance/rocket-chip` | 32 |
| `OpenXiangShan__XiangShan.jsonl` | `OpenXiangShan/XiangShan` | 54 |
| `lowRISC__opentitan.jsonl` | `lowRISC/opentitan` | 245 |
| `hwe_bench_full.jsonl` | all repositories above | 417 |


## Evaluation Notes

Use the repository-specific JSONL files when running the benchmark. The HWE-bench code repository contains the scripts for pulling or building Docker images, generating Harbor task directories, running agents, extracting patches, and scoring results.

The Docker image pull script derives per-PR image tags from the JSONL records. OpenTitan images are not distributed because the evaluation flow requires Synopsys VCS; OpenTitan users need to build images locally from a user-provided `vcs:minimal` base image.

## Citation

If you use HWE-bench, please cite:

```bibtex
@article{cui2026hwe,
  title={HWE-Bench: Benchmarking LLM Agents on Real-World Hardware Bug Repair Tasks},
  author={Cui, Fan and Hou, Hongyuan and Luo, Zizhang and Yin, Chenyun and Liang, Yun},
  journal={arXiv preprint arXiv:2604.14709},
  year={2026}
}
```

## Schema

Each JSONL row is one benchmark instance. The fields are:

| Field | Description |
|-------|-------------|
| `org` | GitHub organization or owner. |
| `repo` | GitHub repository name. |
| `number` | Pull request number. |
| `id` | GitHub pull request numeric ID. |
| `node_id` | GitHub GraphQL node ID for the pull request. |
| `url` | GitHub API URL for the pull request. |
| `html_url` | Browser URL for the pull request. |
| `diff_url` | URL for the pull request diff. |
| `patch_url` | URL for the pull request patch. |
| `issue_url` | GitHub API URL for the pull request's issue thread. |
| `comments_url` | GitHub API URL for issue comments. |
| `commits_url` | GitHub API URL for pull request commits. |
| `review_comments_url` | GitHub API URL for pull request review comments. |
| `review_comment_url` | GitHub API URL template for one review comment. |
| `state` | Pull request state from GitHub. |
| `draft` | Whether the pull request was a draft. |
| `title` | Pull request title. |
| `body` | Pull request body, usually normalized to a compact provenance note. |
| `labels` | GitHub labels attached to the pull request. |
| `created_at` | Pull request creation timestamp. |
| `updated_at` | Pull request update timestamp. |
| `closed_at` | Pull request close timestamp. |
| `merged_at` | Pull request merge timestamp. |
| `merge_commit_sha` | GitHub merge commit SHA. |
| `base` | GitHub base branch metadata, including the upstream base commit SHA. |
| `commits` | Pull request commit metadata collected from GitHub. |
| `resolved_issues` | Issue records linked to the pull request. |
| `modified_files` | Files changed by the pull request. |
| `lines_added` | Number of added lines in the pull request diff. |
| `lines_removed` | Number of removed lines in the pull request diff. |
| `fix_patch` | Ground-truth bug-fix patch. |
| `test_patch` | Test-related patch content from the original pull request, if present. |
| `level1` | Coarse bug category, such as RTL or software-hardware bug fix. |
| `level2` | Finer bug category. |
| `benchmark_value` | Integer score describing how useful the case is as a benchmark task. |
| `cross_layer_depth` | Integer score for hardware-software interaction depth. Present when applicable. |
| `reproducer_signal` | Integer score for how much evidence exists for constructing a reproducer. |
| `simulation_cost` | Integer score for expected simulation cost. |
| `reproducer_path` | Expected reproducer style, such as existing test, minimal testbench, or full-system software path. |
| `priority_score` | Candidate ranking score used during case selection. Present when applicable. |
| `prepare_script` | Optional script baked into the per-PR Docker image before evaluation. |
| `tb_script` | Hidden fail-to-pass test script used by the evaluator. |
| `problem_statement` | Natural-language task description shown to the repair agent. |
| `run_result` | Result summary for running the test before applying the ground-truth fix. |
| `test_patch_result` | Result summary for the buggy baseline run. |
| `fix_patch_result` | Result summary after applying the ground-truth fix. |
| `fixed_tests` | Tests that fail on the buggy baseline and pass after the ground-truth fix. |
| `f2p_tests` | Fail-to-pass test outcomes. |
| `p2p_tests` | Pass-to-pass test outcomes. |
| `s2p_tests` | Skip-to-pass test outcomes. |
| `n2p_tests` | None-to-pass test outcomes. |
