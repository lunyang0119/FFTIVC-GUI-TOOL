"""
외부 도구 자동 탐지 모듈
"""
import os
from pathlib import Path
from utils.logger import get_logger


class ToolFinder:
    """외부 도구를 자동으로 찾는 클래스"""

    def __init__(self):
        """도구 찾기 초기화"""
        self.logger = get_logger()
        # 실행 파일의 위치를 기준으로 설정
        if getattr(sys, 'frozen', False):
            # PyInstaller로 패키징된 경우
            self.base_dir = Path(sys.executable).parent
        else:
            # 일반 Python 스크립트로 실행되는 경우
            self.base_dir = Path(__file__).parent.parent

    def find_ff16tools(self):
        """
        FF16Tools.CLI.exe 찾기

        Returns:
            FF16Tools.CLI.exe 경로 (str) 또는 None
        """
        # 1. ff16tools 폴더 내에서 찾기
        ff16tools_folder = self.base_dir / 'ff16tools'
        if ff16tools_folder.exists():
            exe_path = ff16tools_folder / 'FF16Tools.CLI.exe'
            if exe_path.exists():
                self.logger.info(f"FF16Tools 찾음: {exe_path}")
                return str(exe_path)

        # 2. FF16Tools 폴더 (대문자) 확인
        ff16tools_folder_upper = self.base_dir / 'FF16Tools'
        if ff16tools_folder_upper.exists():
            exe_path = ff16tools_folder_upper / 'FF16Tools.CLI.exe'
            if exe_path.exists():
                self.logger.info(f"FF16Tools 찾음: {exe_path}")
                return str(exe_path)

        # 3. 현재 디렉토리에서 직접 찾기
        exe_path = self.base_dir / 'FF16Tools.CLI.exe'
        if exe_path.exists():
            self.logger.info(f"FF16Tools 찾음: {exe_path}")
            return str(exe_path)

        # 4. 하위 폴더 재귀 검색
        for exe_path in self.base_dir.rglob('FF16Tools.CLI.exe'):
            self.logger.info(f"FF16Tools 찾음: {exe_path}")
            return str(exe_path)

        self.logger.warning("FF16Tools.CLI.exe를 찾을 수 없음")
        return None

    def find_ffttic_nxdtext(self):
        """
        ffttic-nxdtext.exe 찾기

        Returns:
            ffttic-nxdtext.exe 경로 (str) 또는 None
        """
        # 1. 현재 디렉토리에서 찾기
        exe_path = self.base_dir / 'ffttic-nxdtext.exe'
        if exe_path.exists():
            self.logger.info(f"ffttic-nxdtext 찾음: {exe_path}")
            return str(exe_path)

        # 2. 변형된 이름 확인 (하이픈 제거)
        exe_path_alt = self.base_dir / 'ffticcnxdtext.exe'
        if exe_path_alt.exists():
            self.logger.info(f"ffttic-nxdtext 찾음: {exe_path_alt}")
            return str(exe_path_alt)

        # 3. 하위 폴더 재귀 검색
        for exe_path in self.base_dir.rglob('ffttic-nxdtext.exe'):
            self.logger.info(f"ffttic-nxdtext 찾음: {exe_path}")
            return str(exe_path)

        # 4. 변형된 이름으로 재귀 검색
        for exe_path in self.base_dir.rglob('ffticcnxdtext.exe'):
            self.logger.info(f"ffttic-nxdtext 찾음: {exe_path}")
            return str(exe_path)

        self.logger.warning("ffttic-nxdtext.exe를 찾을 수 없음")
        return None

    def get_output_folder_from_pac(self, pac_file_path):
        """
        PAC 파일 경로로부터 출력 폴더 경로 생성

        Args:
            pac_file_path: PAC 파일 경로

        Returns:
            출력 폴더 경로 (str)
        """
        pac_path = Path(pac_file_path)

        # PAC 파일명에서 확장자 제거 (예: 0004.ja.pac -> 0004.ja)
        folder_name = pac_path.stem

        # 현재 프로그램이 있는 폴더에 출력
        output_folder = self.base_dir / folder_name

        self.logger.info(f"출력 폴더 생성: {output_folder}")
        return str(output_folder)


# sys 모듈 import
import sys


# 전역 인스턴스
_global_tool_finder = None


def get_tool_finder():
    """전역 도구 찾기 인스턴스 반환"""
    global _global_tool_finder
    if _global_tool_finder is None:
        _global_tool_finder = ToolFinder()
    return _global_tool_finder
