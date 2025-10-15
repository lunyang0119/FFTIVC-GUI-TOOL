"""
CSV 처리 모듈
"""
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

    def apply_csv_to_json(self, csv_file, json_folder):
        """
        CSV의 번역을 JSON 파일에 적용

        Args:
            csv_file: CSV 파일 경로
            json_folder: JSON 파일이 있는 폴더

        Returns:
            성공 여부
        """
        try:
            df = pd.read_csv(csv_file, encoding='utf-8-sig')

            # 파일별로 그룹화
            for source_file, group in df.groupby('FileName'):
                json_path = self._find_file_recursive(json_folder, source_file)

                if not json_path:
                    self.logger.warning(f"파일을 찾을 수 없음: {source_file}")
                    continue

                # JSON 파일 로드
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 번역 적용
                for _, row in group.iterrows():
                    entry_id = row['EntryID']
                    translated = row['Translation']

                    if pd.notna(translated) and str(translated).strip():
                        data[entry_id] = str(translated)

                # JSON 저장
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                self.logger.info(f"JSON 파일 업데이트 완료: {json_path}")

            return True

        except Exception as e:
            self.logger.error(f"CSV → JSON 적용 실패: {e}")
            return False

    def apply_csv_to_yaml(self, csv_file, yaml_folder):
        """
        CSV의 번역을 YAML 파일에 적용

        Args:
            csv_file: CSV 파일 경로
            yaml_folder: YAML 파일이 있는 폴더

        Returns:
            성공 여부
        """
        try:
            df = pd.read_csv(csv_file, encoding='utf-8-sig')

            # 파일별로 그룹화
            for source_file, group in df.groupby('FileName'):
                yaml_path = self._find_file_recursive(yaml_folder, source_file)

                if not yaml_path:
                    self.logger.warning(f"파일을 찾을 수 없음: {source_file}")
                    continue

                # YAML 파일 로드
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)

                # 번역 적용
                for _, row in group.iterrows():
                    entry_id = int(row['EntryID'])
                    translated = row['Translation']

                    if pd.notna(translated) and str(translated).strip():
                        for entry in data:
                            if entry.get('Id') == entry_id:
                                entry['Line'] = str(translated)
                                break

                # YAML 저장
                with open(yaml_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, allow_unicode=True, sort_keys=False)

                self.logger.info(f"YAML 파일 업데이트 완료: {yaml_path}")

            return True

        except Exception as e:
            self.logger.error(f"CSV → YAML 적용 실패: {e}")
            return False

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
