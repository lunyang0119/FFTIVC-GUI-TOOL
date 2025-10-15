"""
NXD/PZD 변환 모듈
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing
from core.ff16tools_wrapper import FF16ToolsWrapper
from core.ffttic_wrapper import FFTTicNXDTextWrapper
from core.config_manager import get_config_manager
from utils.logger import get_logger


class Converter:
    """NXD/PZD 파일 변환 클래스"""

    def __init__(self, max_workers=None):
        """변환기 초기화

        Args:
            max_workers: 병렬 처리에 사용할 최대 워커 수 (기본값: CPU 코어 수)
        """
        self.logger = get_logger()
        self.config = get_config_manager()

        # 외부 도구 래퍼 초기화
        ff16tools_path = self.config.get_ff16tools_path()
        ffttic_path = self.config.get_ffttic_nxdtext_path()

        self.ff16tools = None
        self.ffttic = None
        self.ff16tools_path = ff16tools_path
        self.ffttic_path = ffttic_path

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

        # 워커 수 설정 (CPU 코어 수, 최소 2, 최대 8)
        if max_workers is None:
            cpu_count = multiprocessing.cpu_count()
            self.max_workers = min(max(cpu_count, 2), 8)
        else:
            self.max_workers = max_workers

        self.logger.info(f"병렬 처리 워커 수: {self.max_workers}")

    def _convert_single_nxd_to_json(self, nxd_file):
        """
        단일 NXD 파일을 JSON으로 변환 (병렬 처리용)

        Args:
            nxd_file: NXD 파일 경로

        Returns:
            (성공 여부, 파일명)
        """
        try:
            # 각 스레드에서 새로운 ffttic 인스턴스 생성
            ffttic = FFTTicNXDTextWrapper(self.ffttic_path)
            json_output = nxd_file.with_suffix('.json')
            if ffttic.nxd_to_json(nxd_file, json_output):
                return (True, nxd_file.name)
            else:
                return (False, nxd_file.name)
        except Exception as e:
            self.logger.error(f"NXD 변환 오류 ({nxd_file}): {e}")
            return (False, nxd_file.name)

    def convert_nxd_to_json(self, folder_path, recursive=True, callback=None):
        """
        폴더 내 모든 NXD 파일을 JSON으로 변환 (병렬 처리)

        Args:
            folder_path: 폴더 경로
            recursive: 하위 폴더 포함 여부
            callback: 진행 상황 콜백 함수 (processed, total) 인자 받음

        Returns:
            변환된 파일 수
        """
        if not self.ffttic_path:
            self.logger.error("ffttic-nxdtext가 초기화되지 않음")
            return 0

        folder = Path(folder_path)
        if recursive:
            nxd_files = list(folder.rglob('*.nxd'))
        else:
            nxd_files = list(folder.glob('*.nxd'))

        total_files = len(nxd_files)
        self.logger.info(f"총 {total_files}개 NXD 파일 변환 시작 (병렬 처리: {self.max_workers} 워커)")

        success_count = 0
        processed = 0

        # 병렬 처리
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 모든 작업 제출
            future_to_file = {executor.submit(self._convert_single_nxd_to_json, nxd_file): nxd_file
                            for nxd_file in nxd_files}

            # 완료된 작업 처리
            for future in as_completed(future_to_file):
                processed += 1
                success, filename = future.result()
                if success:
                    success_count += 1
                    self.logger.debug(f"[{processed}/{total_files}] NXD → JSON 변환 완료: {filename}")
                else:
                    self.logger.error(f"[{processed}/{total_files}] NXD → JSON 변환 실패: {filename}")

                # 진행 상황 콜백
                if callback:
                    callback(processed, total_files)

        self.logger.info(f"NXD → JSON 변환 완료: {success_count}/{total_files}")
        return success_count

    def _convert_single_json_to_nxd(self, json_file):
        """
        단일 JSON 파일을 NXD로 변환 (병렬 처리용)

        Args:
            json_file: JSON 파일 경로

        Returns:
            (성공 여부, 파일명)
        """
        try:
            # 원본 NXD 파일 찾기
            original_nxd = json_file.with_suffix('.nxd')

            if not original_nxd.exists():
                self.logger.warning(f"원본 NXD 파일 없음: {original_nxd}")
                return (False, json_file.name)

            # 각 스레드에서 새로운 ffttic 인스턴스 생성
            ffttic = FFTTicNXDTextWrapper(self.ffttic_path)

            # 임시 출력 파일
            temp_nxd = json_file.with_suffix('.new.nxd')

            if ffttic.json_to_nxd(original_nxd, json_file, temp_nxd):
                # 성공하면 원본 NXD 교체
                temp_nxd.replace(original_nxd)
                return (True, json_file.name)
            else:
                return (False, json_file.name)

        except Exception as e:
            self.logger.error(f"JSON 변환 오류 ({json_file}): {e}")
            return (False, json_file.name)

    def convert_json_to_nxd(self, folder_path, recursive=True, callback=None):
        """
        폴더 내 모든 JSON 파일을 NXD로 변환 (병렬 처리, 원본 NXD 필요)

        Args:
            folder_path: 폴더 경로
            recursive: 하위 폴더 포함 여부
            callback: 진행 상황 콜백 함수 (processed, total) 인자 받음

        Returns:
            변환된 파일 수
        """
        if not self.ffttic_path:
            self.logger.error("ffttic-nxdtext가 초기화되지 않음")
            return 0

        folder = Path(folder_path)
        if recursive:
            json_files = list(folder.rglob('*.json'))
        else:
            json_files = list(folder.glob('*.json'))

        total_files = len(json_files)
        self.logger.info(f"총 {total_files}개 JSON 파일 변환 시작 (병렬 처리: {self.max_workers} 워커)")

        success_count = 0
        processed = 0

        # 병렬 처리
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 모든 작업 제출
            future_to_file = {executor.submit(self._convert_single_json_to_nxd, json_file): json_file
                            for json_file in json_files}

            # 완료된 작업 처리
            for future in as_completed(future_to_file):
                processed += 1
                success, filename = future.result()
                if success:
                    success_count += 1
                    self.logger.debug(f"[{processed}/{total_files}] JSON → NXD 변환 완료: {filename}")
                else:
                    self.logger.error(f"[{processed}/{total_files}] JSON → NXD 변환 실패: {filename}")

                # 진행 상황 콜백
                if callback:
                    callback(processed, total_files)

        self.logger.info(f"JSON → NXD 변환 완료: {success_count}/{total_files}")
        return success_count

    def _convert_single_pzd_to_yaml(self, pzd_file):
        """
        단일 PZD 파일을 YAML로 변환 (병렬 처리용)

        Args:
            pzd_file: PZD 파일 경로

        Returns:
            (성공 여부, 파일명)
        """
        try:
            # 각 스레드에서 새로운 FF16Tools 인스턴스 생성
            ff16tools = FF16ToolsWrapper(self.ff16tools_path)
            if ff16tools.pzd_to_yaml(pzd_file):
                return (True, pzd_file.name)
            else:
                return (False, pzd_file.name)
        except Exception as e:
            self.logger.error(f"PZD 변환 오류 ({pzd_file}): {e}")
            return (False, pzd_file.name)

    def convert_pzd_to_yaml(self, folder_path, recursive=True, callback=None):
        """
        폴더 내 모든 PZD 파일을 YAML로 변환 (병렬 처리)

        Args:
            folder_path: 폴더 경로
            recursive: 하위 폴더 포함 여부
            callback: 진행 상황 콜백 함수 (processed, total) 인자 받음

        Returns:
            변환된 파일 수
        """
        if not self.ff16tools_path:
            self.logger.error("FF16Tools가 초기화되지 않음")
            return 0

        folder = Path(folder_path)
        if recursive:
            pzd_files = list(folder.rglob('*.pzd'))
        else:
            pzd_files = list(folder.glob('*.pzd'))

        total_files = len(pzd_files)
        self.logger.info(f"총 {total_files}개 PZD 파일 변환 시작 (병렬 처리: {self.max_workers} 워커)")

        success_count = 0
        processed = 0

        # 병렬 처리
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 모든 작업 제출
            future_to_file = {executor.submit(self._convert_single_pzd_to_yaml, pzd_file): pzd_file
                            for pzd_file in pzd_files}

            # 완료된 작업 처리
            for future in as_completed(future_to_file):
                processed += 1
                success, filename = future.result()
                if success:
                    success_count += 1
                    self.logger.debug(f"[{processed}/{total_files}] PZD → YAML 변환 완료: {filename}")
                else:
                    self.logger.error(f"[{processed}/{total_files}] PZD → YAML 변환 실패: {filename}")

                # 진행 상황 콜백
                if callback:
                    callback(processed, total_files)

        self.logger.info(f"PZD → YAML 변환 완료: {success_count}/{total_files}")
        return success_count

    def _convert_single_yaml_to_pzd(self, yaml_file):
        """
        단일 YAML 파일을 PZD로 변환 (병렬 처리용)

        Args:
            yaml_file: YAML 파일 경로

        Returns:
            (성공 여부, 파일명)
        """
        try:
            # 각 스레드에서 새로운 FF16Tools 인스턴스 생성
            ff16tools = FF16ToolsWrapper(self.ff16tools_path)
            if ff16tools.yaml_to_pzd(yaml_file):
                return (True, yaml_file.name)
            else:
                return (False, yaml_file.name)
        except Exception as e:
            self.logger.error(f"YAML 변환 오류 ({yaml_file}): {e}")
            return (False, yaml_file.name)

    def convert_yaml_to_pzd(self, folder_path, recursive=True, callback=None):
        """
        폴더 내 모든 YAML 파일을 PZD로 변환 (병렬 처리)

        Args:
            folder_path: 폴더 경로
            recursive: 하위 폴더 포함 여부
            callback: 진행 상황 콜백 함수 (processed, total) 인자 받음

        Returns:
            변환된 파일 수
        """
        if not self.ff16tools_path:
            self.logger.error("FF16Tools가 초기화되지 않음")
            return 0

        folder = Path(folder_path)
        if recursive:
            yaml_files = list(folder.rglob('*.yaml'))
        else:
            yaml_files = list(folder.glob('*.yaml'))

        total_files = len(yaml_files)
        self.logger.info(f"총 {total_files}개 YAML 파일 변환 시작 (병렬 처리: {self.max_workers} 워커)")

        success_count = 0
        processed = 0

        # 병렬 처리
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 모든 작업 제출
            future_to_file = {executor.submit(self._convert_single_yaml_to_pzd, yaml_file): yaml_file
                            for yaml_file in yaml_files}

            # 완료된 작업 처리
            for future in as_completed(future_to_file):
                processed += 1
                success, filename = future.result()
                if success:
                    success_count += 1
                    self.logger.debug(f"[{processed}/{total_files}] YAML → PZD 변환 완료: {filename}")
                else:
                    self.logger.error(f"[{processed}/{total_files}] YAML → PZD 변환 실패: {filename}")

                # 진행 상황 콜백
                if callback:
                    callback(processed, total_files)

        self.logger.info(f"YAML → PZD 변환 완료: {success_count}/{total_files}")
        return success_count
