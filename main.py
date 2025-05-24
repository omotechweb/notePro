import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QFileDialog,
                             QMessageBox, QAction, QMenu, QToolBar, QWidget,
                             QVBoxLayout, QComboBox, QLabel, QHBoxLayout)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QProcess

from editor import CodeEditor  # Az önce verdiğim editor.py dosyasından

class Terminal(QWidget):
    def __init__(self):
        super().__init__()
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.on_readyReadStandardOutput)

        self.layout = QVBoxLayout(self)
        from PyQt5.QtWidgets import QTextEdit, QLineEdit

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.input = QLineEdit()

        self.layout.addWidget(self.output)
        self.layout.addWidget(self.input)

        self.input.returnPressed.connect(self.execute_command)

        # Başlat cmd.exe (Windows için)
        self.process.start("cmd")

    def execute_command(self):
        cmd = self.input.text()
        if cmd.strip() == "":
            return
        self.process.write((cmd + "\n").encode())
        self.input.clear()

    def on_readyReadStandardOutput(self):
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode('cp437')  # Windows cmd kodlama cp437 oluyor
        self.output.append(text)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PyNotePro - VSCode Style Dark Mode Editor")
        self.resize(1000, 700)
        self.setWindowIcon(QIcon())  # İstersen icon ekle

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # İlk sekme: Kod editörü (Python dili varsayılan)
        self.add_code_tab(language="python")

        # İkinci sekme: Terminal
        self.add_terminal_tab()

        # Menü ve araç çubuğu
        self.create_menu()
        self.create_toolbar()

        # Dark mode uygula
        self.apply_dark_mode()

    def create_menu(self):
        menubar = self.menuBar()

        # Dosya Menüsü
        file_menu = menubar.addMenu("Dosya")

        new_action = QAction("Yeni Sekme", self)
        new_action.triggered.connect(self.new_tab)
        file_menu.addAction(new_action)

        open_action = QAction("Dosya Aç", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Dosya Kaydet", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        exit_action = QAction("Çıkış", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Dil Menüsü
        language_menu = menubar.addMenu("Dil")

        languages = ["python", "c++", "c#", "java", "javascript", "rust", "html", "css", "xml"]
        for lang in languages:
            action = QAction(lang.capitalize(), self)
            action.triggered.connect(lambda checked, l=lang: self.change_language(l))
            language_menu.addAction(action)

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        new_btn = QAction("Yeni Sekme", self)
        new_btn.triggered.connect(self.new_tab)
        toolbar.addAction(new_btn)

        open_btn = QAction("Dosya Aç", self)
        open_btn.triggered.connect(self.open_file)
        toolbar.addAction(open_btn)

        save_btn = QAction("Dosya Kaydet", self)
        save_btn.triggered.connect(self.save_file)
        toolbar.addAction(save_btn)

        # Dil seçici combobox
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Python", "C++", "C#", "Java", "JavaScript", "Rust", "HTML", "CSS", "XML"])
        self.lang_combo.currentIndexChanged.connect(self.toolbar_language_changed)
        toolbar.addWidget(self.lang_combo)

    def add_code_tab(self, language="python", file_path=None, content=""):
        editor = CodeEditor(language=language)
        if content:
            editor.setText(content)
        tab_index = self.tabs.addTab(editor, "Yeni Dosya" if not file_path else file_path.split("/")[-1])
        self.tabs.setCurrentIndex(tab_index)

        # Dosya yolu ve dili sekmeye bağla
        editor.file_path = file_path
        editor.language = language

    def add_terminal_tab(self):
        terminal = Terminal()
        tab_index = self.tabs.addTab(terminal, "Terminal")
        # Terminal sekmesine geçiş
        self.tabs.setCurrentIndex(tab_index)

    def new_tab(self):
        self.add_code_tab(language="python")

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Dosya Aç", "", "Tüm Dosyalar (*.*)")
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Dosya açılamadı:\n{e}")
            return

        # Dosya uzantısına göre dil belirle
        lang = self.get_language_from_extension(file_path)

        self.add_code_tab(language=lang, file_path=file_path, content=content)

    def save_file(self):
        editor = self.current_editor()
        if editor is None:
            QMessageBox.warning(self, "Hata", "Kod editörü açık değil.")
            return

        if editor.file_path is None:
            file_path, _ = QFileDialog.getSaveFileName(self, "Dosya Kaydet", "", "Tüm Dosyalar (*.*)")
            if not file_path:
                return
            editor.file_path = file_path

        try:
            with open(editor.file_path, "w", encoding="utf-8") as f:
                f.write(editor.text())
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Dosya kaydedilemedi:\n{e}")
            return

        # Sekme başlığını güncelle
        self.tabs.setTabText(self.tabs.currentIndex(), editor.file_path.split("/")[-1])

    def change_language(self, language):
        editor = self.current_editor()
        if editor:
            editor.set_language(language)
            editor.language = language
            # Toolbar combobox da güncelle
            index = self.lang_combo.findText(language.capitalize())
            if index != -1:
                self.lang_combo.setCurrentIndex(index)

    def toolbar_language_changed(self, index):
        lang = self.lang_combo.currentText().lower()
        self.change_language(lang)

    def current_editor(self):
        widget = self.tabs.currentWidget()
        # Sadece CodeEditor döndürülecek, terminal değil
        if isinstance(widget, CodeEditor):
            return widget
        return None

    def get_language_from_extension(self, path):
        ext = path.split(".")[-1].lower()
        mapping = {
            "py": "python",
            "cpp": "c++",
            "c": "c++",
            "cs": "c#",
            "java": "java",
            "js": "javascript",
            "rs": "rust",
            "html": "html",
            "htm": "html",
            "css": "css",
            "xml": "xml",
        }
        return mapping.get(ext, "python")

    def apply_dark_mode(self):
        # VSCode tarzı koyu tema (sadece örnek, geliştirilebilir)
        dark_stylesheet = """
        QMainWindow {
            background-color: #1e1e1e;
        }
        QTabWidget::pane {
            border: 1px solid #444;
            background: #252526;
        }
        QTabBar::tab {
            background: #2d2d30;
            color: #cccccc;
            padding: 8px;
            border: 1px solid #444;
            border-bottom-color: #252526;
            min-width: 80px;
        }
        QTabBar::tab:selected {
            background: #007acc;
            color: white;
            border: 1px solid #007acc;
            border-bottom-color: #1e1e1e;
        }
        QTabBar::tab:hover {
            background: #3e3e42;
        }
        QToolBar {
            background: #333333;
            border-bottom: 1px solid #444;
        }
        QMenuBar {
            background: #2d2d30;
            color: #cccccc;
        }
        QMenuBar::item:selected {
            background: #007acc;
        }
        QMenu {
            background: #252526;
            color: #cccccc;
            border: 1px solid #444;
        }
        QMenu::item:selected {
            background: #007acc;
        }
        QTextEdit, QLineEdit {
            background-color: #1e1e1e;
            color: #d4d4d4;
            border: none;
        }
        QComboBox {
            background-color: #3c3c3c;
            color: #d4d4d4;
            border: 1px solid #555;
            padding: 2px 5px;
        }
        QPushButton {
            background-color: #0e639c;
            color: white;
            border: none;
            padding: 5px 10px;
        }
        QPushButton:hover {
            background-color: #1177cc;
        }
        """
        self.setStyleSheet(dark_stylesheet)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

# hello world
# this is the first version of notepro 
# thanks for your helps