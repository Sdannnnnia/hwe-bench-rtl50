#!/usr/bin/env python3
"""离线核验50例原始数据、项目拆分、上游工具与随包证据。"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def check_manifest(root, entries):
    for item in entries:
        path = root / item['path']
        require(path.resolve().is_relative_to(root), f'路径越界：{item["path"]}')
        if item['kind'] == 'symlink':
            require(path.is_symlink() and os.readlink(path) == item['target'], f'链接不匹配：{path}')
        else:
            require(path.is_file() and digest(path.read_bytes()) == item['sha256'], f'文件哈希不匹配：{path}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, help='可选：完整原始417例JSONL')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    selection = load(root / 'provenance/selection.json')
    entries = load(root / 'provenance/package_files.json')
    check_manifest(root, entries)
    originals = load(root / 'provenance/upstream_files.json')
    check_manifest(root, originals)
    items = selection['cases']
    require(len(items) == 50, '选择记录数量应为50')
    ids = [r['case_id'] for r in items]
    require(len(set(ids)) == 50 and 'ibex_882' not in ids and 'opentitan_15269' in ids, 'ID集合异常')
    raw_lines = (root / 'datasets/hwe_bench_full.jsonl').read_bytes().splitlines(keepends=True)
    require(len(raw_lines) == 50, '合并JSONL应恰好50行')
    raw_rows = [json.loads(line) for line in raw_lines]
    require([f"{r['repo']}_{r['number']}" for r in raw_rows] == ids, '选择记录与JSONL顺序不一致')
    require(Counter(r['repo'] for r in raw_rows) == selection['summary']['by_repo'], '项目数量不匹配')
    partitions = {}
    field_checks = 0
    evidence_files = 0
    pair_cases = 0
    for item, raw, line in zip(items, raw_rows, raw_lines):
        require(digest(line) == item['source_line_sha256'], f'原始行被改动：{item["case_id"]}')
        for key, expected in item['source_fields_sha256'].items():
            value = raw[key] if isinstance(raw[key], str) else json.dumps(raw[key], ensure_ascii=False)
            require(digest(value.encode()) == expected, f'原始字段被改动：{item["case_id"]}/{key}')
            field_checks += 1
        partitions.setdefault(f"{raw['org']}__{raw['repo']}", []).append(line)
        require((root / item['review_path']).is_file(), f'逐例审查缺失：{item["case_id"]}')
        variants = set()
        for evidence in item['runtime_evidence']:
            data = (root / evidence['path']).read_bytes()
            require(digest(data) == evidence['sha256'], '日志哈希不匹配')
            if evidence['semantic_marker']:
                require(evidence['semantic_marker'] in data.decode(), '目标行为失败/通过签名缺失')
            require(not evidence['timed_out'], '已验证配对包含超时')
            require((evidence['returncode'] == 0) == (evidence['variant'] == 'reference'), '返回码与配对不一致')
            variants.add(evidence['variant'])
            evidence_files += 1
        if item['runtime_status'] in ('NEW_ORIGINAL_PAIR', 'HISTORICAL_ORIGINAL_PAIR'):
            require(variants == {'buggy','reference'}, '配对日志不完整')
            pair_cases += 1
    for project, lines in partitions.items():
        require((root / f'datasets/{project}.jsonl').read_bytes() == b''.join(lines), f'项目拆分不一致：{project}')
    require(pair_cases == selection['summary']['local_original_pair_cases'] == 10, '原测试配对数异常')
    expected_datasets = {'hwe_bench_full.jsonl'} | {p+'.jsonl' for p in partitions}
    require({p.name for p in (root/'datasets').glob('*.jsonl')} == expected_datasets, '含意外数据集文件')
    source_compared = False
    if args.source:
        source = args.source.read_bytes()
        require(digest(source) == selection['source']['full_dataset_sha256'], '完整原数据哈希不匹配')
        source_lines = source.splitlines(keepends=True)
        for item, line in zip(items, raw_lines):
            require(source_lines[item['source_line']-1] == line, f'与原始行不相同：{item["case_id"]}')
        source_compared = True
    review_dir = root / 'experiments/quality_review_20261110/analysis'
    replacement = review_dir / 'replacement_review'
    sources = load(replacement / 'sources.json')
    for item in sources['files']:
        data = (replacement / item['local_path']).read_bytes()
        require(digest(data) == item['sha256'], '补位审查源码哈希不匹配')
        git_blob = hashlib.sha1(('blob '+str(len(data))+'\0').encode()+data).hexdigest()
        require(git_blob == item['git_blob_sha'], '补位审查Git blob不匹配')
    own_docs = [root/'README.md', root/'benchmark_prep.md', root/'datasets/README.md'] + list((review_dir/'cases').glob('*.md'))
    links = 0
    for path in own_docs:
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if '://' in target or target.startswith('#'):
                continue
            relative = target.split('#')[0]
            require(not relative.startswith('/'), f'本地绝对链接：{path}/{target}')
            require((path.parent / relative).resolve().is_relative_to(root), f'链接离开分享包：{target}')
            require((path.parent / relative).exists(), f'失效链接：{path}/{target}')
            links += 1
    print(json.dumps({'status':'PASS', 'cases':50, 'project_partitions':len(partitions),
        'source_fields_checked':field_checks, 'package_entries_checked':len(entries),
        'upstream_entries_checked':len(originals), 'original_pair_cases':pair_cases,
        'runtime_log_files':evidence_files, 'replacement_source_files':len(sources['files']),
        'local_links_checked':links, 'source_compared':source_compared,
        'runtime_runs':0, 'model_calls':0}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
