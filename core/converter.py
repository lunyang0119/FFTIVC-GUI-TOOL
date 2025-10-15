"""
NXD/PZD 변환 모듈
"""
from pathlib import Path
from core.ff16tools_wrapper import FF16ToolsWrapper
from core.ffttic_wrapper import FFTTicNXDTextWrapper
from core.config_manager import get_config_manager
from utils.logger import get_logger


class Converter:
    """NXD/PZD 파일 변환 클래스"""

    def __init__(self):
        """변환기 초기화"""
        self.logger = get_logger()
        self.config = get_config_manager()

        # 외부 도구 래퍼 초기화
        ff16tools_path = self.config.get_ff16tools_path()
        ffttic_path = self.config.get_ffttic_nxdtext_path()

        self.ff16tools = None
        self.ffttic = None

        if ff16tools_path:
            try:
                self.ff16tools = FF16ToolsWrapper(ff16tools_path)
            except Exception as e:
                self.logger.error(f"FF16Tools 초기화 실패: {e}")

        if ffttic_path:
            try:
                self.ffttic = FFTTicNXDTextWrapper(ffttic_path)
            except Exception as e:
                self.logger.error(f"ffttic-nxdtext 초기화 실패: {e}")

    def convert_nxd_to_json(self, folder_path, recursive=True):
        """
        폴더 내 모든 NXD 파일을 JSON으로 변환

        Args:
            folder_path: 폴더 경로
            recursive: 하위 폴더 포함 여부

        Returns:
            변환된 파일 수
        """
        if not self.ffttic:
            self.logger.error("ffttic-nxdtext가 초기화되지 않음")
            return 0

        folder = Path(folder_path)
        if recursive:
            nxd_files = list(folder.rglob('*.nxd'))
        else:
            nxd_files = list(folder.glob('*.nxd'))

        self.logger.info(f"총 {len(nxd_files)}개 NXD 파일 변환 시작")

        success_count = 0
        for nxd_file in nxd_files:
            try:
                json_output = nxd_file.with_suffix('.json')
                if self.ffttic.nxd_to_json(nxd_file, json_output):
                    success_count += 1
                    self.logger.info(f"NXD → JSON 변환 완료: {nxd_file.name}")
                else:
                    self.logger.error(f"NXD → JSON 변환 실패: {nxd_file.name}")
            except Exception as e:
                self.logger.error(f"NXD 변환 오류 ({nxd_file}): {e}")

        self.logger.info(f"NXD → JSON 변환 완료: {success_count}/{len(nxd_files)}")
        return success_count

    def convert_json_to_nxd(self, folder_path, recursive=True):
        """
        폴더 내 모든 JSON 파일을 NXD로 변환 (원본 NXD 필요)

        Args:
            folder_path: 폴더 경로
            recursive: 하위 폴더 포함 여부

        Returns:
            변환된 파일 수
        """
        if not self.ffttic:
            self.logger.error("ffttic-nxdtext가 초기화되지 않음")
            return 0

        folder = Path(folder_path)
        if recursive:
            json_files = list(folder.rglob('*.json'))
        else:
            json_files = list(folder.glob('*.json'))

        self.logger.info(f"총 {len(json_files)}개 JSON 파일 변환 시작")

        success_count = 0
        for json_file in json_files:
            try:
                # 원본 NXD 파일 찾기
                original_nxd = json_file.with_suffix('.nxd')

                if not original_nxd.exists():
                    self.logger.warning(f"원본 NXD 파일 없음: {original_nxd}")
                    continue

                # 임시 출력 파일
                temp_nxd = json_file.with_suffix('.new.nxd')

                if self.ffttic.json_to_nxd(original_nxd, json_file, temp_nxd):
                    # 성공하면 원본 NXD 교체
                    temp_nxd.replace(original_nxd)
                    success_count += 1
                    self.logger.info(f"JSON → NXD 변환 완료: {json_file.name}")
                else:
                    self.logger.error(f"JSON → NXD 변환 실패: {json_file.name}")

            except Exception as e:
                self.logger.error(f"JSON 변환 오류 ({json_file}): {e}")

        self.logger.info(f"JSON → NXD 변환 완료: {success_count}/{len(json_files)}")
        return success_count

    def convert_pzd_to_yaml(self, folder_path, recursive=True):
        """
        폴더 내 모든 PZD 파일을 YAML로 변환

        Args:
            folder_path: 폴더 경로
            recursive: 하위 폴더 포함 여부

        Returns:
            변환된 파일 수
        """
        if not self.ff16tools:
            self.logger.error("FF16Tools가 초기화되지 않음")
            return 0

        folder = Path(folder_path)
        if recursive:
            pzd_files = list(folder.rglob('*.pzd'))
        else:
            pzd_files = list(folder.glob('*.pzd'))

        self.logger.info(f"총 {len(pzd_files)}개 PZD 파일 변환 시작")

        success_count = 0
        for pzd_file in pzd_files:
            try:
                if self.ff16tools.pzd_to_yaml(pzd_file):
                    success_count += 1
                    self.logger.info(f"PZD → YAML 변환 완료: {pzd_file.name}")
                else:
                    self.logger.error(f"PZD → YAML 변환 실패: {pzd_file.name}")
            except Exception as e:
                self.logger.error(f"PZD 변환 오류 ({pzd_file}): {e}")

        self.logger.info(f"PZD → YAML 변환 완료: {success_count}/{len(pzd_files)}")
        return success_count

    def convert_yaml_to_pzd(self, folder_path, recursive=True):
        """
        폴더 내 모든 YAML 파일을 PZD로 변환

        Args:
            folder_path: 폴더 경로
            recursive: 하위 폴더 포함 여부

        Returns:
            변환된 파일 수
        """
        if not self.ff16tools:
            self.logger.error("FF16Tools가 초기화되지 않음")
            return 0

        folder = Path(folder_path)
        if recursive:
            yaml_files = list(folder.rglob('*.yaml'))
        else:
            yaml_files = list(folder.glob('*.yaml'))

        self.logger.info(f"총 {len(yaml_files)}개 YAML 파일 변환 시작")

        success_count = 0
        for yaml_file in yaml_files:
            try:
                if self.ff16tools.yaml_to_pzd(yaml_file):
                    success_count += 1
                    self.logger.info(f"YAML → PZD 변환 완료: {yaml_file.name}")
                else:
                    self.logger.error(f"YAML → PZD 변환 실패: {yaml_file.name}")
            except Exception as e:
                self.logger.error(f"YAML 변환 오류 ({yaml_file}): {e}")

        self.logger.info(f"YAML → PZD 변환 완료: {success_count}/{len(yaml_files)}")
        return success_count
