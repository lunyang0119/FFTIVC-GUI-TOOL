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

            self.log_signal.emit("CSV 변환 시작...")
            self.progress_signal.emit(10)

            # CSV 생성
            csv_count = csv_handler.generate_csvs(
                self.input_folder,
                self.output_folder,
                self.recursive
            )

            self.progress_signal.emit(100)
            self.finished_signal.emit(True, f"CSV 생성 완료!", csv_count)

        except Exception as e:
            self.log_signal.emit(f"오류 발생: {str(e)}")
            self.finished_signal.emit(False, f"오류: {str(e)}", 0)


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
        group_input = QGroupBox("변환할 파일 선택")
        layout_input = QVBoxLayout()

        # 단일 폴더 선택
        layout_single = QHBoxLayout()
        self.input_folder_edit = QLineEdit()
        self.input_folder_edit.setReadOnly(True)
        self.input_folder_edit.setPlaceholderText("YAML/JSON 파일이 있는 폴더")
        btn_select_folder = QPushButton("폴더 선택")
        btn_select_folder.clicked.connect(self.select_input_folder)
        layout_single.addWidget(QLabel("폴더:"))
        layout_single.addWidget(self.input_folder_edit)
        layout_single.addWidget(btn_select_folder)
        layout_input.addLayout(layout_single)

        # 재귀 탐색 옵션
        layout_recursive = QHBoxLayout()
        self.radio_single = QRadioButton("선택한 폴더만")
        self.radio_recursive = QRadioButton("하위 폴더 포함 (재귀)")
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
        group_output = QGroupBox("CSV 저장 위치")
        layout_output = QHBoxLayout()
        self.output_folder_edit = QLineEdit()
        self.output_folder_edit.setReadOnly(True)
        self.output_folder_edit.setPlaceholderText("CSV 파일이 저장될 폴더")
        btn_select_output = QPushButton("폴더 선택")
        btn_select_output.clicked.connect(self.select_output_folder)
        layout_output.addWidget(QLabel("출력 폴더:"))
        layout_output.addWidget(self.output_folder_edit)
        layout_output.addWidget(btn_select_output)
        group_output.setLayout(layout_output)
        layout.addWidget(group_output)

        # 실행 버튼
        self.btn_start = QPushButton("CSV 생성")
        self.btn_start.clicked.connect(self.start_conversion)
        layout.addWidget(self.btn_start)

        # 진행 상태
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # 로그 출력
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(QLabel("로그:"))
        layout.addWidget(self.log_text)

        self.setLayout(layout)

    def select_input_folder(self):
        """입력 폴더 선택"""
        folder_path = QFileDialog.getExistingDirectory(self, "폴더 선택")
        if folder_path:
            self.input_folder_edit.setText(folder_path)
            self.add_log(f"폴더 선택됨: {folder_path}")

    def select_output_folder(self):
        """출력 폴더 선택"""
        folder_path = QFileDialog.getExistingDirectory(self, "CSV 저장 폴더 선택")
        if folder_path:
            self.output_folder_edit.setText(folder_path)
            self.add_log(f"출력 폴더 선택됨: {folder_path}")

    def start_conversion(self):
        """CSV 변환 시작"""
        # 입력 검증
        input_folder = self.input_folder_edit.text()
        output_folder = self.output_folder_edit.text()

        if not input_folder:
            QMessageBox.warning(self, "입력 오류", "입력 폴더를 선택해주세요.")
            return

        if not output_folder:
            QMessageBox.warning(self, "입력 오류", "출력 폴더를 선택해주세요.")
            return

        if not Path(input_folder).exists():
            QMessageBox.warning(self, "폴더 오류", f"폴더를 찾을 수 없습니다:\n{input_folder}")
            return

        # UI 상태 변경
        self.btn_start.setEnabled(False)
        self.progress_bar.setValue(0)
        self.add_log("CSV 변환 준비 중...")

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
            self.add_log(f"총 {csv_count}개의 CSV 파일이 생성되었습니다.")
        self.btn_start.setEnabled(True)

        if success:
            QMessageBox.information(self, "완료", f"{message}\n총 {csv_count}개 파일 생성")
        else:
            QMessageBox.critical(self, "오류", message)

        self.worker = None

    def add_log(self, message):
        """로그 추가"""
        self.log_text.append(message)
