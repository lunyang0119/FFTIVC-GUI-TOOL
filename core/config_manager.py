"""
설정 관리 모듈
"""
import json
import os
from pathlib import Path
from utils.logger import get_logger


class ConfigManager:
    """설정 파일 관리 클래스"""

    def __init__(self, config_file='config.json'):
        """
        설정 관리자 초기화

        Args:
            config_file: 설정 파일 경로
        """
        self.config_file = Path(config_file)
        self.logger = get_logger()
        self.config = self._load_config()
        self._auto_detect_tools()

    def _load_config(self):
        """설정 파일 로드"""
        if not self.config_file.exists():
            self.logger.warning(f"설정 파일이 존재하지 않습니다: {self.config_file}")
            return self._get_default_config()

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self.logger.info("설정 파일 로드 완료")
            return config
        except Exception as e:
            self.logger.error(f"설정 파일 로드 실패: {e}")
            return self._get_default_config()

    def _get_default_config(self):
        """기본 설정 반환"""
        return {
            "ff16tools_path": "",
            "ffttic_nxdtext_path": "",
            "default_game_folder": "",
            "default_unpack_folder": "",
            "default_csv_folder": "",
            "last_used_paths": {
                "pac_input": "",
                "pac_output": "",
                "csv_input": "",
                "csv_output": ""
            }
        }

    def save_config(self):
        """설정 파일 저장"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info("설정 파일 저장 완료")
            return True
        except Exception as e:
            self.logger.error(f"설정 파일 저장 실패: {e}")
            return False

    def get(self, key, default=None):
        """설정 값 가져오기"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key, value):
        """설정 값 설정"""
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value
        self.save_config()

    def get_ff16tools_path(self):
        """FF16Tools 실행 파일 경로 반환"""
        return self.get('ff16tools_path', '')

    def set_ff16tools_path(self, path):
        """FF16Tools 실행 파일 경로 설정"""
        self.set('ff16tools_path', path)

    def get_ffttic_nxdtext_path(self):
        """ffttic-nxdtext 실행 파일 경로 반환"""
        return self.get('ffttic_nxdtext_path', '')

    def set_ffttic_nxdtext_path(self, path):
        """ffttic-nxdtext 실행 파일 경로 설정"""
        self.set('ffttic_nxdtext_path', path)

    def get_last_used_path(self, path_type):
        """마지막으로 사용한 경로 반환"""
        return self.get(f'last_used_paths.{path_type}', '')

    def set_last_used_path(self, path_type, path):
        """마지막으로 사용한 경로 설정"""
        self.set(f'last_used_paths.{path_type}', path)

    def _auto_detect_tools(self):
        """외부 도구 자동 탐지"""
        from utils.tool_finder import get_tool_finder

        tool_finder = get_tool_finder()

        # FF16Tools 자동 탐지
        ff16tools_path = self.get_ff16tools_path()
        if not ff16tools_path or not Path(ff16tools_path).exists():
            self.logger.info("FF16Tools 자동 탐지 시도...")
            detected_path = tool_finder.find_ff16tools()
            if detected_path:
                self.set_ff16tools_path(detected_path)
                self.logger.info(f"FF16Tools 자동 탐지 성공: {detected_path}")
            else:
                self.logger.warning("FF16Tools를 자동으로 찾을 수 없음")

        # ffttic-nxdtext 자동 탐지
        ffttic_path = self.get_ffttic_nxdtext_path()
        if not ffttic_path or not Path(ffttic_path).exists():
            self.logger.info("ffttic-nxdtext 자동 탐지 시도...")
            detected_path = tool_finder.find_ffttic_nxdtext()
            if detected_path:
                self.set_ffttic_nxdtext_path(detected_path)
                self.logger.info(f"ffttic-nxdtext 자동 탐지 성공: {detected_path}")
            else:
                self.logger.warning("ffttic-nxdtext를 자동으로 찾을 수 없음")


# 전역 설정 관리자 인스턴스
_global_config_manager = None


def get_config_manager():
    """전역 설정 관리자 인스턴스 반환"""
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = ConfigManager()
    return _global_config_manager
