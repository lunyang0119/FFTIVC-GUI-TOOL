"""
ffttic-nxdtext 래퍼 클래스
"""
import subprocess
from pathlib import Path
from utils.logger import get_logger


class FFTTicNXDTextWrapper:
    """ffttic-nxdtext 실행을 위한 래퍼 클래스"""

    def __init__(self, exe_path):
        """
        ffttic-nxdtext 래퍼 초기화

        Args:
            exe_path: ffttic-nxdtext.exe 경로
        """
        self.exe_path = Path(exe_path)
        self.logger = get_logger()

        if not self.exe_path.exists():
            self.logger.error(f"ffttic-nxdtext를 찾을 수 없음: {exe_path}")
            raise FileNotFoundError(f"ffttic-nxdtext를 찾을 수 없음: {exe_path}")

    def run_command(self, args, callback=None):
        """
        ffttic-nxdtext 명령 실행

        Args:
            args: 명령어 인자 리스트
            callback: 출력을 받을 콜백 함수

        Returns:
            반환 코드 (0: 성공, 그 외: 실패)
        """
        cmd = [str(self.exe_path)] + args
        self.logger.info(f"ffttic-nxdtext 실행: {' '.join(cmd)}")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )

            # 실시간 출력
            for line in process.stdout:
                line = line.strip()
                if line:
                    self.logger.debug(f"ffttic-nxdtext: {line}")
                    if callback:
                        callback(line)

            # 에러 출력
            stderr_output = process.stderr.read()
            if stderr_output:
                self.logger.error(f"ffttic-nxdtext 에러: {stderr_output}")
                if callback:
                    callback(f"ERROR: {stderr_output}")

            process.wait()
            self.logger.info(f"ffttic-nxdtext 종료 코드: {process.returncode}")
            return process.returncode

        except Exception as e:
            self.logger.error(f"ffttic-nxdtext 실행 실패: {e}")
            if callback:
                callback(f"실행 실패: {e}")
            return -1

    def nxd_to_json(self, nxd_file, output_json=None):
        """
        NXD 파일을 JSON으로 변환

        Args:
            nxd_file: NXD 파일 경로
            output_json: 출력 JSON 파일 경로 (None이면 자동 생성)

        Returns:
            성공 여부
        """
        if output_json is None:
            output_json = Path(nxd_file).with_suffix('.json')

        args = ['export', str(nxd_file), '--out-json', str(output_json)]
        return self.run_command(args) == 0

    def json_to_nxd(self, original_nxd, json_file, output_nxd=None):
        """
        JSON 파일을 NXD로 변환 (원본 NXD 파일 필요)

        Args:
            original_nxd: 원본 NXD 파일 경로
            json_file: JSON 파일 경로
            output_nxd: 출력 NXD 파일 경로 (None이면 원본 덮어쓰기)

        Returns:
            성공 여부
        """
        if output_nxd is None:
            output_nxd = original_nxd

        args = ['import', str(original_nxd), '--json', str(json_file), '--out', str(output_nxd)]
        return self.run_command(args) == 0
