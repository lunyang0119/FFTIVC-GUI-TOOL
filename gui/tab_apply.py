"""
탭 4: 번역 적용
"""
from pathlib import Path
import shutil
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QLineEdit, QTextEdit, QProgressBar,
                              QCheckBox, QFileDialog, QGroupBox, QMessageBox,
                              QRadioButton, QButtonGroup)
from PyQt6.QtCore import QThread, pyqtSignal
from core.pac_handler import PACHandler
from utils.i18n import t


class ApplyWorker(QThread):
    """번역 적용 및 팩킹 작업을 수행하는 워커 스레드"""

    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, csv_folder, source_folder, output_pac, workflow_mode,
                 delete_other, apply_yaml=True, apply_json=True):
        super().__init__()
        self.csv_folder = csv_folder
        self.source_folder = source_folder
        self.output_pac = output_pac
        self.workflow_mode = workflow_mode
        self.delete_other = delete_other
        self.apply_yaml = apply_yaml
        self.apply_json = apply_json

    def run(self):
        """작업 실행"""
        try:
            pac_handler = PACHandler()

            # 콜백 함수로 로그 전송
            def callback(msg):
                self.log_signal.emit(msg)

            # 워크플로우 모드에 따른 처리
            working_folder = self.source_folder
            delete_yaml_json_after = False
            skip_packing = False

            # 모드 1: 복사본 생성 → YAML/JSON 삭제 → 팩킹
            if self.workflow_mode == 1:
                callback("=" * 60)
                callback(t("tab_apply.workflow_log_1"))
                callback("=" * 60)

                # 복사본 폴더 생성
                source_path = Path(self.source_folder)
                copy_folder = source_path.parent / f"{source_path.name}_copy"

                callback(t("tab_apply.copy_creating", path=str(copy_folder)))
                if copy_folder.exists():
                    callback(t("tab_apply.copy_deleting_old"))
                    shutil.rmtree(copy_folder)
                shutil.copytree(self.source_folder, copy_folder)
                working_folder = str(copy_folder)
                callback(t("tab_apply.copy_complete"))

                delete_yaml_json_after = True  # 변환 후 YAML/JSON 삭제
                skip_packing = False  # 팩킹 수행

            # 모드 2: YAML/JSON 삭제 → 팩킹
            elif self.workflow_mode == 2:
                callback("=" * 60)
                callback(t("tab_apply.workflow_log_2"))
                callback("=" * 60)

                delete_yaml_json_after = True  # 변환 후 YAML/JSON 삭제
                skip_packing = False  # 팩킹 수행

            # 모드 3: 팩킹하지 않음 (YAML/JSON 유지)
            elif self.workflow_mode == 3:
                callback("=" * 60)
                callback(t("tab_apply.workflow_log_3"))
                callback("=" * 60)

                delete_yaml_json_after = False  # YAML/JSON 유지
                skip_packing = True  # 팩킹 안함

            # 모드 4: 팩킹하지 않음 (YAML/JSON 삭제)
            elif self.workflow_mode == 4:
                callback("=" * 60)
                callback(t("tab_apply.workflow_log_4"))
                callback("=" * 60)

                delete_yaml_json_after = True  # YAML/JSON 삭제
                skip_packing = True  # 팩킹 안함

            # 번역 적용 및 팩킹 실행
            success = pac_handler.apply_translation_and_pack(
                self.csv_folder,
                working_folder,
                self.output_pac,
                delete_yaml_json=delete_yaml_json_after,
                delete_other=self.delete_other,
                apply_yaml=self.apply_yaml,
                apply_json=self.apply_json,
                skip_packing=skip_packing,
                game='fft',
                callback=callback
            )

            if success:
                self.progress_signal.emit(100)

                # 성공 메시지
                if self.workflow_mode == 1:
                    self.finished_signal.emit(True, t("tab_apply.complete_with_pack_mode1", folder=working_folder, pac=self.output_pac))
                elif self.workflow_mode == 2:
                    self.finished_signal.emit(True, t("tab_apply.complete_with_pack_mode2", pac=self.output_pac))
                elif self.workflow_mode == 3:
                    self.finished_signal.emit(True, t("tab_apply.complete_no_pack_mode3", folder=working_folder))
                elif self.workflow_mode == 4:
                    self.finished_signal.emit(True, t("tab_apply.complete_no_pack_mode4", folder=working_folder))
            else:
                self.finished_signal.emit(False, t("tab_apply.error_occurred"))

        except Exception as e:
            self.log_signal.emit(t("tab_apply.error_with_detail", error=str(e)))
            import traceback
            self.log_signal.emit(traceback.format_exc())
            self.finished_signal.emit(False, t("tab_apply.error_with_detail", error=str(e)))

    def _delete_yaml_json(self, folder, callback):
        """YAML/JSON 파일 삭제"""
        folder_path = Path(folder)

        # YAML 삭제
        yaml_files = list(folder_path.rglob('*.yaml'))
        for yaml_file in yaml_files:
            yaml_file.unlink()
        if yaml_files:
            callback(t("tab_apply.yaml_deleted", count=len(yaml_files)))

        # JSON 삭제
        json_files = list(folder_path.rglob('*.json'))
        for json_file in json_files:
            json_file.unlink()
        if json_files:
            callback(t("tab_apply.json_deleted", count=len(json_files)))


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
        group_csv = QGroupBox(t("tab_apply.csv_folder"))
        layout_csv = QHBoxLayout()
        self.csv_folder_edit = QLineEdit()
        self.csv_folder_edit.setReadOnly(True)
        self.csv_folder_edit.setPlaceholderText(t("tab_apply.select_csv"))
        btn_select_csv = QPushButton(t("tab_apply.select_folder"))
        btn_select_csv.clicked.connect(self.select_csv_folder)
        layout_csv.addWidget(QLabel(t("tab_apply.csv_folder_label")))
        layout_csv.addWidget(self.csv_folder_edit)
        layout_csv.addWidget(btn_select_csv)
        group_csv.setLayout(layout_csv)
        layout.addWidget(group_csv)

        # YAML/JSON 폴더 선택
        group_source = QGroupBox(t("tab_apply.source_folder"))
        layout_source = QHBoxLayout()
        self.source_folder_edit = QLineEdit()
        self.source_folder_edit.setReadOnly(True)
        self.source_folder_edit.setPlaceholderText(t("tab_apply.select_source"))
        btn_select_source = QPushButton(t("tab_apply.select_folder"))
        btn_select_source.clicked.connect(self.select_source_folder)
        layout_source.addWidget(QLabel(t("tab_apply.source_folder_label")))
        layout_source.addWidget(self.source_folder_edit)
        layout_source.addWidget(btn_select_source)
        group_source.setLayout(layout_source)
        layout.addWidget(group_source)

        # 출력 폴더 선택
        group_output = QGroupBox(t("tab_apply.output_folder"))
        layout_output = QHBoxLayout()
        self.output_folder_edit = QLineEdit()
        self.output_folder_edit.setReadOnly(True)
        self.output_folder_edit.setPlaceholderText(t("tab_apply.select_output"))
        btn_select_output = QPushButton(t("tab_apply.select_folder"))
        btn_select_output.clicked.connect(self.select_output_folder)
        layout_output.addWidget(QLabel(t("tab_apply.output_folder_label")))
        layout_output.addWidget(self.output_folder_edit)
        layout_output.addWidget(btn_select_output)
        group_output.setLayout(layout_output)
        layout.addWidget(group_output)

        # === 옵션 1: CSV 번역 적용 대상 ===
        group_apply = QGroupBox(t("tab_apply.apply_target_section"))
        layout_apply = QHBoxLayout()
        self.check_apply_yaml = QCheckBox(t("tab_apply.apply_yaml"))
        self.check_apply_yaml.setChecked(True)
        self.check_apply_json = QCheckBox(t("tab_apply.apply_json"))
        self.check_apply_json.setChecked(True)
        layout_apply.addWidget(self.check_apply_yaml)
        layout_apply.addWidget(self.check_apply_json)
        layout_apply.addStretch()
        group_apply.setLayout(layout_apply)
        layout.addWidget(group_apply)

        # === 옵션 2: 팩킹 워크플로우 ===
        group_workflow = QGroupBox(t("tab_apply.workflow_section"))
        layout_workflow = QVBoxLayout()

        self.workflow_group = QButtonGroup()

        self.radio_workflow_1 = QRadioButton(t("tab_apply.workflow_mode_1"))
        self.radio_workflow_2 = QRadioButton(t("tab_apply.workflow_mode_2"))
        self.radio_workflow_3 = QRadioButton(t("tab_apply.workflow_mode_3"))
        self.radio_workflow_4 = QRadioButton(t("tab_apply.workflow_mode_4"))

        self.workflow_group.addButton(self.radio_workflow_1, 1)
        self.workflow_group.addButton(self.radio_workflow_2, 2)
        self.workflow_group.addButton(self.radio_workflow_3, 3)
        self.workflow_group.addButton(self.radio_workflow_4, 4)

        # 기본값: 모드 2 (일반적인 사용 케이스)
        self.radio_workflow_2.setChecked(True)

        # 워크플로우 변경 시 버튼 텍스트 업데이트
        self.workflow_group.buttonClicked.connect(self.on_workflow_changed)

        layout_workflow.addWidget(self.radio_workflow_1)
        layout_workflow.addWidget(self.radio_workflow_2)
        layout_workflow.addWidget(self.radio_workflow_3)
        layout_workflow.addWidget(self.radio_workflow_4)

        # 워크플로우 설명
        workflow_info = QLabel(t("tab_apply.workflow_desc"))
        workflow_info.setStyleSheet("color: #666; font-size: 10px; margin-top: 5px;")
        layout_workflow.addWidget(workflow_info)

        group_workflow.setLayout(layout_workflow)
        layout.addWidget(group_workflow)

        # === 옵션 3: 추가 옵션 ===
        group_extra = QGroupBox(t("tab_apply.extra_options_section"))
        layout_extra = QVBoxLayout()

        self.check_delete_other = QCheckBox(t("tab_apply.delete_other"))
        self.check_delete_other.setChecked(False)
        layout_extra.addWidget(self.check_delete_other)

        extra_info = QLabel(t("tab_apply.delete_other_warning"))
        extra_info.setStyleSheet("color: #d9534f; font-size: 10px;")
        layout_extra.addWidget(extra_info)

        group_extra.setLayout(layout_extra)
        layout.addWidget(group_extra)

        # 실행 버튼
        self.btn_start = QPushButton(t("tab_apply.button_start_pack"))
        self.btn_start.clicked.connect(self.start_apply)
        self.btn_start.setStyleSheet("font-size: 14px; padding: 8px; font-weight: bold;")
        layout.addWidget(self.btn_start)

        # 진행 상태
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        # 로그 출력
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(QLabel(t("tab_apply.log")))
        layout.addWidget(self.log_text)

        self.setLayout(layout)

        # 초기 버튼 텍스트 설정
        self.update_button_text()

    def on_workflow_changed(self):
        """워크플로우 모드 변경 시 호출"""
        self.update_button_text()

    def update_button_text(self):
        """워크플로우 모드에 따라 버튼 텍스트 업데이트"""
        workflow_mode = self.workflow_group.checkedId()

        if workflow_mode in [1, 2]:
            self.btn_start.setText(t("tab_apply.button_start_pack"))
        elif workflow_mode in [3, 4]:
            self.btn_start.setText(t("tab_apply.button_start_no_pack"))

    def select_csv_folder(self):
        """CSV 폴더 선택"""
        folder_path = QFileDialog.getExistingDirectory(self, t("tab_apply.csv_folder"))
        if folder_path:
            self.csv_folder_edit.setText(folder_path)
            self.add_log(t("tab_apply.folder_selected", path=folder_path))

    def select_source_folder(self):
        """원본 폴더 선택"""
        folder_path = QFileDialog.getExistingDirectory(self, t("tab_apply.source_folder"))
        if folder_path:
            self.source_folder_edit.setText(folder_path)
            self.add_log(t("tab_apply.folder_selected", path=folder_path))

    def select_output_folder(self):
        """출력 폴더 선택"""
        folder_path = QFileDialog.getExistingDirectory(self, t("tab_apply.output_folder"))
        if folder_path:
            self.output_folder_edit.setText(folder_path)
            self.add_log(t("tab_apply.folder_selected", path=folder_path))

    def start_apply(self):
        """번역 적용 및 팩킹 시작"""
        # 입력 검증
        csv_folder = self.csv_folder_edit.text()
        source_folder = self.source_folder_edit.text()
        output_folder = self.output_folder_edit.text()

        if not csv_folder:
            QMessageBox.warning(self, t("common.error"), t("tab_apply.error_no_csv"))
            return

        if not source_folder:
            QMessageBox.warning(self, t("common.error"), t("tab_apply.error_no_source"))
            return

        # CSV 적용 대상 검증
        if not self.check_apply_yaml.isChecked() and not self.check_apply_json.isChecked():
            QMessageBox.warning(self, t("common.error"), t("tab_apply.error_no_target"))
            return

        if not Path(csv_folder).exists():
            QMessageBox.warning(self, t("common.error"), t("tab_apply.error_folder_not_found", path=csv_folder))
            return

        if not Path(source_folder).exists():
            QMessageBox.warning(self, t("common.error"), t("tab_apply.error_folder_not_found", path=source_folder))
            return

        # 워크플로우 모드 가져오기
        workflow_mode = self.workflow_group.checkedId()

        # 모드 1, 2는 팩킹하므로 출력 폴더 필요
        if workflow_mode in [1, 2]:
            if not output_folder:
                QMessageBox.warning(self, t("common.error"), t("tab_apply.error_no_output_mode12"))
                return

        # 출력 PAC 파일 경로 생성 (모드 1, 2만)
        output_pac = None
        if workflow_mode in [1, 2]:
            source_folder_name = Path(source_folder).name
            output_pac = Path(output_folder) / f"{source_folder_name}.pac"

        # UI 상태 변경
        self.btn_start.setEnabled(False)
        self.progress_bar.setValue(0)
        self.add_log(t("tab_apply.start_apply"))

        # 워커 스레드 생성 및 시작
        self.worker = ApplyWorker(
            csv_folder,
            source_folder,
            str(output_pac) if output_pac else None,
            workflow_mode,
            self.check_delete_other.isChecked(),
            apply_yaml=self.check_apply_yaml.isChecked(),
            apply_json=self.check_apply_json.isChecked()
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

    def add_log(self, message):
        """로그 추가"""
        self.log_text.append(message)
