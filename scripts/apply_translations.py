"""
번역된 CSV 파일을 읽어서 원본 YAML 파일의 대사를 업데이트합니다.

사용법:
    python apply_translations.py [translation_csv_path] [scenario_folder_path]

예시:
    python apply_translations.py "translation_completed.csv" "../data/enhanced/0004.ja/nxd/text/scenario"
"""

import yaml
import csv
import sys
from pathlib import Path
from collections import defaultdict


def load_translations_from_csv(csv_path):
    """
    CSV 파일에서 번역 데이터를 로드합니다.

    Args:
        csv_path: 번역된 CSV 파일 경로

    Returns:
        dict: {(filename, entry_id): translation} 형태의 딕셔너리
    """
    translations = {}
    skipped_count = 0
    loaded_count = 0

    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                filename = row['FileName']
                entry_id = int(row['EntryID'])
                translation = row['Translation'].strip()

                # 번역문이 있는 경우만 로드
                if translation:
                    translations[(filename, entry_id)] = translation
                    loaded_count += 1
                else:
                    skipped_count += 1

        print(f"Loaded {loaded_count} translations")
        print(f"Skipped {skipped_count} empty translations")
        return translations

    except Exception as e:
        print(f"Error loading CSV: {e}")
        return {}


def update_yaml_file(yaml_file_path, translations):
    """
    YAML 파일의 대사를 번역문으로 업데이트합니다.

    Args:
        yaml_file_path: YAML 파일 경로
        translations: 번역 딕셔너리

    Returns:
        int: 업데이트된 항목 수
    """
    try:
        # YAML 파일 읽기
        with open(yaml_file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not data:
            return 0

        filename = Path(yaml_file_path).name
        updated_count = 0

        # 각 항목의 Line 필드 업데이트
        for entry in data:
            if isinstance(entry, dict) and 'Id' in entry and 'Line' in entry:
                entry_id = entry['Id']
                key = (filename, entry_id)

                # 해당 항목의 번역이 있으면 업데이트
                if key in translations:
                    original_line = entry['Line']
                    translated_line = translations[key]

                    # 빈 대사가 아니고, 원문과 다른 경우만 업데이트
                    if original_line and original_line.strip() and original_line != translated_line:
                        entry['Line'] = translated_line
                        updated_count += 1

        # 업데이트된 내용을 파일에 저장
        if updated_count > 0:
            with open(yaml_file_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

        return updated_count

    except Exception as e:
        print(f"Error updating {yaml_file_path}: {e}")
        return 0


def apply_translations(scenario_folder, translations):
    """
    시나리오 폴더의 모든 YAML 파일에 번역을 적용합니다.

    Args:
        scenario_folder: 시나리오 폴더 경로
        translations: 번역 딕셔너리

    Returns:
        dict: 파일별 업데이트 통계
    """
    scenario_path = Path(scenario_folder)

    if not scenario_path.exists():
        print(f"Error: Folder not found: {scenario_folder}")
        return {}

    # 번역이 있는 파일명 추출
    files_to_update = set(filename for filename, _ in translations.keys())

    print(f"\nFiles to update: {len(files_to_update)}")

    stats = {}
    total_updated = 0

    for filename in sorted(files_to_update):
        yaml_file_path = scenario_path / filename

        if yaml_file_path.exists():
            print(f"Updating: {filename}...", end=" ")
            updated_count = update_yaml_file(yaml_file_path, translations)
            stats[filename] = updated_count
            total_updated += updated_count
            print(f"{updated_count} entries updated")
        else:
            print(f"Warning: File not found: {filename}")
            stats[filename] = 0

    print(f"\n{'='*60}")
    print(f"Total entries updated: {total_updated}")
    print(f"{'='*60}")

    return stats


def create_backup(scenario_folder):
    """
    시나리오 폴더를 백업합니다 (선택사항).

    Args:
        scenario_folder: 시나리오 폴더 경로
    """
    # 이 함수는 필요시 구현할 수 있습니다
    pass


def main():
    # 명령줄 인자 처리
    if len(sys.argv) >= 2:
        csv_path = sys.argv[1]
    else:
        csv_path = "translation_completed.csv"

    if len(sys.argv) >= 3:
        scenario_folder = sys.argv[2]
    else:
        # 기본값: 스크립트가 scripts 폴더에 있다고 가정
        script_dir = Path(__file__).parent
        scenario_folder = script_dir.parent / "data" / "enhanced" / "0004.ja" / "nxd" / "text" / "scenario"

    print("=" * 60)
    print("Game Scenario Translation Application Tool")
    print("=" * 60)
    print(f"Translation CSV: {csv_path}")
    print(f"Scenario folder: {scenario_folder}")
    print("=" * 60)
    print()

    # CSV에서 번역 로드
    translations = load_translations_from_csv(csv_path)

    if not translations:
        print("No translations found. Exiting.")
        return

    # 사용자 확인
    print(f"\nReady to update YAML files with {len(translations)} translations.")
    response = input("Continue? (y/n): ").strip().lower()

    if response != 'y':
        print("Operation cancelled.")
        return

    print()

    # 번역 적용
    stats = apply_translations(scenario_folder, translations)

    # 결과 요약
    if stats:
        print("\nUpdate Summary:")
        print("-" * 60)
        for filename, count in stats.items():
            if count > 0:
                print(f"  {filename}: {count} entries")


if __name__ == "__main__":
    main()
