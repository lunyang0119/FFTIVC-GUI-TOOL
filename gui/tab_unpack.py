from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QLineEdit, QCheckBox, QTextEdit,
                              QProgressBar, QFileDialog, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from core.pac_handler import PACHandler
from utils.i18n import t



class UnpackWorker(QThread):
    """언팩 작업을 수행하는 워커 스레드"""

    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, pac_file, output_folder, convert_nxd, convert_pzd):
        super().__init__()
        self.pac_file = pac_file
        self.output_folder = output_folder
        self.convert_nxd = convert_nxd
        self.convert_pzd = convert_pzd

    def run(self):
        """작업 실행"""
        try:
            pac_handler = PACHandler()

            # 진행률 추적
            self.current_progress = 0

            # 콜백 함수로 로그 전송 및 진행률 업데이트
            def callback(msg):
                self.log_signal.emit(msg)

                # 메시지에 따라 진행률 업데이트
                if "언팩 중" in msg:
                    self.progress_signal.emit(20)
                elif "언팩 완료" in msg:
                    self.progress_signal.emit(40)
                elif "NXD" in msg and "변환 중" in msg:
                    self.progress_signal.emit(60)
                elif "NXD" in msg and "완료" in msg:
                    self.progress_signal.emit(75)
                elif "PZD" in msg and "변환 중" in msg:
                    self.progress_signal.emit(80)
                elif "PZD" in msg and "완료" in msg:
                    self.progress_signal.emit(95)
                elif "모든 작업 완료" in msg:
                    self.progress_signal.emit(100)

            self.progress_signal.emit(5)

            # 언팩 및 변환 실행
            success = pac_handler.unpack_and_convert(
                self.pac_file,
                self.output_folder,
                convert_nxd=self.convert_nxd,
                convert_pzd=self.convert_pzd,
                game='fft',
                callback=callback
            )

            if success:
                self.progress_signal.emit(100)
                self.finished_signal.emit(True, "작업이 성공적으로 완료되었습니다!")
            else:
                self.finished_signal.emit(False, "작업 중 오류가 발생했습니다.")

        except Exception as e:
            self.log_signal.emit(f"오류 발생: {str(e)}")
            self.finished_signal.emit(False, f"오류: {str(e)}")


class ConvertWorker(QThread):
    """파일 변환 작업을 수행하는 워커 스레드"""

    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str, int)

    def __init__(self, folder_path, convert_type):
        """
        Args:
            folder_path: 변환할 파일이 있는 폴더
            convert_type: 'pzd_to_yaml', 'nxd_to_json'
        """
        super().__init__()
        self.folder_path = folder_path
        self.convert_type = convert_type

    def run(self):
        """작업 실행"""
        try:
            from core.converter import Converter
            converter = Converter()

            self.progress_signal.emit(10)

            if self.convert_type == 'pzd_to_yaml':
                self.log_signal.emit("PZD → YAML 변환 시작...")
                count = converter.convert_pzd_to_yaml(self.folder_path, recursive=True)
                self.log_signal.emit(f"PZD → YAML 변환 완료: {count}개 파일")

            elif self.convert_type == 'nxd_to_json':
                self.log_signal.emit("NXD → JSON 변환 시작...")
                count = converter.convert_nxd_to_json(self.folder_path, recursive=True)
                self.log_signal.emit(f"NXD → JSON 변환 완료: {count}개 파일")

            self.progress_signal.emit(100)
            self.finished_signal.emit(True, "변환 완료!", count)

        except Exception as e:
            self.log_signal.emit(f"오류 발생: {str(e)}")
            self.finished_signal.emit(False, f"오류: {str(e)}", 0)


class TabUnpack(QWidget):
    """PAC 언팩 및 변환 탭"""

    def __init__(self):
        super().__init__()
        self.worker = None
        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout()

        # 원본 게임 파일 선택
        group_input = QGroupBox(t("tab_unpack.title"))
        layout_input = QVBoxLayout()

        # 파일 선택
        layout_file = QHBoxLayout()
        self.input_file_edit = QLineEdit()
        self.input_file_edit.setReadOnly(True)
        self.input_file_edit.setPlaceholderText(t("tab_unpack.select_pac"))
        btn_select_file = QPushButton(t("common.select_file"))
        btn_select_file.clicked.connect(self.select_input_file)
        layout_file.addWidget(QLabel(t("tab_unpack.pac_file")))
        layout_file.addWidget(self.input_file_edit)
        layout_file.addWidget(btn_select_file)
        layout_input.addLayout(layout_file)

        # 폴더 선택
        layout_folder = QHBoxLayout()
        self.input_folder_edit = QLineEdit()
        self.input_folder_edit.setReadOnly(True)
        self.input_folder_edit.setPlaceholderText("또는 PAC 파일이 있는 폴더를 선택하세요")
        btn_select_folder = QPushButton(t("common.select_folder"))
        btn_select_folder.clicked.connect(self.select_input_folder)
        layout_folder.addWidget(QLabel("폴더:"))
        layout_folder.addWidget(self.input_folder_edit)
        layout_folder.addWidget(btn_select_folder)
        layout_input.addLayout(layout_folder)

        group_input.setLayout(layout_input)
        layout.addWidget(group_input)

        # 출력 폴더 선택
        group_output = QGroupBox("변환 파일 저장 위치")
        layout_output = QHBoxLayout()
        self.output_folder_edit = QLineEdit()
        self.output_folder_edit.setReadOnly(True)
        self.output_folder_edit.setPlaceholderText(t("tab_unpack.select_output"))
        btn_select_output = QPushButton(t("common.select_folder"))
        btn_select_output.clicked.connect(self.select_output_folder)
        layout_output.addWidget(QLabel(t("tab_unpack.output_folder")))
        layout_output.addWidget(self.output_folder_edit)
        layout_output.addWidget(btn_select_output)
        group_output.setLayout(layout_output)
        layout.addWidget(group_output)

        # 추가 변환 옵션
        group_options = QGroupBox(t("tab_unpack.convert_options"))
        layout_options = QVBoxLayout()
        self.check_convert_nxd = QCheckBox(t("tab_unpack.convert_nxd"))
        self.check_convert_nxd.setChecked(True)
        self.check_convert_pzd = QCheckBox(t("tab_unpack.convert_pzd"))
        self.check_convert_pzd.setChecked(True)
        layout_options.addWidget(self.check_convert_nxd)
        layout_options.addWidget(self.check_convert_pzd)
        group_options.setLayout(layout_options)
        layout.addWidget(group_options)

        # 실행 버튼
        self.btn_start = QPushButton(t("tab_unpack.start_unpack"))
        self.btn_start.clicked.connect(self.start_unpack)
        layout.addWidget(self.btn_start)

        # 독립 변환 기능
        group_standalone = QGroupBox("독립 변환 기능 (언팩 없이 변환만 수행)\n(출력 폴더로 지정된 곳에서 변환합니다.)")
        layout_standalone = QHBoxLayout()

        self.btn_pzd_to_yaml = QPushButton(t("tab_unpack.convert_pzd"))
        self.btn_pzd_to_yaml.clicked.connect(self.convert_pzd_to_yaml)

        self.btn_nxd_to_json = QPushButton(t("tab_unpack.convert_nxd"))
        self.btn_nxd_to_json.clicked.connect(self.convert_nxd_to_json)

        layout_standalone.addWidget(self.btn_pzd_to_yaml)
        layout_standalone.addWidget(self.btn_nxd_to_json)
        group_standalone.setLayout(layout_standalone)
        layout.addWidget(group_standalone)

        # 진행 상태
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # 로그 출력
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(QLabel(t("tab_unpack.log")))
        layout.addWidget(self.log_text)

        self.setLayout(layout)

    def select_input_file(self):
        """입력 파일 선택"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, t("tab_unpack.select_pac"), "", "PAC Files (*.pac);;All Files (*)"
        )
        if file_path:
            self.input_file_edit.setText(file_path)
            self.input_folder_edit.clear()
            self.add_log(t("tab_unpack.pac_selected").format(path=file_path))

            # 출력 폴더 자동 설정
            self._auto_set_output_folder(file_path)

    def select_input_folder(self):
        """입력 폴더 선택"""
        folder_path = QFileDialog.getExistingDirectory(self, t("common.select_folder"))
        if folder_path:
            self.input_folder_edit.setText(folder_path)
            self.input_file_edit.clear()
            self.add_log(t("tab_unpack.folder_selected").format(path=folder_path))

    def select_output_folder(self):
        """출력 폴더 선택"""
        folder_path = QFileDialog.getExistingDirectory(self, t("tab_unpack.select_output"))
        if folder_path:
            self.output_folder_edit.setText(folder_path)
            self.add_log(t("tab_unpack.folder_selected").format(path=folder_path))

    def start_unpack(self):
        """언팩 및 변환 시작"""
        # 입력 검증
        pac_file = self.input_file_edit.text()
        output_folder = self.output_folder_edit.text()

        if not pac_file:
            QMessageBox.warning(self, t("common.warning"), t("tab_unpack.error_no_pac"))
            return

        if not output_folder:
            QMessageBox.warning(self, t("common.warning"), t("tab_unpack.error_no_output"))
            return

        if not Path(pac_file).exists():
            QMessageBox.warning(self, t("common.warning"), t("tab_unpack.error_pac_not_found").format(path=pac_file))
            return

        # UI 상태 변경
        self.btn_start.setEnabled(False)
        self.progress_bar.setValue(0)
        self.add_log(t("tab_unpack.start_unpack"))

        # 워커 스레드 생성 및 시작
        self.worker = UnpackWorker(
            pac_file,
            output_folder,
            self.check_convert_nxd.isChecked(),
            self.check_convert_pzd.isChecked()
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
            QMessageBox.information(self, t("common.completed"), message)
        else:
            QMessageBox.critical(self, t("common.error"), message)

        self.worker = None

    def _auto_set_output_folder(self, pac_file_path):
        """
        PAC 파일 경로로부터 출력 폴더 자동 설정

        Args:
            pac_file_path: PAC 파일 경로
        """
        from utils.tool_finder import get_tool_finder

        tool_finder = get_tool_finder()
        output_folder = tool_finder.get_output_folder_from_pac(pac_file_path)

        self.output_folder_edit.setText(output_folder)
        self.add_log(t("tab_unpack.folder_selected").format(path=output_folder))

    def convert_pzd_to_yaml(self):
        """PZD → YAML 독립 변환"""
        folder_path = self.input_folder_edit.text()

        if not folder_path:
            QMessageBox.warning(self, t("common.warning"), "변환할 파일이 있는 폴더를 선택해주세요.")
            return

        if not Path(folder_path).exists():
            QMessageBox.warning(self, t("common.warning"), "폴더를 찾을 수 없습니다:\n{0}".format(folder_path))
            return

        # UI 상태 변경
        self.btn_pzd_to_yaml.setEnabled(False)
        self.progress_bar.setValue(0)
        self.add_log("PZD → YAML 변환 준비 중...")

        # 워커 스레드 생성 및 시작
        self.worker = ConvertWorker(folder_path, 'pzd_to_yaml')

        # 시그널 연결
        self.worker.log_signal.connect(self.add_log)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.finished_signal.connect(self.on_convert_finished)

        # 스레드 시작
        self.worker.start()

    def convert_nxd_to_json(self):
        """NXD → JSON 독립 변환"""
        folder_path = self.input_folder_edit.text()

        if not folder_path:
            QMessageBox.warning(self, t("common.warning"), "변환할 파일이 있는 폴더를 선택해주세요.")
            return

        if not Path(folder_path).exists():
            QMessageBox.warning(self, t("common.warning"), "폴더를 찾을 수 없습니다:\n{0}".format(folder_path))
            return

        # UI 상태 변경
        self.btn_nxd_to_json.setEnabled(False)
        self.progress_bar.setValue(0)
        self.add_log("NXD → JSON 변환 준비 중...")

        # 워커 스레드 생성 및 시작
        self.worker = ConvertWorker(folder_path, 'nxd_to_json')

        # 시그널 연결
        self.worker.log_signal.connect(self.add_log)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.finished_signal.connect(self.on_convert_finished)

        # 스레드 시작
        self.worker.start()

    def on_convert_finished(self, success, message, count):
        """변환 완료 시 호출"""
        self.add_log(message)
        if count > 0:
            self.add_log("총 {0}개의 파일이 변환되었습니다.".format(count))

        self.btn_pzd_to_yaml.setEnabled(True)
        self.btn_nxd_to_json.setEnabled(True)

        if success:
            QMessageBox.information(self, t("common.completed"), "{0}\n총 {1}개 파일 변환".format(message, count))
        else:
            QMessageBox.critical(self, t("common.error"), message)

        self.worker = None

    def add_log(self, message):
        """로그 추가"""
        self.log_text.append(message)
