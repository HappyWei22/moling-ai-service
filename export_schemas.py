"""导出当前 WorksheetPlan 协议；--check 只检查，不写文件。"""
import argparse
import json
from pathlib import Path
from schemas import WorksheetPlan


def schema_text():
    schema = WorksheetPlan.model_json_schema()
    # 只调整阅读顺序，不改变 Schema 含义。
    first = ('$schema', 'title', 'description', 'type', '$comment')
    ordered = {key: schema[key] for key in first if key in schema}
    ordered.update({key: value for key, value in schema.items() if key not in first})
    return json.dumps(ordered, ensure_ascii=False, indent=2) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='检查导出文件是否与模型一致')
    args = parser.parse_args()
    target = Path(__file__).parent / 'WorkSheetPlan' / 'worksheet_plan.schema.json'
    text = schema_text()
    if args.check:
        if not target.exists() or target.read_text(encoding='utf-8') != text:
            raise SystemExit('Schema 需要更新：请运行 python export_schemas.py')
        print('Schema 与模型一致')
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
        print(f'已导出：{target}')


if __name__ == '__main__':
    main()
