"""
탭 2: CSV 변환
"""
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QLineEdit, QTextEdit, QProgressBar,
                              QFileDialog, QGroupBox, QRadioButton, QButtonGroup,
                              QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal
from core.csv_handler import CSVHandler
from utils.i18n import t



class CSVConversionWorker(QThread):
    """CSV 변환 작업을 수행하는 워커 스레드"""

    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str, int)

    def __init__(self, input_folder, output_folder, recursive):
        super().__init__()
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.recursive = recursive

    def run(self):
        """작업 실행"""
        try:
            csv_handler = CSVHandler()

            self.log_signal.emit(t("tab_to_csv.log_start"))
            self.progress_signal.emit(10)

            # CSV 생성
            csv_count = csv_handler.generate_csvs(
                self.input_folder,
                self.output_folder,
                self.recursive
            )

            self.progress_signal.emit(100)
            self.finished_signal.emit(True, t("tab_to_csv.log_complete"), csv_count)

        except Exception as e:
            self.log_signal.emit(t("tab_to_csv.log_error", error=str(e)))
            self.finished_signal.emit(False, t("tab_to_csv.error_occurred", error=str(e)), 0)


class TabToCSV(QWidget):
    """YAML/JSON → CSV 변환 탭"""

    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout()

        # 변환할 파일 선택
        group_input = QGroupBox(t("tab_to_csv.group_input"))
        layout_input = QVBoxLayout()

        # 단일 폴더 선택
        layout_single = QHBoxLayout()
        self.input_folder_edit = QLineEdit()
        self.input_folder_edit.setReadOnly(True)
        self.input_folder_edit.setPlaceholderText(t("tab_to_csv.select_source"))
        btn_select_folder = QPushButton(t("common.select_folder"))
        btn_select_folder.clicked.connect(self.select_input_folder)
        layout_single.addWidget(QLabel(t("tab_to_csv.source_folder")))
        layout_single.addWidget(self.input_folder_edit)
        layout_single.addWidget(btn_select_folder)
        layout_input.addLayout(layout_single)

        # 재귀 탐색 옵션
        layout_recursive = QHBoxLayout()
        self.radio_single = QRadioButton(t("tab_to_csv.radio_single_folder"))
        self.radio_recursive = QRadioButton(t("tab_to_csv.recursive"))
        self.radio_single.setChecked(True)
        self.folder_group = QButtonGroup()
        self.folder_group.addButton(self.radio_single)
        self.folder_group.addButton(self.radio_recursive)
        layout_recursive.addWidget(self.radio_single)
        layout_recursive.addWidget(self.radio_recursive)
        layout_input.addLayout(layout_recursive)

        group_input.setLayout(layout_input)
        layout.addWidget(group_input)

        # CSV 저장 위치
        group_output = QGroupBox(t("tab_to_csv.group_output"))
        layout_output = QHBoxLayout()
        self.output_folder_edit = QLineEdit()
        self.output_folder_edit.setReadOnly(True)
        self.output_folder_edit.setPlaceholderText(t("tab_to_csv.select_output"))
        btn_select_output = QPushButton(t("common.select_folder"))
        btn_select_output.clicked.connect(self.select_output_folder)
        layout_output.addWidget(QLabel(t("tab_to_csv.output_folder")))
        layout_output.addWidget(self.output_folder_edit)
        layout_output.addWidget(btn_select_output)
        group_output.setLayout(layout_output)
        layout.addWidget(group_output)

        # 실행 버튼
        self.btn_start = QPushButton(t("tab_to_csv.start_convert"))
        self.btn_start.clicked.connect(self.start_conversion)
        layout.addWidget(self.btn_start)

        # 진행 상태
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # 로그 출력
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(QLabel(t("tab_to_csv.log")))
        layout.addWidget(self.log_text)

        self.setLayout(layout)

    def select_input_folder(self):
        """입력 폴더 선택"""
        folder_path = QFileDialog.getExistingDirectory(self, t("common.select_folder"))
        if folder_path:
            self.input_folder_edit.setText(folder_path)
            self.add_log(t("tab_to_csv.folder_selected", path=folder_path))

    def select_output_folder(self):
        """출력 폴더 선택"""
        folder_path = QFileDialog.getExistingDirectory(self, t("tab_to_csv.dialog_select_output"))
        if folder_path:
            self.output_folder_edit.setText(folder_path)
            self.add_log(t("tab_to_csv.output_folder_selected", path=folder_path))

    def start_conversion(self):
        """CSV 변환 시작"""
        # 입력 검증
        input_folder = self.input_folder_edit.text()
        output_folder = self.output_folder_edit.text()

        if not input_folder:
            QMessageBox.warning(self, t("common.warning"), t("tab_to_csv.error_no_source"))
            return

        if not output_folder:
            QMessageBox.warning(self, t("common.warning"), t("tab_to_csv.error_no_output"))
            return

        if not Path(input_folder).exists():
            QMessageBox.warning(self, t("common.warning"), t("tab_to_csv.error_folder_not_found", path=input_folder))
            return

        # UI 상태 변경
        self.btn_start.setEnabled(False)
        self.progress_bar.setValue(0)
        self.add_log(t("tab_to_csv.log_preparing"))

        # 재귀 옵션 확인
        recursive = self.radio_recursive.isChecked()

        # 워커 스레드 생성 및 시작
        self.worker = CSVConversionWorker(input_folder, output_folder, recursive)

        # 시그널 연결
        self.worker.log_signal.connect(self.add_log)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.finished_signal.connect(self.on_finished)

        # 스레드 시작
        self.worker.start()

    def on_finished(self, success, message, csv_count):
        """작업 완료 시 호출"""
        self.add_log(message)
        if csv_count > 0:
            self.add_log(t("tab_to_csv.log_files_generated", count=csv_count))
        self.btn_start.setEnabled(True)

        if success:
            QMessageBox.information(self, t("common.completed"), t("tab_to_csv.complete_message", message=message, count=csv_count))
        else:
            QMessageBox.critical(self, t("common.error"), message)

        self.worker = None

    def add_log(self, message):
        """로그 추가"""
        self.log_text.append(message)
