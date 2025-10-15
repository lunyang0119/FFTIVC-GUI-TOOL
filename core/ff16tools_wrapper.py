"""
FF16Tools 래퍼 클래스
"""
import subprocess
from pathlib import Path
from utils.logger import get_logger


class FF16ToolsWrapper:
    """FF16Tools 실행을 위한 래퍼 클래스"""

    def __init__(self, exe_path):
        """
        FF16Tools 래퍼 초기화

        Args:
            exe_path: FF16Tools.CLI.exe 경로
        """
        self.exe_path = Path(exe_path)
        self.logger = get_logger()

        if not self.exe_path.exists():
            self.logger.error(f"FF16Tools를 찾을 수 없음: {exe_path}")
            raise FileNotFoundError(f"FF16Tools를 찾을 수 없음: {exe_path}")

    def run_command(self, args, callback=None):
        """
        FF16Tools 명령 실행

        Args:
            args: 명령어 인자 리스트
            callback: 출력을 받을 콜백 함수

        Returns:
            반환 코드 (0: 성공, 그 외: 실패)
        """
        cmd = [str(self.exe_path)] + args
        self.logger.info(f"FF16Tools 실행: {' '.join(cmd)}")

        try:
            # Windows에서 CMD 창 숨기기
            import sys
            creationflags = 0
            if sys.platform == 'win32':
                creationflags = subprocess.CREATE_NO_WINDOW

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore',
                creationflags=creationflags
            )

            # 실시간 출력
            for line in process.stdout:
                line = line.strip()
                if line:
                    self.logger.debug(f"FF16Tools: {line}")
                    if callback:
                        callback(line)

            # 에러 출력
            stderr_output = process.stderr.read()
            if stderr_output:
                self.logger.error(f"FF16Tools 에러: {stderr_output}")

                # .NET 오류 감지
                if ".NET" in stderr_output or "dotnet" in stderr_output:
                    error_msg = "FF16Tools 실행 실패: .NET Runtime이 필요합니다.\n\n"
                    if "version '9.0.0'" in stderr_output:
                        error_msg += ".NET 9.0 Runtime을 설치해주세요.\n"
                        error_msg += "다운로드: https://dotnet.microsoft.com/download/dotnet/9.0"
                    else:
                        error_msg += "필요한 .NET Runtime을 설치해주세요.\n"
                        error_msg += stderr_output[:200]  # 처음 200자만

                    if callback:
                        callback(error_msg)
                else:
                    if callback:
                        callback(f"ERROR: {stderr_output}")

            process.wait()
            self.logger.info(f"FF16Tools 종료 코드: {process.returncode}")
            return process.returncode

        except Exception as e:
            self.logger.error(f"FF16Tools 실행 실패: {e}")
            if callback:
                callback(f"실행 실패: {e}")
            return -1

    def unpack_all(self, pac_file, output_folder, game='fft'):
        """
        PAC 파일 언팩

        Args:
            pac_file: 언팩할 PAC 파일 경로
            output_folder: 출력 폴더 경로
            game: 게임 종류 (fft 또는 ff16)

        Returns:
            성공 여부
        """
        args = ['unpack-all', '-i', str(pac_file), '-o', str(output_folder), '-g', game]
        return self.run_command(args) == 0

    def pack(self, input_folder, output_pac, game='fft'):
        """
        PAC 파일 팩

        Args:
            input_folder: 팩킹할 폴더 경로
            output_pac: 출력 PAC 파일 경로
            game: 게임 종류 (fft 또는 ff16)

        Returns:
            성공 여부
        """
        args = ['pack', '-i', str(input_folder), '-o', str(output_pac), '-g', game]
        return self.run_command(args) == 0

    def pzd_to_yaml(self, pzd_file, game='fft', callback=None):
        """
        PZD 파일을 YAML로 변환

        Args:
            pzd_file: PZD 파일 경로
            game: 사용 안 함 (pzd-to-yaml은 game type을 받지 않음)
            callback: 진행 상황 콜백

        Returns:
            성공 여부
        """
        pzd_path = Path(pzd_file)
        expected_yaml = pzd_path.with_suffix('.yaml')

        # 기존 YAML 파일 존재 확인
        if expected_yaml.exists():
            self.logger.debug(f"기존 YAML 파일 삭제: {expected_yaml}")
            expected_yaml.unlink()

        args = ['pzd-conv', '-i', str(pzd_file)]
        result = self.run_command(args, callback) == 0

        # 변환 후 YAML 파일 생성 확인
        if result and not expected_yaml.exists():
            self.logger.error(f"PZD 변환 성공했으나 YAML 파일이 생성되지 않음: {expected_yaml}")
            return False

        return result

    def yaml_to_pzd(self, yaml_file, game='fft'):
        """
        YAML 파일을 PZD로 변환

        Args:
            yaml_file: YAML 파일 경로
            game: 게임 종류 (fft 또는 ff16)

        Returns:
            성공 여부
        """
        args = ['pzd-conv', '-i', str(yaml_file), '-g', game]
        return self.run_command(args) == 0
