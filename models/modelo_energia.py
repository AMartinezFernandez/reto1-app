from PySide6.QtCore import QObject, Signal, Slot


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
