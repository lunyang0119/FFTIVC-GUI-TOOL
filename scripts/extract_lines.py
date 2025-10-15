"""
게임 시나리오 YAML 파일에서 대사를 추출하여 번역 작업용 CSV 파일을 생성합니다.

사용법:
    python extract_lines.py [scenario_folder_path] [output_csv_path]

예시:
    python extract_lines.py "../data/enhanced/0004.ja/nxd/text/scenario" "translation_work.csv"
"""

import yaml
import csv
import sys
from pathlib import Path


def extract_lines_from_yaml(yaml_file_path):
    """
    YAML 파일에서 모든 대사 항목을 추출합니다.

    Args:
        yaml_file_path: YAML 파일 경로

    Returns:
        list: (entry_id, line_text) 튜플의 리스트
    """
    try:
        with open(yaml_file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not data:
            return []

        lines = []
        for entry in data:
            if isinstance(entry, dict) and 'Line' in entry and 'Id' in entry:
                entry_id = entry['Id']
                line_text = entry['Line']

                # 빈 대사가 아닌 경우만 추가
                if line_text and line_text.strip():
                    lines.append((entry_id, line_text))

        return lines

    except Exception as e:
        print(f"Error processing {yaml_file_path}: {e}")
        return []


def extract_all_lines(scenario_folder):
    """
    시나리오 폴더의 모든 .ja.yaml 파일에서 대사를 추출합니다.

    Args:
        scenario_folder: 시나리오 파일이 있는 폴더 경로

    Returns:
        list: (tag, filename, entry_id, original_text) 튜플의 리스트
    """
    scenario_path = Path(scenario_folder)

    if not scenario_path.exists():
        print(f"Error: Folder not found: {scenario_folder}")
        return []

    # .ja.yaml 파일 찾기
    yaml_files = sorted(scenario_path.glob("*.ja.yaml"))

    if not yaml_files:
        print(f"Warning: No .ja.yaml files found in {scenario_folder}")
        return []

    print(f"Found {len(yaml_files)} YAML files")

    all_entries = []
    text_counter = 1

    for yaml_file in yaml_files:
        print(f"Processing: {yaml_file.name}")
        lines = extract_lines_from_yaml(yaml_file)

        for entry_id, line_text in lines:
            tag = f"<text{text_counter}>"
            all_entries.append({
                'Tag': tag,
                'FileName': yaml_file.name,
                'EntryID': entry_id,
                'OriginalText': line_text,
                'Translation': ''
            })
            text_counter += 1

    print(f"\nTotal lines extracted: {len(all_entries)}")
    return all_entries


def save_to_csv(entries, output_csv):
    """
    추출된 대사를 CSV 파일로 저장합니다.

    Args:
        entries: 대사 항목 리스트
        output_csv: 출력 CSV 파일 경로
    """
    if not entries:
        print("No entries to save.")
        return

    try:
        with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['Tag', 'FileName', 'EntryID', 'OriginalText', 'Translation']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(entries)

        print(f"\nSuccessfully saved to: {output_csv}")
        print(f"Total entries: {len(entries)}")

    except Exception as e:
        print(f"Error saving CSV: {e}")


def main():
    # 기본 경로 설정
    if len(sys.argv) >= 2:
        scenario_folder = sys.argv[1]
    else:
        # 기본값: 스크립트가 scripts 폴더에 있다고 가정
        script_dir = Path(__file__).parent
        scenario_folder = script_dir.parent / "data" / "enhanced" / "0004.ja" / "nxd" / "text" / "scenario"

    if len(sys.argv) >= 3:
        output_csv = sys.argv[2]
    else:
        output_csv = "translation_work.csv"

    print("=" * 60)
    print("Game Scenario Line Extraction Tool")
    print("=" * 60)
    print(f"Scenario folder: {scenario_folder}")
    print(f"Output CSV: {output_csv}")
    print("=" * 60)
    print()

    # 대사 추출
    entries = extract_all_lines(scenario_folder)

    # CSV 저장
    if entries:
        save_to_csv(entries, output_csv)


if __name__ == "__main__":
    main()
