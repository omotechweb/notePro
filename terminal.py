from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit, QLineEdit
from PyQt5.QtCore import QProcess


class Terminal(QWidget):
    def __init__(self):
        super().__init__()

        self.output_area = QPlainTextEdit()
        self.output_area.setReadOnly(True)

        self.input_line = QLineEdit()
        self.input_line.returnPressed.connect(self.run_command)

        layout = QVBoxLayout()
        layout.addWidget(self.output_area)
        layout.addWidget(self.input_line)
        self.setLayout(layout)

        self.encoding = "mbcs"

        # Çalışan işlemleri tutmak için liste
        self.processes = []

    def run_command(self):
        command = self.input_line.text().strip()
        if not command:
            return
        self.output_area.appendPlainText(f"> {command}")

        process = QProcess(self)
        self.processes.append(process)  # Listeye ekle

        process.setProgram("cmd.exe")
        process.setArguments(['/c', command])
        process.readyReadStandardOutput.connect(lambda p=process: self.handle_stdout(p))
        process.readyReadStandardError.connect(lambda p=process: self.handle_stderr(p))
        process.finished.connect(lambda exitCode, exitStatus, p=process: self.process_finished(p))
        process.start()

        self.input_line.clear()

    def handle_stdout(self, process):
        data = process.readAllStandardOutput()
        text = bytes(data).decode(self.encoding, errors='replace')
        self.output_area.appendPlainText(text)

    def handle_stderr(self, process):
        data = process.readAllStandardError()
        text = bytes(data).decode(self.encoding, errors='replace')
        self.output_area.appendPlainText(text)

    def process_finished(self, process):
        if process in self.processes:
            self.processes.remove(process)
        process.deleteLater()
