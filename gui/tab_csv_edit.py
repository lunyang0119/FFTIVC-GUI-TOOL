"""
Tab 3: CSV Edit
"""
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                              QPushButton, QLineEdit, QTextEdit, QCheckBox,
                              QFileDialog, QGroupBox, QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal
from core.validator import CSVValidator
from core.csv_handler import CSVHandler
from utils.i18n import t

class ValidationWorker(QThread):
    """Worker thread for validation tasks"""

    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, list)

    def __init__(self, csv_folder):
        super().__init__()
        self.csv_folder = csv_folder

    def run(self):
        """Execute task"""
        try:
            validator = CSVValidator()
            self.log_signal.emit(t("tab_csv_edit.log_validation_start"))

            results = validator.validate_csv(self.csv_folder)

            self.log_signal.emit(t("tab_csv_edit.log_validation_complete"))
            self.finished_signal.emit(True, results)

        except Exception as e:
            self.log_signal.emit(t("tab_csv_edit.log_error", error=str(e)))
            self.finished_signal.emit(False, [])


class ReplaceWorker(QThread):
    """Worker thread for replace tasks"""

    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, int)

    def __init__(self, csv_folder, find_text, replace_text, translated_only):
        super().__init__()
        self.csv_folder = csv_folder
        self.find_text = find_text
        self.replace_text = replace_text
        self.translated_only = translated_only

    def run(self):
        """Execute task"""
        try:
            csv_handler = CSVHandler()
            self.log_signal.emit(t("tab_csv_edit.log_replace_start"))

            count = csv_handler.batch_replace(
                self.csv_folder,
                self.find_text,
                self.replace_text,
                self.translated_only
            )

            self.log_signal.emit(t("tab_csv_edit.log_replace_complete", count=count))
            self.finished_signal.emit(True, count)

        except Exception as e:
            self.log_signal.emit(t("tab_csv_edit.log_error", error=str(e)))
            self.finished_signal.emit(False, 0)


class TabCSVEdit(QWidget):
    """CSV validation and edit tab"""

    def __init__(self):
        super().__init__()
        self.validation_worker = None
        self.replace_worker = None
        self.validation_results = []
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()

        # CSV file validation
        group_validate = QGroupBox(t("tab_csv_edit.validation"))
        layout_validate = QVBoxLayout()
        info_label = QLabel(t("tab_csv_edit.validation_info"))
        info_label.setStyleSheet("color: #666; font-size: 10px;")
        layout_options = QVBoxLayout()
        layout_options.addWidget(info_label)

        # CSV folder selection
        layout_folder = QHBoxLayout()
        self.csv_folder_edit = QLineEdit()
        self.csv_folder_edit.setReadOnly(True)
        self.csv_folder_edit.setPlaceholderText(t("tab_csv_edit.select_folder"))
        btn_select_folder = QPushButton(t("common.select_folder"))
        btn_select_folder.clicked.connect(self.select_csv_folder)
        layout_folder.addWidget(QLabel(t("tab_csv_edit.csv_folder")))
        layout_folder.addWidget(self.csv_folder_edit)
        layout_folder.addWidget(btn_select_folder)
        layout_validate.addLayout(layout_folder)

        # Validation button
        self.btn_validate = QPushButton(t("tab_csv_edit.validate_button"))
        self.btn_validate.clicked.connect(self.validate_csv)
        layout_validate.addWidget(self.btn_validate)

        # Validation results (summary)
        self.validate_summary = QTextEdit()
        self.validate_summary.setReadOnly(True)
        self.validate_summary.setMaximumHeight(100)
        layout_validate.addWidget(QLabel(t("tab_csv_edit.summary")))
        layout_validate.addWidget(self.validate_summary)

        # Validation results (detail)
        self.validate_detail = QTextEdit()
        self.validate_detail.setReadOnly(True)
        self.validate_detail.setMaximumHeight(300)
        layout_validate.addWidget(QLabel(t("tab_csv_edit.detail")))
        layout_validate.addWidget(self.validate_detail)

        # Save result button
        self.btn_save_result = QPushButton(t("tab_csv_edit.save_result"))
        self.btn_save_result.clicked.connect(self.save_validation_result)
        layout_validate.addWidget(self.btn_save_result)

        group_validate.setLayout(layout_validate)
        layout.addWidget(group_validate)

        # Batch text replace
        group_replace = QGroupBox(t("tab_csv_edit.replace"))
        info_label_2 = QLabel(t("tab_csv_edit.replace_info"))
        info_label_2.setStyleSheet("color: #666; font-size: 10px;")
        layout_options.addWidget(info_label_2)
        layout_replace = QVBoxLayout()

        # Replace target folder
        layout_replace_folder = QHBoxLayout()
        self.replace_folder_edit = QLineEdit()
        self.replace_folder_edit.setReadOnly(True)
        self.replace_folder_edit.setPlaceholderText(t("tab_csv_edit.replace_folder"))
        btn_select_replace_folder = QPushButton(t("common.select_folder"))
        btn_select_replace_folder.clicked.connect(self.select_replace_folder)
        layout_replace_folder.addWidget(QLabel(t("tab_csv_edit.csv_folder")))
        layout_replace_folder.addWidget(self.replace_folder_edit)
        layout_replace_folder.addWidget(btn_select_replace_folder)
        layout_replace.addLayout(layout_replace_folder)

        # Find text
        layout_find = QHBoxLayout()
        self.find_text_edit = QLineEdit()
        self.find_text_edit.setPlaceholderText(t("tab_csv_edit.find_text_placeholder"))
        layout_find.addWidget(QLabel(t("tab_csv_edit.find_text")))
        layout_find.addWidget(self.find_text_edit)
        layout_replace.addLayout(layout_find)

        # Replace text
        layout_replace_text = QHBoxLayout()
        self.replace_text_edit = QLineEdit()
        self.replace_text_edit.setPlaceholderText(t("tab_csv_edit.replace_text_placeholder"))
        layout_replace_text.addWidget(QLabel(t("tab_csv_edit.replace_text")))
        layout_replace_text.addWidget(self.replace_text_edit)
        layout_replace.addLayout(layout_replace_text)

        # Options
        self.check_translated_only = QCheckBox(t("tab_csv_edit.translated_only"))
        self.check_translated_only.setChecked(True)
        layout_replace.addWidget(self.check_translated_only)

        # Replace button
        self.btn_replace = QPushButton(t("tab_csv_edit.replace_button"))
        self.btn_replace.clicked.connect(self.batch_replace)
        layout_replace.addWidget(self.btn_replace)

        # Replace log
        self.replace_log = QTextEdit()
        self.replace_log.setReadOnly(True)
        self.replace_log.setMaximumHeight(100)
        layout_replace.addWidget(QLabel(t("tab_csv_edit.replace_log")))
        layout_replace.addWidget(self.replace_log)

        group_replace.setLayout(layout_replace)
        layout.addWidget(group_replace)

        self.setLayout(layout)

    def select_csv_folder(self):
        """Select CSV folder for validation"""
        folder_path = QFileDialog.getExistingDirectory(self, t("tab_csv_edit.dialog_select_folder"))
        if folder_path:
            self.csv_folder_edit.setText(folder_path)
            self.add_validate_log(t("tab_csv_edit.folder_selected", path=folder_path))

    def select_replace_folder(self):
        """Select CSV folder for replace"""
        folder_path = QFileDialog.getExistingDirectory(self, t("tab_csv_edit.dialog_select_folder"))
        if folder_path:
            self.replace_folder_edit.setText(folder_path)
            self.add_replace_log(t("tab_csv_edit.folder_selected", path=folder_path))

    def validate_csv(self):
        """CSV file validation"""
        csv_folder = self.csv_folder_edit.text()

        if not csv_folder:
            QMessageBox.warning(self, t("common.warning"), t("tab_csv_edit.error_no_folder"))
            return

        if not Path(csv_folder).exists():
            QMessageBox.warning(self, t("common.warning"), t("tab_csv_edit.error_folder_not_found", path=csv_folder))
            return

        # Change UI state
        self.btn_validate.setEnabled(False)
        self.validate_summary.clear()
        self.validate_detail.clear()

        # Create and start worker thread
        self.validation_worker = ValidationWorker(csv_folder)

        # Connect signals
        self.validation_worker.log_signal.connect(self.add_validate_log)
        self.validation_worker.finished_signal.connect(self.on_validation_finished)

        # Start thread
        self.validation_worker.start()

    def on_validation_finished(self, success, results):
        """Called when validation is finished"""
        self.btn_validate.setEnabled(True)
        self.validation_results = results

        if success:
            from core.validator import CSVValidator
            validator = CSVValidator()

            # Show summary
            summary = validator.get_validation_summary(results)
            self.validate_summary.setPlainText(summary)

            # Show detailed results
            if len(results) > 0:
                detail = validator.get_detailed_validation_text(results)
                self.validate_detail.setPlainText(detail)
                QMessageBox.warning(self, t("tab_csv_edit.validation_complete"), t("tab_csv_edit.issues_found", count=len(results)))
            else:
                self.validate_detail.setPlainText(t("tab_csv_edit.no_issues_detail"))
                QMessageBox.information(self, t("tab_csv_edit.validation_complete"), t("tab_csv_edit.no_issues"))
        else:
            QMessageBox.critical(self, t("common.error"), t("tab_csv_edit.validation_error"))

        self.validation_worker = None

    def save_validation_result(self):
        """Save validation result"""
        if not self.validation_results:
            QMessageBox.warning(self, t("common.warning"), t("tab_csv_edit.save_error"))
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, t("tab_csv_edit.dialog_save_result"), "", "Text Files (*.txt)"
        )
        if file_path:
            try:
                validator = CSVValidator()
                validator.save_validation_result(self.validation_results, file_path)
                QMessageBox.information(self, t("common.completed"), t("tab_csv_edit.save_complete", path=file_path))
                self.add_validate_log(t("tab_csv_edit.log_result_saved", path=file_path))
            except Exception as e:
                QMessageBox.critical(self, t("common.error"), t("tab_csv_edit.save_failed", error=str(e)))

    def batch_replace(self):
        """Batch text replace"""
        csv_folder = self.replace_folder_edit.text()
        find_text = self.find_text_edit.text()
        replace_text = self.replace_text_edit.text()

        if not csv_folder:
            QMessageBox.warning(self, t("common.warning"), t("tab_csv_edit.error_no_folder"))
            return

        if not find_text:
            QMessageBox.warning(self, t("common.warning"), t("tab_csv_edit.error_no_find_text"))
            return

        if not Path(csv_folder).exists():
            QMessageBox.warning(self, t("common.warning"), t("tab_csv_edit.error_folder_not_found", path=csv_folder))
            return

        # Confirmation message
        reply = QMessageBox.question(
            self,
            t("tab_csv_edit.dialog_confirm"),
            t("tab_csv_edit.replace_confirm", find=find_text, replace=replace_text),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        # Change UI state
        self.btn_replace.setEnabled(False)
        self.replace_log.clear()

        # Create and start worker thread
        self.replace_worker = ReplaceWorker(
            csv_folder,
            find_text,
            replace_text,
            self.check_translated_only.isChecked()
        )

        # Connect signals
        self.replace_worker.log_signal.connect(self.add_replace_log)
        self.replace_worker.finished_signal.connect(self.on_replace_finished)

        # Start thread
        self.replace_worker.start()

    def on_replace_finished(self, success, count):
        """Called when replace is finished"""
        self.btn_replace.setEnabled(True)

        if success:
            QMessageBox.information(self, t("common.completed"), t("tab_csv_edit.replace_complete", count=count))
        else:
            QMessageBox.critical(self, t("common.error"), t("tab_csv_edit.replace_error"))

        self.replace_worker = None

    def add_validate_log(self, message):
        """Add validation log"""
        self.validate_summary.append(message)

    def add_replace_log(self, message):
        """Add replace log"""
        self.replace_log.append(message)
