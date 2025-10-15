"""
탭 4: 번역 적용
"""
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QLineEdit, QTextEdit, QProgressBar,
                              QCheckBox, QFileDialog, QGroupBox, QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal
from core.pac_handler import PACHandler


class ApplyWorker(QThread):
    """번역 적용 및 팩킹 작업을 수행하는 워커 스레드"""

    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, csv_folder, source_folder, output_pac, delete_yaml_json, delete_other):
        super().__init__()
        self.csv_folder = csv_folder
        self.source_folder = source_folder
        self.output_pac = output_pac
        self.delete_yaml_json = delete_yaml_json
        self.delete_other = delete_other

    def run(self):
        """작업 실행"""
        try:
            pac_handler = PACHandler()

            # 콜백 함수로 로그 전송
            def callback(msg):
                self.log_signal.emit(msg)

            # 번역 적용 및 팩킹 실행
            success = pac_handler.apply_translation_and_pack(
                self.csv_folder,
                self.source_folder,
                self.output_pac,
                self.delete_yaml_json,
                self.delete_other,
                game='fft',
                callback=callback
            )

            if success:
                self.progress_signal.emit(100)
                self.finished_signal.emit(True, "번역 적용 및 팩킹이 완료되었습니다!")
            else:
                self.finished_signal.emit(False, "작업 중 오류가 발생했습니다.")

        except Exception as e:
            self.log_signal.emit(f"오류 발생: {str(e)}")
            self.finished_signal.emit(False, f"오류: {str(e)}")


class TabApply(QWidget):
    """번역 적용 및 팩킹 탭"""

    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout()

        # CSV 폴더 선택
        group_csv = QGroupBox("번역된 CSV 파일")
        layout_csv = QHBoxLayout()
        self.csv_folder_edit = QLineEdit()
        self.csv_folder_edit.setReadOnly(True)
        self.csv_folder_edit.setPlaceholderText("번역이 완료된 CSV 파일이 있는 폴더")
        btn_select_csv = QPushButton("폴더 선택")
        btn_select_csv.clicked.connect(self.select_csv_folder)
        layout_csv.addWidget(QLabel("CSV 폴더:"))
        layout_csv.addWidget(self.csv_folder_edit)
        layout_csv.addWidget(btn_select_csv)
        group_csv.setLayout(layout_csv)
        layout.addWidget(group_csv)

        # YAML/JSON 폴더 선택
        group_source = QGroupBox("원본 YAML/JSON 파일")
        layout_source = QHBoxLayout()
        self.source_folder_edit = QLineEdit()
        self.source_folder_edit.setReadOnly(True)
        self.source_folder_edit.setPlaceholderText("언팩된 YAML/JSON 파일이 있는 폴더")
        btn_select_source = QPushButton("폴더 선택")
        btn_select_source.clicked.connect(self.select_source_folder)
        layout_source.addWidget(QLabel("원본 폴더:"))
        layout_source.addWidget(self.source_folder_edit)
        layout_source.addWidget(btn_select_source)
        group_source.setLayout(layout_source)
        layout.addWidget(group_source)

        # 출력 폴더 선택
        group_output = QGroupBox("최종 PAC 파일 저장 위치")
        layout_output = QHBoxLayout()
        self.output_folder_edit = QLineEdit()
        self.output_folder_edit.setReadOnly(True)
        self.output_folder_edit.setPlaceholderText("팩킹된 PAC 파일이 저장될 폴더")
        btn_select_output = QPushButton("폴더 선택")
        btn_select_output.clicked.connect(self.select_output_folder)
        layout_output.addWidget(QLabel("출력 폴더:"))
        layout_output.addWidget(self.output_folder_edit)
        layout_output.addWidget(btn_select_output)
        group_output.setLayout(layout_output)
        layout.addWidget(group_output)

        # 처리 옵션
        group_options = QGroupBox("처리 옵션")
        layout_options = QVBoxLayout()
        self.check_delete_yaml_json = QCheckBox("변환 후 YAML/JSON 삭제 (NXD/PZD만 남김)")
        self.check_delete_yaml_json.setChecked(True)  # 기본값 True로 변경
        self.check_delete_other = QCheckBox("기타 파일 자동 삭제 (NXD/PZD 이외)")
        self.check_delete_other.setChecked(False)
        layout_options.addWidget(self.check_delete_yaml_json)
        layout_options.addWidget(self.check_delete_other)

        # 안내 메시지
        info_label = QLabel(
            "참고: NXD/PZD 파일은 번역이 적용되어 덮어쓰기 됩니다.\n"
            "YAML/JSON 파일은 중간 파일이므로 팩킹 후 삭제를 권장합니다."
        )
        info_label.setStyleSheet("color: #666; font-size: 10px;")
        layout_options.addWidget(info_label)

        group_options.setLayout(layout_options)
        layout.addWidget(group_options)

        # 실행 버튼
        self.btn_start = QPushButton("번역 적용 및 팩킹")
        self.btn_start.clicked.connect(self.start_apply)
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

    def select_csv_folder(self):
        """CSV 폴더 선택"""
        folder_path = QFileDialog.getExistingDirectory(self, "CSV 폴더 선택")
        if folder_path:
            self.csv_folder_edit.setText(folder_path)
            self.add_log(f"CSV 폴더 선택됨: {folder_path}")

    def select_source_folder(self):
        """원본 폴더 선택"""
        folder_path = QFileDialog.getExistingDirectory(self, "원본 폴더 선택")
        if folder_path:
            self.source_folder_edit.setText(folder_path)
            self.add_log(f"원본 폴더 선택됨: {folder_path}")

    def select_output_folder(self):
        """출력 폴더 선택"""
        folder_path = QFileDialog.getExistingDirectory(self, "출력 폴더 선택")
        if folder_path:
            self.output_folder_edit.setText(folder_path)
            self.add_log(f"출력 폴더 선택됨: {folder_path}")

    def start_apply(self):
        """번역 적용 및 팩킹 시작"""
        # 입력 검증
        csv_folder = self.csv_folder_edit.text()
        source_folder = self.source_folder_edit.text()
        output_folder = self.output_folder_edit.text()

        if not csv_folder:
            QMessageBox.warning(self, "입력 오류", "CSV 폴더를 선택해주세요.")
            return

        if not source_folder:
            QMessageBox.warning(self, "입력 오류", "원본 YAML/JSON 폴더를 선택해주세요.")
            return

        if not output_folder:
            QMessageBox.warning(self, "입력 오류", "출력 폴더를 선택해주세요.")
            return

        if not Path(csv_folder).exists():
            QMessageBox.warning(self, "폴더 오류", f"폴더를 찾을 수 없습니다:\n{csv_folder}")
            return

        if not Path(source_folder).exists():
            QMessageBox.warning(self, "폴더 오류", f"폴더를 찾을 수 없습니다:\n{source_folder}")
            return

        # 출력 PAC 파일 경로 생성
        output_pac = Path(output_folder) / "translated.pac"

        # UI 상태 변경
        self.btn_start.setEnabled(False)
        self.progress_bar.setValue(0)
        self.add_log("번역 적용 및 팩킹 시작...")

        # 워커 스레드 생성 및 시작
        self.worker = ApplyWorker(
            csv_folder,
            source_folder,
            str(output_pac),
            self.check_delete_yaml_json.isChecked(),
            self.check_delete_other.isChecked()
        )

        # 시그널 연결
        self.worker.log_signal.connect(self.add_log)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.finished_signal.connect(self.on_finished)

        # 스레드 시작
        self.worker.start()

    def on_finished(self, success, message):
        """작업 완료 시 호출"""
        self.add_log(message)
        self.btn_start.setEnabled(True)

        if success:
            QMessageBox.information(self, "완료", message)
        else:
            QMessageBox.critical(self, "오류", message)

        self.worker = None

    def add_log(self, message):
        """로그 추가"""
        self.log_text.append(message)
