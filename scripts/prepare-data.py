"""Build the catalog from the supplied static-analysis CSVs, without inferring support."""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

root = Path(__file__).resolve().parents[1]


def read(name):
    with (root / 'data' / name).open(encoding='utf-8-sig', newline='') as source:
        return list(csv.DictReader(source))


def unique(values):
    return list(dict.fromkeys(value for value in values if value))


def usable_default(value, kind, uncertain):
    if not value or uncertain or kind.startswith('文字列'):
        return True
    if '0/1' in kind:
        return value in ('0', '1')
    if any(word in kind for word in ('整数', '数値', '浮動小数', '小数')):
        try:
            number = float(value)
        except ValueError:
            return False
        return math.isfinite(number) and ('整数' not in kind or number.is_integer())
    return True


def build(all_rows, candidates):
    candidate_by_name = {row['起動オプション']: row for row in candidates}
    if len(candidate_by_name) != len(candidates):
        raise ValueError('Duplicate candidate names')
    groups = defaultdict(list)
    for row in all_rows:
        name = row['起動オプション']
        if not name or not name.startswith(('+', '-')) or any(c.isspace() for c in name):
            raise ValueError(f'Invalid option name: {name!r}')
        groups[name].append(row)
    if candidate_by_name.keys() - groups.keys():
        raise ValueError('Candidates missing from full catalog')
    options = []
    for name, rows in groups.items():
        row = rows[0]
        candidate = candidate_by_name.get(name)
        kind = candidate['必要な値の型'] if candidate else row['必要な値の型']
        defaults = unique(r['デフォルト値'] for r in rows)
        default = candidate['既定値（静的解析・推定を含む）'] if candidate else (defaults[0] if len(defaults) == 1 else '')
        if default and default not in defaults:
            defaults.append(default)
        value = default if len(defaults) == 1 and not default.startswith(('未', '不明', '（')) else ''
        if '値不要' in kind:
            value = ''
        uncertain = any(word in kind for word in ('不明', '引数形式未確認'))
        if not usable_default(value, kind, uncertain):
            value = ''
        sources = unique(url.strip() for r in rows for key in ('今回の再調査ソース', '評価ソースURL', '参考URL') for url in r[key].split('|') if url.strip().startswith(('https://', 'http://')))
        options.append(dict(
            id=name, name=name, default=value, defaults=defaults,
            value_kind='値なし' if '値不要' in kind else kind,
            min_bound='', max_bound='', help=' '.join(unique(r['EXE内の根拠'] for r in rows)),
            description=candidate['内容'] if candidate else row['内容'],
            confidence=candidate['判定'] if candidate else row['今回の区分'],
            category=candidate['用途の分類'] if candidate else '拡張候補の対象外',
            deprecated=False, internal=not bool(candidate), recommendation=0 if candidate else 1,
            cfg=False, format=name + ('' if '値不要' in kind else ('{value}' if name.endswith('=') else ' {value}')),
            candidate=bool(candidate), example=candidate['入力例'] if candidate else row['入力例'],
            uncertain=uncertain,
            reasons=unique(r['理由（今回）'] for r in rows),
            notes=unique(([candidate['注意']] if candidate else []) + [r[key] for r in rows for key in ('使用可否の評価', '判定上の注意', 'Windows実機での動作')]),
            sources=sources, registrations=len(rows),
        ))
    return options


if __name__ == '__main__':
    options = build(read('all.csv'), read('candidates.csv'))
    target = root / 'public/data/registrations.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(options, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print(f'Prepared {len(options)} options ({sum(o["candidate"] for o in options)} candidates)')
