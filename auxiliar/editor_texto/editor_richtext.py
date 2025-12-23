# auxiliar/widgets/editor_richtext.py
from PyQt5.QtWidgets import QTextEdit, QToolBar, QAction, QColorDialog, QFontComboBox, QSpinBox
from PyQt5.QtGui import QTextCharFormat, QFont, QColor
from PyQt5.QtCore import Qt

class EditorTextoEnriquecido(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setAcceptRichText(True)

        # Fondo SIEMPRE blanco
        self.setStyleSheet("""
            QTextEdit {
                background: white;
                color: black;
            }
        """)

    def toolbar(self):
        tb = QToolBar()

        # Fuente
        font_box = QFontComboBox()
        font_box.currentFontChanged.connect(
            lambda f: self._set_format(font=f)
        )
        tb.addWidget(font_box)

        # Tamaño
        size_box = QSpinBox()
        size_box.setRange(8, 48)
        size_box.setValue(10)
        size_box.valueChanged.connect(
            lambda s: self._set_format(size=s)
        )
        tb.addWidget(size_box)

        # Negrita / Cursiva / Subrayado
        for texto, attr in [("B", "bold"), ("I", "italic"), ("U", "underline")]:
            act = QAction(texto, self)
            act.setCheckable(True)
            act.triggered.connect(lambda _, a=attr: self._toggle(a))
            tb.addAction(act)

        # Color texto
        act_color = QAction("Color", self)
        act_color.triggered.connect(self._color_texto)
        tb.addAction(act_color)

        # Resaltado
        act_bg = QAction("Resaltado", self)
        act_bg.triggered.connect(self._color_fondo)
        tb.addAction(act_bg)

        # Alineación
        for txt, align in [
            ("Izq", Qt.AlignLeft),
            ("Centro", Qt.AlignCenter),
            ("Der", Qt.AlignRight),
            ("Just", Qt.AlignJustify),
        ]:
            act = QAction(txt, self)
            act.triggered.connect(lambda _, a=align: self.setAlignment(a))
            tb.addAction(act)

        # Listas
        tb.addAction("•", lambda: self.insertHtml("<ul><li></li></ul>"))
        tb.addAction("1.", lambda: self.insertHtml("<ol><li></li></ol>"))

        # Cortar / Copiar / Pegar
        tb.addAction("✂", self.cut)
        tb.addAction("📋", self.copy)
        tb.addAction("📄", self.paste)

        return tb

    def _set_format(self, font=None, size=None):
        fmt = QTextCharFormat()
        if font:
            fmt.setFont(font)
        if size:
            fmt.setFontPointSize(size)
        self.mergeCurrentCharFormat(fmt)

    def _toggle(self, attr):
        fmt = QTextCharFormat()
        if attr == "bold":
            fmt.setFontWeight(QFont.Bold if self.fontWeight() != QFont.Bold else QFont.Normal)
        elif attr == "italic":
            fmt.setFontItalic(not self.fontItalic())
        elif attr == "underline":
            fmt.setFontUnderline(not self.fontUnderline())
        self.mergeCurrentCharFormat(fmt)

    def _color_texto(self):
        color = QColorDialog.getColor()
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            self.mergeCurrentCharFormat(fmt)

    def _color_fondo(self):
        color = QColorDialog.getColor()
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setBackground(color)
            self.mergeCurrentCharFormat(fmt)