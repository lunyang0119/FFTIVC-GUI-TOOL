"""
CSV 처리 모듈
"""
import csv
import json
import yaml
import pandas as pd
from pathlib import Path
from glob import glob
from utils.logger import get_logger


class CSVHandler:
    """CSV 생성 및 적용을 위한 클래스"""

    def __init__(self):
        """CSV 핸들러 초기화"""
        self.logger = get_logger()

    def extract_from_json(self, json_files):
        """
        JSON 파일에서 데이터 추출하여 CSV 형식으로 변환

        Args:
            json_files: JSON 파일 경로 리스트

        Returns:
            CSV 데이터 리스트 (딕셔너리 리스트)
        """
        all_data = []
        text_counter = 1

        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                filename = Path(json_file).name

                # JSON은 key-value 쌍 (예: "achievement/1/6": "텍스트")
                for key, value in data.items():
                    if value and str(value).strip():  # 빈 값이 아닌 경우만
                        all_data.append({
                            'Tag': f'<text{text_counter}>',
                            'FileName': filename,
                            'EntryID': key,
                            'OriginalText': str(value),
                            'Translation': ''
                        })
                        text_counter += 1

                self.logger.info(f"JSON 파일 처리 완료: {filename}")

            except Exception as e:
                self.logger.error(f"JSON 파일 처리 실패 ({json_file}): {e}")

        return all_data

    def extract_from_yaml(self, yaml_files, group_by_folder=True):
        """
        YAML 파일에서 데이터 추출하여 CSV 형식으로 변환

        Args:
            yaml_files: YAML 파일 경로 리스트
            group_by_folder: 폴더별로 그룹화 여부

        Returns:
            폴더별 CSV 데이터 딕셔너리 {폴더명: 데이터 리스트}
        """
        if not group_by_folder:
            # 폴더별 그룹화 없이 하나의 CSV로
            return {'all': self._extract_yaml_files(yaml_files)}

        # 폴더별로 그룹화
        folder_groups = {}

        for yaml_file in yaml_files:
            folder_name = Path(yaml_file).parent.name
            if folder_name not in folder_groups:
                folder_groups[folder_name] = []
            folder_groups[folder_name].append(yaml_file)

        # 각 폴더별로 CSV 생성
        all_csvs = {}
        for folder_name, files in folder_groups.items():
            all_csvs[folder_name] = self._extract_yaml_files(files)

        return all_csvs

    def _extract_yaml_files(self, yaml_files):
        """
        YAML 파일 리스트에서 데이터 추출

        Args:
            yaml_files: YAML 파일 경로 리스트

        Returns:
            CSV 데이터 리스트
        """
        all_data = []
        text_counter = 1

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)

                filename = Path(yaml_file).name

                # YAML은 리스트 형태 [{Id: 123, Line: "텍스트"}, ...]
                if isinstance(data, list):
                    for entry in data:
                        if isinstance(entry, dict) and 'Id' in entry and 'Line' in entry:
                            line = entry['Line']
                            if line and str(line).strip():
                                all_data.append({
                                    'Tag': f'<text{text_counter}>',
                                    'FileName': filename,
                                    'EntryID': entry['Id'],
                                    'OriginalText': str(line),
                                    'Translation': ''
                                })
                                text_counter += 1

                self.logger.info(f"YAML 파일 처리 완료: {filename}")

            except Exception as e:
                self.logger.error(f"YAML 파일 처리 실패 ({yaml_file}): {e}")

        return all_data

    def generate_csvs(self, source_folder, output_folder, recursive=True):
        """
        JSON과 YAML을 스캔하여 CSV 생성

        Args:
            source_folder: 소스 폴더 경로
            output_folder: 출력 폴더 경로
            recursive: 하위 폴더 포함 여부

        Returns:
            생성된 CSV 파일 수
        """
        source_path = Path(source_folder)
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)

        csv_count = 0

        # JSON 파일 처리 (파일명별로 CSV)
        if recursive:
            json_files = list(source_path.rglob('*.json'))
        else:
            json_files = list(source_path.glob('*.json'))

        for json_file in json_files:
            data = self.extract_from_json([json_file])
            if data:
                csv_name = json_file.stem + '.csv'
                csv_path = output_path / csv_name
                self.save_to_csv(data, csv_path)
                csv_count += 1

        # YAML 파일 처리 (폴더명별로 CSV)
        if recursive:
            yaml_files = list(source_path.rglob('*.yaml'))
        else:
            yaml_files = list(source_path.glob('*.yaml'))

        folder_csvs = self.extract_from_yaml(yaml_files, group_by_folder=True)
        for folder_name, data in folder_csvs.items():
            if data:
                csv_name = f"{folder_name}.csv"
                csv_path = output_path / csv_name
                self.save_to_csv(data, csv_path)
                csv_count += 1

        self.logger.info(f"총 {csv_count}개의 CSV 파일 생성 완료")
        return csv_count

    def save_to_csv(self, data, output_file):
        """
        데이터를 CSV 파일로 저장

        Args:
            data: CSV 데이터 (딕셔너리 리스트)
            output_file: 출력 파일 경로
        """
        try:
            df = pd.DataFrame(data)
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            self.logger.info(f"CSV 파일 저장 완료: {output_file}")
        except Exception as e:
            self.logger.error(f"CSV 파일 저장 실패 ({output_file}): {e}")

    def load_all_translations(self, csv_folder):
        """
        지정된 폴더 내의 모든 CSV 파일에서 번역 데이터를 로드합니다.
        FileName과 EntryID를 키로 사용하여 번역문을 저장합니다.
        EntryID는 JSON과 YAML 모두에 대응하기 위해 문자열로 저장됩니다.

        Args:
            csv_folder (str): CSV 파일이 있는 폴더 경로.

        Returns:
            dict: {(filename, str(entry_id)): translation} 형태의 딕셔너리.
        """
        translations = {}
        translated_count = 0
        original_fallback_count = 0

        csv_files = list(Path(csv_folder).rglob('*.csv'))
        if not csv_files:
            self.logger.warning(f"CSV 폴더 '{csv_folder}'에서 CSV 파일을 찾을 수 없습니다.")
            return translations

        self.logger.info(f"총 {len(csv_files)}개의 CSV 파일에서 데이터 로딩 시작...")

        for csv_file in csv_files:
            try:
                with open(csv_file, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        filename = row.get('FileName', '').strip()
                        entry_id = row.get('EntryID', '').strip()
                        translation = row.get('Translation', '')
                        original_text = row.get('OriginalText', '')

                        if filename and entry_id:
                            # 번역문이 있으면 번역문 사용
                            if translation and str(translation).strip():
                                translations[(filename, str(entry_id))] = str(translation)
                                translated_count += 1
                            # 번역문이 없으면 원문 사용 (폴백)
                            else:
                                translations[(filename, str(entry_id))] = str(original_text)
                                original_fallback_count += 1
                        else:
                            self.logger.warning(f"CSV 파일 '{csv_file.name}'에서 필수 컬럼(FileName, EntryID, Translation) 중 누락된 항목이 있습니다: {row}")

            except Exception as e:
                self.logger.error(f"CSV 파일 로드 중 오류 발생 ({csv_file}): {e}")

        self.logger.info(f"데이터 로딩 완료: 번역된 항목 {translated_count}개, 원문으로 대체된 항목 {original_fallback_count}개.")
        return translations

    def apply_translations_to_folder(self, source_folder, translations, apply_yaml=True, apply_json=True):
        """
        통합된 번역 데이터를 지정된 폴더 내의 YAML 및 JSON 파일에 적용합니다.

        Args:
            source_folder (str): YAML/JSON 파일이 있는 폴더 경로.
            translations (dict): {(filename, str(entry_id)): translation} 형태의 번역 딕셔너리.
            apply_yaml (bool): YAML 파일에 번역을 적용할지 여부.
            apply_json (bool): JSON 파일에 번역을 적용할지 여부.

        Returns:
            int: 총 업데이트된 항목 수.
        """
        source_path = Path(source_folder)
        updated_entries_count = 0

        if not source_path.exists():
            self.logger.error(f"원본 폴더를 찾을 수 없습니다: {source_folder}")
            return 0

        # YAML 파일에 번역 적용
        if apply_yaml:
            yaml_files = list(source_path.rglob('*.yaml'))
            self.logger.info(f"총 {len(yaml_files)}개의 YAML 파일에 번역 적용 시도...")
            for yaml_file_path in yaml_files:
                try:
                    with open(yaml_file_path, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)

                    if not isinstance(data, list):
                        self.logger.warning(f"YAML 파일 '{yaml_file_path.name}'의 형식이 예상과 다릅니다 (리스트 아님). 건너뜁니다.")
                        continue

                    filename = yaml_file_path.name
                    file_updated_count = 0
                    for entry in data:
                        if isinstance(entry, dict) and 'Id' in entry and 'Line' in entry:
                            entry_id = entry['Id'] # YAML EntryID는 보통 int
                            key = (filename, str(entry_id)) # 딕셔너리 키는 (filename, str(entry_id))

                            if key in translations:
                                translated_line = translations[key]
                                if str(translated_line).strip() and entry['Line'] != translated_line:
                                    entry['Line'] = str(translated_line)
                                    file_updated_count += 1
                    
                    if file_updated_count > 0:
                        with open(yaml_file_path, 'w', encoding='utf-8') as f:
                            yaml.dump(data, f, allow_unicode=True, sort_keys=False)
                        self.logger.info(f"YAML 파일 업데이트 완료: {yaml_file_path.name} ({file_updated_count} 항목)")
                        updated_entries_count += file_updated_count

                except Exception as e:
                    self.logger.error(f"YAML 파일 '{yaml_file_path}' 번역 적용 중 오류 발생: {e}")

        # JSON 파일에 번역 적용
        if apply_json:
            json_files = list(source_path.rglob('*.json'))
            self.logger.info(f"총 {len(json_files)}개의 JSON 파일에 번역 적용 시도...")
            for json_file_path in json_files:
                try:
                    with open(json_file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    if not isinstance(data, dict):
                        self.logger.warning(f"JSON 파일 '{json_file_path.name}'의 형식이 예상과 다릅니다 (딕셔너리 아님). 건너뜁니다.")
                        continue

                    filename = json_file_path.name
                    file_updated_count = 0
                    for entry_id_str, original_value in data.items():
                        key = (filename, entry_id_str) # JSON EntryID는 보통 str

                        if key in translations:
                            translated_value = translations[key]
                            if str(translated_value).strip() and original_value != translated_value:
                                data[entry_id_str] = str(translated_value)
                                file_updated_count += 1

                    if file_updated_count > 0:
                        with open(json_file_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        self.logger.info(f"JSON 파일 업데이트 완료: {json_file_path.name} ({file_updated_count} 항목)")
                        updated_entries_count += file_updated_count

                except Exception as e:
                    self.logger.error(f"JSON 파일 '{json_file_path}' 번역 적용 중 오류 발생: {e}")

        return updated_entries_count

    def _find_file_recursive(self, folder, filename):
        """
        폴더 내에서 파일을 재귀적으로 검색

        Args:
            folder: 검색할 폴더
            filename: 찾을 파일명

        Returns:
            파일 경로 (없으면 None)
        """
        folder_path = Path(folder)
        matches = list(folder_path.rglob(filename))
        return matches[0] if matches else None

    def batch_replace(self, csv_folder, find_text, replace_text, translated_only=False):
        """
        CSV 파일들에서 일괄 치환

        Args:
            csv_folder: CSV 폴더 경로
            find_text: 찾을 문자열
            replace_text: 바꿀 문자열
            translated_only: Translation 열만 변경할지 여부

        Returns:
            처리된 파일 수
        """
        csv_files = list(Path(csv_folder).glob('*.csv'))
        count = 0

        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, encoding='utf-8-sig')

                if translated_only:
                    df['Translation'] = df['Translation'].astype(str).str.replace(
                        find_text, replace_text, regex=False
                    )
                else:
                    df = df.astype(str).replace(find_text, replace_text, regex=False)

                df.to_csv(csv_file, index=False, encoding='utf-8-sig')
                self.logger.info(f"일괄 치환 완료: {csv_file}")
                count += 1

            except Exception as e:
                self.logger.error(f"일괄 치환 실패 ({csv_file}): {e}")

        return count
