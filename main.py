"""
FFT/FF16 번역 도구 메인 실행 파일
"""
import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import get_logger
from utils.i18n import set_language, t
from core.config_manager import get_config_manager


def main():
    """메인 함수"""
    logger = get_logger()
    logger.info("=" * 50)
    logger.info("FFT/FF16 Translation Tool Starting")
    logger.info("=" * 50)

    # 저장된 언어 설정 로드
    config = get_config_manager()
    lang_code = config.get_language()
    set_language(lang_code)
    logger.info(f"Language: {lang_code}")

    app = QApplication(sys.argv)
    app.setApplicationName(t("app.name"))
    app.setOrganizationName(t("app.organization"))

    window = MainWindow()
    window.show()

    logger.info("Main window displayed")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
