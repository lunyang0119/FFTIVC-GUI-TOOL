"""
CSV 검증 모듈
"""
import re
import pandas as pd
from pathlib import Path
from utils.logger import get_logger


class CSVValidator:
    """CSV 파일 검증 클래스"""

    # 일본어 문자 패턴
    JAPANESE_PATTERNS = {
        'fullwidth': r'[！-～]',        # 전각 문자
        'kanji': r'[\u4e00-\u9fff]',    # 한자
        'hiragana': r'[\u3040-\u309f]', # 히라가나
        'katakana': r'[\u30a0-\u30ff]'  # 가타카나
    }

    def __init__(self):
        """검증기 초기화"""
        self.logger = get_logger()

    def validate_csv(self, csv_folder):
        """
        CSV 파일들에서 일본어 문자 검증

        Args:
            csv_folder: 검증할 CSV 폴더 경로

        Returns:
            검증 결과 리스트 [{file, row, issues, text}, ...]
        """
        results = []
        csv_files = list(Path(csv_folder).glob('*.csv'))

        self.logger.info(f"총 {len(csv_files)}개 CSV 파일 검증 시작")

        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, encoding='utf-8-sig')

                # Translation 열이 없으면 건너뛰기
                if 'Translation' not in df.columns:
                    self.logger.warning(f"Translation 열이 없음: {csv_file}")
                    continue

                for idx, row in df.iterrows():
                    translated = str(row['Translation'])

                    # NaN이거나 빈 문자열이면 건너뛰기
                    if pd.isna(row['Translation']) or not translated.strip():
                        continue

                    issues = []

                    # 각 패턴별로 검사
                    if re.search(self.JAPANESE_PATTERNS['fullwidth'], translated):
                        issues.append('전각문자')
                    if re.search(self.JAPANESE_PATTERNS['kanji'], translated):
                        issues.append('한자')
                    if re.search(self.JAPANESE_PATTERNS['hiragana'], translated):
                        issues.append('히라가나')
                    if re.search(self.JAPANESE_PATTERNS['katakana'], translated):
                        issues.append('가타카나')

                    if issues:
                        results.append({
                            'file': csv_file.name,
                            'row': idx + 2,  # +2 (헤더 + 0-based)
                            'issues': ', '.join(issues),
                            'text': translated[:100]  # 처음 100자만
                        })

                self.logger.info(f"검증 완료: {csv_file.name}")

            except Exception as e:
                self.logger.error(f"CSV 검증 실패 ({csv_file}): {e}")

        self.logger.info(f"검증 완료. 총 {len(results)}개 문제 발견")
        return results

    def save_validation_result(self, results, output_file):
        """
        검증 결과를 TXT 파일로 저장

        Args:
            results: 검증 결과 리스트
            output_file: 출력 파일 경로

        Returns:
            성공 여부
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("CSV 일본어 문자 검증 결과\n")
                f.write("=" * 80 + "\n\n")

                if not results:
                    f.write("문제가 발견되지 않았습니다.\n")
                else:
                    f.write(f"총 {len(results)}개의 문제가 발견되었습니다.\n\n")

                    for result in results:
                        f.write(f"파일: {result['file']}\n")
                        f.write(f"행 번호: {result['row']}\n")
                        f.write(f"문제: {result['issues']}\n")
                        f.write(f"내용: {result['text']}\n")
                        f.write("-" * 80 + "\n\n")

            self.logger.info(f"검증 결과 저장 완료: {output_file}")
            return True

        except Exception as e:
            self.logger.error(f"검증 결과 저장 실패: {e}")
            return False

    def get_validation_summary(self, results):
        """
        검증 결과 요약 생성

        Args:
            results: 검증 결과 리스트

        Returns:
            요약 문자열
        """
        if not results:
            return "문제가 발견되지 않았습니다."

        # 파일별, 문제별 통계
        file_stats = {}
        issue_stats = {
            '전각문자': 0,
            '한자': 0,
            '히라가나': 0,
            '가타카나': 0
        }

        for result in results:
            # 파일별 통계
            file_name = result['file']
            if file_name not in file_stats:
                file_stats[file_name] = 0
            file_stats[file_name] += 1

            # 문제별 통계
            for issue in result['issues'].split(', '):
                if issue in issue_stats:
                    issue_stats[issue] += 1

        summary = f"총 {len(results)}개의 문제가 발견되었습니다.\n\n"
        summary += "파일별 문제 수:\n"
        for file_name, count in sorted(file_stats.items()):
            summary += f"  - {file_name}: {count}개\n"

        summary += "\n문제 유형별 통계:\n"
        for issue_type, count in issue_stats.items():
            if count > 0:
                summary += f"  - {issue_type}: {count}개\n"

        return summary

    def get_detailed_validation_text(self, results):
        """
        검증 결과를 상세 텍스트로 생성

        Args:
            results: 검증 결과 리스트

        Returns:
            상세 결과 문자열
        """
        if not results:
            return "문제가 발견되지 않았습니다."

        text = f"총 {len(results)}개의 문제가 발견되었습니다.\n\n"
        text += "=" * 80 + "\n\n"

        current_file = None
        for result in results:
            # 파일이 바뀔 때마다 파일명 표시
            if current_file != result['file']:
                current_file = result['file']
                text += f"\n[파일: {current_file}]\n"
                text += "-" * 80 + "\n"

            # 행별 문제 표시
            text += f"  행 {result['row']}: {result['issues']}\n"
            text += f"    내용: {result['text'][:80]}...\n\n"

        return text
