import sys

from PySide6.QtCore import QObject, QEasingCurve, QRectF, QSize, Qt, Signal, Slot, QVariantAnimation
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QLabel, QSlider, QSpinBox, QVBoxLayout, QWidget


class ModeloEnergia(QObject):
    nivelCambiado = Signal(int)

    def __init__(self):
        super().__init__()
        self.nivel = 50

    @Slot(int)
    def establecer_nivel(self, nuevo_nivel):
        # Rango
        nivel_ajustado = max(0, min(100, int(nuevo_nivel)))
        if nivel_ajustado == self.nivel:
            return

        self.nivel = nivel_ajustado
        # Aviso
        self.nivelCambiado.emit(self.nivel)


class MedidorEnergiaRadial(QWidget):
    def __init__(self, principal=None):
        super().__init__(principal)

        self.valor_dibujado = 0.0
        self.grosor_anillo = 16
        self.color_tema = QColor("#E0B400")
        self.color_fondo_anillo = QColor("#D0D0D0")

        # Animacion
        self.animacion = QVariantAnimation(self)
        self.animacion.setDuration(400)
        self.animacion.setEasingCurve(QEasingCurve.OutCubic)
        self.animacion.valueChanged.connect(self.actualizar_valor_dibujado)

        self.setMinimumSize(140, 140)

    def sizeHint(self):
        return QSize(220, 220)

    @Slot(int)
    def establecer_valor(self, nuevo_valor):
        self.animacion.stop()
        self.animacion.setStartValue(self.valor_dibujado)
        self.animacion.setEndValue(float(nuevo_valor))
        self.animacion.start()

    @Slot(int)
    def establecer_grosor(self, grosor):
        self.grosor_anillo = max(6, min(40, int(grosor)))
        self.update()

    @Slot(str)
    def establecer_color_tema(self, color):
        qcolor = QColor(color)
        if qcolor.isValid():
            self.color_tema = qcolor
            self.update()

    @Slot(object)
    def actualizar_valor_dibujado(self, valor):
        self.valor_dibujado = float(valor)
        self.update()

    def color_por_nivel(self, nivel):
        if nivel < 35:
            return QColor("#D64545")
        if nivel < 70:
            return QColor(self.color_tema)
        return QColor("#3AA757")

    def paintEvent(self, evento):
        del evento
        dibujo = QPainter(self)
        dibujo.setRenderHint(QPainter.Antialiasing, True)

        lado = min(self.width(), self.height())
        margen = self.grosor_anillo / 2.0 + 10.0
        diametro = max(20.0, lado - 2.0 * margen)
        # Area
        rect_anillo = QRectF(
            (self.width() - diametro) / 2.0,
            (self.height() - diametro) / 2.0,
            diametro,
            diametro,
        )

        # Fondo
        trazo_fondo = QPen(self.color_fondo_anillo, self.grosor_anillo)
        trazo_fondo.setCapStyle(Qt.RoundCap)
        dibujo.setPen(trazo_fondo)
        dibujo.drawArc(rect_anillo, 0, 360 * 16)

        # Progreso
        trazo_progreso = QPen(self.color_por_nivel(self.valor_dibujado), self.grosor_anillo)
        trazo_progreso.setCapStyle(Qt.RoundCap)
        dibujo.setPen(trazo_progreso)
        extension = int(-(self.valor_dibujado / 100.0) * 360.0 * 16.0)
        dibujo.drawArc(rect_anillo, 90 * 16, extension)

        # Texto
        fuente = QFont(self.font())
        fuente.setBold(True)
        fuente.setPointSizeF(max(11.0, diametro * 0.16))
        dibujo.setFont(fuente)
        dibujo.setPen(QColor("#202020"))
        dibujo.drawText(rect_anillo, Qt.AlignCenter, f"{int(round(self.valor_dibujado))}%")


class VentanaPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medidor de Energía Radial")

        self.modelo = ModeloEnergia()
        self.crear_interfaz()
        self.conectar_eventos()

        self.medidor.establecer_valor(self.modelo.nivel)
        self.actualizar_estado(self.modelo.nivel)

    def crear_interfaz(self):
        self.medidor = MedidorEnergiaRadial()

        # Controles
        self.slider_valor = QSlider(Qt.Horizontal)
        self.slider_valor.setRange(0, 100)
        self.slider_valor.setValue(self.modelo.nivel)

        self.entrada_valor = QSpinBox()
        self.entrada_valor.setRange(0, 100)
        self.entrada_valor.setSuffix("%")
        self.entrada_valor.setValue(self.modelo.nivel)

        self.combo_tema = QComboBox()
        self.combo_tema.addItem("Amarillo", "#E0B400")
        self.combo_tema.addItem("Azul", "#3A7BD5")
        self.combo_tema.addItem("Naranja", "#E67E22")

        self.slider_grosor = QSlider(Qt.Horizontal)
        self.slider_grosor.setRange(6, 40)
        self.slider_grosor.setValue(self.medidor.grosor_anillo)

        self.etiqueta_estado = QLabel()
        self.etiqueta_estado.setAlignment(Qt.AlignCenter)

        fila_valor = QHBoxLayout()
        fila_valor.addWidget(QLabel("Nivel"))
        fila_valor.addWidget(self.slider_valor, 1)
        fila_valor.addWidget(self.entrada_valor)

        fila_tema = QHBoxLayout()
        fila_tema.addWidget(QLabel("Tema"))
        fila_tema.addWidget(self.combo_tema, 1)

        fila_grosor = QHBoxLayout()
        fila_grosor.addWidget(QLabel("Grosor"))
        fila_grosor.addWidget(self.slider_grosor, 1)

        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(self.medidor, 1)
        layout_principal.addWidget(self.etiqueta_estado)
        layout_principal.addLayout(fila_valor)
        layout_principal.addLayout(fila_tema)
        layout_principal.addLayout(fila_grosor)

    def conectar_eventos(self):
        # Modelo
        self.slider_valor.valueChanged.connect(self.modelo.establecer_nivel)
        self.entrada_valor.valueChanged.connect(self.modelo.establecer_nivel)

        # Vista
        self.modelo.nivelCambiado.connect(self.medidor.establecer_valor)
        self.modelo.nivelCambiado.connect(self.sincronizar_valor)
        self.modelo.nivelCambiado.connect(self.actualizar_estado)

        # Tema
        self.slider_grosor.valueChanged.connect(self.medidor.establecer_grosor)
        self.combo_tema.currentIndexChanged.connect(self.cambiar_tema)

    @Slot(int)
    def sincronizar_valor(self, valor):
        # Sin bucle
        self.slider_valor.blockSignals(True)
        self.entrada_valor.blockSignals(True)
        self.slider_valor.setValue(valor)
        self.entrada_valor.setValue(valor)
        self.slider_valor.blockSignals(False)
        self.entrada_valor.blockSignals(False)

    @Slot(int)
    def actualizar_estado(self, valor):
        if valor < 35:
            texto = "Energía baja"
        elif valor < 70:
            texto = "Energía media"
        else:
            texto = "Energía alta"
        self.etiqueta_estado.setText(f"{texto} ({valor}%)")

    @Slot(int)
    def cambiar_tema(self, indice):
        del indice
        self.medidor.establecer_color_tema(self.combo_tema.currentData())


def main():
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.resize(420, 520)
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
