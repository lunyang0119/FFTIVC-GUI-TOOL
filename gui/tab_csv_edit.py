"""
탭 3: CSV 수정
"""
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QLineEdit, QTextEdit, QCheckBox,
                              QFileDialog, QGroupBox, QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal
from core.validator import CSVValidator
from core.csv_handler import CSVHandler


class ValidationWorker(QThread):
    """검증 작업을 수행하는 워커 스레드"""

    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, list)

    def __init__(self, csv_folder):
        super().__init__()
        self.csv_folder = csv_folder

    def run(self):
        """작업 실행"""
        try:
            validator = CSVValidator()
            self.log_signal.emit("일본어 문자 검사 시작...")

            results = validator.validate_csv(self.csv_folder)

            self.log_signal.emit("검사 완료")
            self.finished_signal.emit(True, results)

        except Exception as e:
            self.log_signal.emit(f"오류 발생: {str(e)}")
            self.finished_signal.emit(False, [])


class ReplaceWorker(QThread):
    """치환 작업을 수행하는 워커 스레드"""

    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, int)

    def __init__(self, csv_folder, find_text, replace_text, translated_only):
        super().__init__()
        self.csv_folder = csv_folder
        self.find_text = find_text
        self.replace_text = replace_text
        self.translated_only = translated_only

    def run(self):
        """작업 실행"""
        try:
            csv_handler = CSVHandler()
            self.log_signal.emit("일괄 치환 시작...")

            count = csv_handler.batch_replace(
                self.csv_folder,
                self.find_text,
                self.replace_text,
                self.translated_only
            )

            self.log_signal.emit(f"완료: {count}개 파일 처리됨")
            self.finished_signal.emit(True, count)

        except Exception as e:
            self.log_signal.emit(f"오류 발생: {str(e)}")
            self.finished_signal.emit(False, 0)


class TabCSVEdit(QWidget):
    """CSV 검증 및 수정 탭"""

    def __init__(self):
        super().__init__()
        self.validation_worker = None
        self.replace_worker = None
        self.validation_results = []
        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout()

        # CSV 파일 검증
        group_validate = QGroupBox("CSV 파일 검증")
        layout_validate = QVBoxLayout()

        # CSV 폴더 선택
        layout_folder = QHBoxLayout()
        self.csv_folder_edit = QLineEdit()
        self.csv_folder_edit.setReadOnly(True)
        self.csv_folder_edit.setPlaceholderText("검증할 CSV 파일이 있는 폴더")
        btn_select_folder = QPushButton("폴더 선택")
        btn_select_folder.clicked.connect(self.select_csv_folder)
        layout_folder.addWidget(QLabel("CSV 폴더:"))
        layout_folder.addWidget(self.csv_folder_edit)
        layout_folder.addWidget(btn_select_folder)
        layout_validate.addLayout(layout_folder)

        # 검증 버튼
        self.btn_validate = QPushButton("일본어 문자 검사")
        self.btn_validate.clicked.connect(self.validate_csv)
        layout_validate.addWidget(self.btn_validate)

        # 검사 결과 (요약)
        self.validate_summary = QTextEdit()
        self.validate_summary.setReadOnly(True)
        self.validate_summary.setMaximumHeight(100)
        layout_validate.addWidget(QLabel("검사 요약:"))
        layout_validate.addWidget(self.validate_summary)

        # 검사 결과 (상세)
        self.validate_detail = QTextEdit()
        self.validate_detail.setReadOnly(True)
        self.validate_detail.setMaximumHeight(300)
        layout_validate.addWidget(QLabel("상세 결과 (파일명과 행 번호):"))
        layout_validate.addWidget(self.validate_detail)

        # 결과 저장 버튼
        self.btn_save_result = QPushButton("결과를 TXT 파일로 저장")
        self.btn_save_result.clicked.connect(self.save_validation_result)
        layout_validate.addWidget(self.btn_save_result)

        group_validate.setLayout(layout_validate)
        layout.addWidget(group_validate)

        # 일괄 문자 치환
        group_replace = QGroupBox("일괄 문자 치환")
        layout_replace = QVBoxLayout()

        # 치환 대상 폴더
        layout_replace_folder = QHBoxLayout()
        self.replace_folder_edit = QLineEdit()
        self.replace_folder_edit.setReadOnly(True)
        self.replace_folder_edit.setPlaceholderText("치환할 CSV 파일이 있는 폴더")
        btn_select_replace_folder = QPushButton("폴더 선택")
        btn_select_replace_folder.clicked.connect(self.select_replace_folder)
        layout_replace_folder.addWidget(QLabel("CSV 폴더:"))
        layout_replace_folder.addWidget(self.replace_folder_edit)
        layout_replace_folder.addWidget(btn_select_replace_folder)
        layout_replace.addLayout(layout_replace_folder)

        # 찾을 문자
        layout_find = QHBoxLayout()
        self.find_text_edit = QLineEdit()
        self.find_text_edit.setPlaceholderText("찾을 문자")
        layout_find.addWidget(QLabel("찾을 문자:"))
        layout_find.addWidget(self.find_text_edit)
        layout_replace.addLayout(layout_find)

        # 바꿀 문자
        layout_replace_text = QHBoxLayout()
        self.replace_text_edit = QLineEdit()
        self.replace_text_edit.setPlaceholderText("바꿀 문자")
        layout_replace_text.addWidget(QLabel("바꿀 문자:"))
        layout_replace_text.addWidget(self.replace_text_edit)
        layout_replace.addLayout(layout_replace_text)

        # 옵션
        self.check_translated_only = QCheckBox("Translation 열만 변경")
        self.check_translated_only.setChecked(True)
        layout_replace.addWidget(self.check_translated_only)

        # 치환 버튼
        self.btn_replace = QPushButton("일괄 치환")
        self.btn_replace.clicked.connect(self.batch_replace)
        layout_replace.addWidget(self.btn_replace)

        # 치환 로그
        self.replace_log = QTextEdit()
        self.replace_log.setReadOnly(True)
        self.replace_log.setMaximumHeight(100)
        layout_replace.addWidget(QLabel("로그:"))
        layout_replace.addWidget(self.replace_log)

        group_replace.setLayout(layout_replace)
        layout.addWidget(group_replace)

        self.setLayout(layout)

    def select_csv_folder(self):
        """검증용 CSV 폴더 선택"""
        folder_path = QFileDialog.getExistingDirectory(self, "CSV 폴더 선택")
        if folder_path:
            self.csv_folder_edit.setText(folder_path)
            self.add_validate_log(f"폴더 선택됨: {folder_path}")

    def select_replace_folder(self):
        """치환용 CSV 폴더 선택"""
        folder_path = QFileDialog.getExistingDirectory(self, "CSV 폴더 선택")
        if folder_path:
            self.replace_folder_edit.setText(folder_path)
            self.add_replace_log(f"폴더 선택됨: {folder_path}")

    def validate_csv(self):
        """CSV 파일 검증"""
        csv_folder = self.csv_folder_edit.text()

        if not csv_folder:
            QMessageBox.warning(self, "입력 오류", "CSV 폴더를 선택해주세요.")
            return

        if not Path(csv_folder).exists():
            QMessageBox.warning(self, "폴더 오류", f"폴더를 찾을 수 없습니다:\n{csv_folder}")
            return

        # UI 상태 변경
        self.btn_validate.setEnabled(False)
        self.validate_summary.clear()
        self.validate_detail.clear()

        # 워커 스레드 생성 및 시작
        self.validation_worker = ValidationWorker(csv_folder)

        # 시그널 연결
        self.validation_worker.log_signal.connect(self.add_validate_log)
        self.validation_worker.finished_signal.connect(self.on_validation_finished)

        # 스레드 시작
        self.validation_worker.start()

    def on_validation_finished(self, success, results):
        """검증 완료 시 호출"""
        self.btn_validate.setEnabled(True)
        self.validation_results = results

        if success:
            from core.validator import CSVValidator
            validator = CSVValidator()

            # 요약 표시
            summary = validator.get_validation_summary(results)
            self.validate_summary.setPlainText(summary)

            # 상세 결과 표시
            if len(results) > 0:
                detail = validator.get_detailed_validation_text(results)
                self.validate_detail.setPlainText(detail)
                QMessageBox.warning(self, "검증 완료", f"{len(results)}개의 문제가 발견되었습니다.\n상세 결과를 확인하세요.")
            else:
                self.validate_detail.setPlainText("문제가 발견되지 않았습니다.")
                QMessageBox.information(self, "검증 완료", "문제가 발견되지 않았습니다!")
        else:
            QMessageBox.critical(self, "오류", "검증 중 오류가 발생했습니다.")

        self.validation_worker = None

    def save_validation_result(self):
        """검증 결과 저장"""
        if not self.validation_results:
            QMessageBox.warning(self, "저장 오류", "저장할 검증 결과가 없습니다.\n먼저 검증을 실행해주세요.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "검증 결과 저장", "", "Text Files (*.txt)"
        )
        if file_path:
            try:
                validator = CSVValidator()
                validator.save_validation_result(self.validation_results, file_path)
                QMessageBox.information(self, "저장 완료", f"결과가 저장되었습니다:\n{file_path}")
                self.add_validate_log(f"결과 저장됨: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "저장 오류", f"저장 중 오류 발생:\n{str(e)}")

    def batch_replace(self):
        """일괄 문자 치환"""
        csv_folder = self.replace_folder_edit.text()
        find_text = self.find_text_edit.text()
        replace_text = self.replace_text_edit.text()

        if not csv_folder:
            QMessageBox.warning(self, "입력 오류", "CSV 폴더를 선택해주세요.")
            return

        if not find_text:
            QMessageBox.warning(self, "입력 오류", "찾을 문자를 입력해주세요.")
            return

        if not Path(csv_folder).exists():
            QMessageBox.warning(self, "폴더 오류", f"폴더를 찾을 수 없습니다:\n{csv_folder}")
            return

        # 확인 메시지
        reply = QMessageBox.question(
            self,
            "확인",
            f"'{find_text}'를 '{replace_text}'로 치환하시겠습니까?\n이 작업은 되돌릴 수 없습니다.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        # UI 상태 변경
        self.btn_replace.setEnabled(False)
        self.replace_log.clear()

        # 워커 스레드 생성 및 시작
        self.replace_worker = ReplaceWorker(
            csv_folder,
            find_text,
            replace_text,
            self.check_translated_only.isChecked()
        )

        # 시그널 연결
        self.replace_worker.log_signal.connect(self.add_replace_log)
        self.replace_worker.finished_signal.connect(self.on_replace_finished)

        # 스레드 시작
        self.replace_worker.start()

    def on_replace_finished(self, success, count):
        """치환 완료 시 호출"""
        self.btn_replace.setEnabled(True)

        if success:
            QMessageBox.information(self, "완료", f"{count}개 파일에서 치환이 완료되었습니다.")
        else:
            QMessageBox.critical(self, "오류", "치환 중 오류가 발생했습니다.")

        self.replace_worker = None

    def add_validate_log(self, message):
        """검증 로그 추가"""
        self.validate_summary.append(message)

    def add_replace_log(self, message):
        """치환 로그 추가"""
        self.replace_log.append(message)
