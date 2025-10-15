"""
로깅 시스템 모듈
"""
import logging
import os
from datetime import datetime
from pathlib import Path


class AppLogger:
    """애플리케이션 로거 클래스"""

    def __init__(self, log_dir='logs'):
        """
        로거 초기화

        Args:
            log_dir: 로그 파일을 저장할 디렉토리 경로
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger('FFT_Tool')
        self.logger.setLevel(logging.DEBUG)

        # 기존 핸들러 제거 (중복 방지)
        if self.logger.handlers:
            self.logger.handlers.clear()

        # 파일 핸들러
        log_file = self.log_dir / f'app_{datetime.now().strftime("%Y%m%d")}.log'
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)

        # 포맷터
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)

        self.logger.addHandler(fh)

    def debug(self, msg):
        """디버그 로그"""
        self.logger.debug(msg)

    def info(self, msg):
        """정보 로그"""
        self.logger.info(msg)

    def warning(self, msg):
        """경고 로그"""
        self.logger.warning(msg)

    def error(self, msg):
        """에러 로그"""
        self.logger.error(msg)

    def critical(self, msg):
        """치명적 에러 로그"""
        self.logger.critical(msg)


# 전역 로거 인스턴스
_global_logger = None


def get_logger():
    """전역 로거 인스턴스 반환"""
    global _global_logger
    if _global_logger is None:
        _global_logger = AppLogger()
    return _global_logger
