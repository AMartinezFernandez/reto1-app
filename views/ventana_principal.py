from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QSlider, QSpinBox, QVBoxLayout, QWidget

from widgets import ModeloEnergia
from widgets import MedidorEnergiaRadial


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
