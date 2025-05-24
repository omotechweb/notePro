from PyQt5.Qsci import QsciScintilla, QsciLexerPython, QsciLexerCPP, QsciLexerJava, QsciLexerJavaScript, QsciLexerCSS, QsciLexerHTML, QsciLexerXML
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt

class CodeEditor(QsciScintilla):
    def __init__(self, language="python", parent=None):
        super().__init__(parent)

        # Temel ayarlar
        self.setUtf8(True)
        font = QFont("Consolas", 12)
        self.setFont(font)
        self.setMarginsFont(font)

        # Satır numarası ayarı (Margin 0)
        fontmetrics = self.fontMetrics()
        self.setMarginWidth(0, fontmetrics.width("00000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#1e1e1e"))  # koyu margin arka planı
        self.setMarginsForegroundColor(QColor("#858585"))  # gri satır numaraları

        # Caret satırı koyu ton vurgusu
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#2a2d2e"))  # koyu gri satır arka planı

        # Koyu tema renk ayarları
        self.setPaper(QColor("#1e1e1e"))     # kod editör arka planı (çok koyu)
        self.setColor(QColor("#d4d4d4"))     # yazı rengi (açık gri, beyaz değil)
        self.setCaretForegroundColor(QColor("#d4d4d4"))  # imlec açık gri

        # Otomatik tamamlama
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionSource(QsciScintilla.AcsAll)

        # Parantez ve tırnak eşleştirme
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        self.setMatchedBraceBackgroundColor(QColor("#515c6a"))
        self.setMatchedBraceForegroundColor(QColor("#d4d4d4"))

        self.setAutoIndent(True)
        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(4)
        self.setBackspaceUnindents(True)

        self.language = language
        self.set_language(language)

    def set_language(self, language):
        lexer_class = None

        if language.lower() == "python":
            lexer_class = QsciLexerPython
        elif language.lower() == "c++":
            lexer_class = QsciLexerCPP
        elif language.lower() == "c#":
            lexer_class = QsciLexerCPP  # C# lexer yok, cpp lexer kullan
        elif language.lower() == "java":
            lexer_class = QsciLexerJava
        elif language.lower() == "javascript":
            lexer_class = QsciLexerJavaScript
        elif language.lower() == "rust":
            lexer_class = QsciLexerPython  # Rust lexer yok, python lexer geçici
        elif language.lower() == "html":
            lexer_class = QsciLexerHTML
        elif language.lower() == "css":
            lexer_class = QsciLexerCSS
        elif language.lower() == "xml":
            lexer_class = QsciLexerXML
        else:
            lexer_class = QsciLexerPython

        lexer = lexer_class()
        font = QFont("Consolas", 12)
        lexer.setFont(font)

        # Koyu tema arka plan ve yazı rengi varsayılan
        lexer.setPaper(QColor("#1e1e1e"))
        lexer.setColor(QColor("#d4d4d4"), lexer_class.Default)

        # Renkleri tanımlıysa atıyoruz (VS Code tarzı koyu tema renkleri)
        if hasattr(lexer_class, "Keyword"):
            lexer.setColor(QColor("#569CD6"), lexer_class.Keyword)  # Mavi
        if hasattr(lexer_class, "String"):
            lexer.setColor(QColor("#D69D85"), lexer_class.String)   # Turuncu
        if hasattr(lexer_class, "Comment"):
            lexer.setColor(QColor("#6A9955"), lexer_class.Comment)  # Yeşil
        if hasattr(lexer_class, "Number"):
            lexer.setColor(QColor("#B5CEA8"), lexer_class.Number)   # Açık yeşil
        if hasattr(lexer_class, "Operator"):
            lexer.setColor(QColor("#d4d4d4"), lexer_class.Operator) # Açık gri
        if hasattr(lexer_class, "Identifier"):
            lexer.setColor(QColor("#9CDCFE"), lexer_class.Identifier) # Açık mavi

        self.setLexer(lexer)

        # Editör genel renk ayarları
        self.setPaper(QColor("#1e1e1e"))
        self.setColor(QColor("#d4d4d4"))

        # Margin renkleri (satır numaraları ve boşluklar)
        self.setMarginsBackgroundColor(QColor("#1e1e1e"))
        self.setMarginsForegroundColor(QColor("#858585"))

        self.language = language
