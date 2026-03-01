import sys

from PySide6.QtWidgets import QApplication

from widgets import VentanaPrincipal


def main():
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.resize(420, 520)
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
