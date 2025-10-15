"""
FFT/FF16 번역 도구 메인 실행 파일
"""
import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import get_logger


def main():
    """메인 함수"""
    logger = get_logger()
    logger.info("=" * 50)
    logger.info("FFT/FF16 번역 도구 시작")
    logger.info("=" * 50)

    app = QApplication(sys.argv)
    app.setApplicationName("FFT/FF16 번역 도구")
    app.setOrganizationName("FFT Translation Tool")

    window = MainWindow()
    window.show()

    logger.info("메인 윈도우 표시됨")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
