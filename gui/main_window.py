"""
메인 윈도우
"""
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                              QMenuBar, QStatusBar, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from gui.tab_unpack import TabUnpack
from gui.tab_to_csv import TabToCSV
from gui.tab_csv_edit import TabCSVEdit
from gui.tab_apply import TabApply
from core.config_manager import get_config_manager
from utils.logger import get_logger


class MainWindow(QMainWindow):
    """메인 윈도우 클래스"""

    def __init__(self):
        super().__init__()
        self.config_manager = get_config_manager()
        self.logger = get_logger()
        self.init_ui()
        self.check_external_tools()

    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("FFT/FF16 번역 도구 v1.0")
        self.setGeometry(100, 100, 1000, 700)

        # 메뉴바
        self.create_menu_bar()

        # 탭 위젯
        tabs = QTabWidget()
        tabs.addTab(TabUnpack(), "1. PAC 변환")
        tabs.addTab(TabToCSV(), "2. CSV 변환")
        tabs.addTab(TabCSVEdit(), "3. CSV 수정")
        tabs.addTab(TabApply(), "4. 번역 적용")

        self.setCentralWidget(tabs)

        # 상태바
        self.statusBar().showMessage("준비")
        self.logger.info("메인 윈도우 초기화 완료")

    def create_menu_bar(self):
        """메뉴바 생성"""
        menubar = self.menuBar()

        # 파일 메뉴
        file_menu = menubar.addMenu("파일")
        exit_action = file_menu.addAction("종료")
        exit_action.triggered.connect(self.close)

        # 설정 메뉴
        settings_menu = menubar.addMenu("설정")
        set_ff16tools_action = settings_menu.addAction("FF16Tools 경로 설정")
        set_ff16tools_action.triggered.connect(self.set_ff16tools_path)
        set_ffttic_action = settings_menu.addAction("ffttic-nxdtext 경로 설정")
        set_ffttic_action.triggered.connect(self.set_ffttic_path)

        # 도움말 메뉴
        help_menu = menubar.addMenu("도움말")
        about_action = help_menu.addAction("정보")
        about_action.triggered.connect(self.show_about)

    def check_external_tools(self):
        """외부 도구 경로 확인"""
        ff16tools_path = self.config_manager.get_ff16tools_path()
        ffttic_path = self.config_manager.get_ffttic_nxdtext_path()

        if not ff16tools_path or not ffttic_path:
            QMessageBox.warning(
                self,
                "외부 도구 설정 필요",
                "FF16Tools와 ffttic-nxdtext 경로를 설정해주세요.\n"
                "설정 메뉴에서 경로를 지정할 수 있습니다."
            )
            self.logger.warning("외부 도구 경로가 설정되지 않음")

    def set_ff16tools_path(self):
        """FF16Tools 경로 설정"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "FF16Tools.CLI.exe 선택",
            "",
            "Executable Files (*.exe);;All Files (*)"
        )
        if file_path:
            self.config_manager.set_ff16tools_path(file_path)
            QMessageBox.information(self, "설정 완료", f"FF16Tools 경로가 설정되었습니다:\n{file_path}")
            self.logger.info(f"FF16Tools 경로 설정: {file_path}")

    def set_ffttic_path(self):
        """ffttic-nxdtext 경로 설정"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "ffttic-nxdtext.exe 선택",
            "",
            "Executable Files (*.exe);;All Files (*)"
        )
        if file_path:
            self.config_manager.set_ffttic_nxdtext_path(file_path)
            QMessageBox.information(self, "설정 완료", f"ffttic-nxdtext 경로가 설정되었습니다:\n{file_path}")
            self.logger.info(f"ffttic-nxdtext 경로 설정: {file_path}")

    def show_about(self):
        """정보 표시"""
        about_text = """
        FFT/FF16 번역 도구 v1.0

        파이썬을 모르는 일반 사용자도 FFT/FF16 게임 파일의
        번역 작업을 쉽게 수행할 수 있도록 하는 GUI 기반 올인원 도구

        주요 기능:
        - PAC 파일 언팩/팩
        - NXD/PZD 파일을 JSON/YAML로 변환
        - JSON/YAML을 CSV로 변환하여 번역 작업 수행
        - CSV 검증 (일본어 문자 탐지)
        - 번역 적용 및 재팩킹

        외부 도구:
        - FF16Tools (https://github.com/Nenkai/FF16Tools)
        - ffttic-nxdtext
        """
        QMessageBox.about(self, "정보", about_text)

    def closeEvent(self, event):
        """종료 이벤트"""
        self.logger.info("프로그램 종료")
        event.accept()
