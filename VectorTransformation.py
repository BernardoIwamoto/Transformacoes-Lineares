import sys
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QSlider, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QWidget, QLineEdit, QFormLayout, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class TransformationSimulator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Transformações Lineares 3D")
        self.setGeometry(100, 100, 1000, 800)

        # Vetores iniciais
        self.vectors = [np.array([3, 4, 5]), np.array([-4, 2, 1])]
        self.transformed_vectors = self.vectors.copy()

        # Cores disponíveis e associadas
        self.available_colors = ['blue', 'green', 'red', 'orange', 'purple', 'cyan', 'magenta', 'yellow']
        self.vector_colors = self.available_colors[:len(self.vectors)]

        # Layout principal
        main_layout = QVBoxLayout()
        self.canvas = FigureCanvas(Figure())
        main_layout.addWidget(self.canvas)

        # Criação dos sliders e botões
        self.create_controls(main_layout)

        # Widget principal
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Configuração do gráfico
        self.ax = self.canvas.figure.add_subplot(111, projection='3d')
        self.update_plot()

    def create_controls(self, layout):
        # Sliders de rotação
        self.rotation_sliders = {
            axis: QSlider(Qt.Horizontal)
            for axis in ['X', 'Y', 'Z']
        }
        for axis, slider in self.rotation_sliders.items():
            slider.setRange(-180, 180)
            slider.setValue(0)
            slider.valueChanged.connect(self.apply_transformations)
            layout.addWidget(QLabel(f"Rotação {axis} (°)"))
            layout.addWidget(slider)

        # Botões de reflexões
        for plane in ['XY', 'XZ', 'YZ']:
            button = QPushButton(f"Refletir no plano {plane}")
            button.clicked.connect(lambda _, p=plane: self.reflect_vectors(p))
            layout.addWidget(button)

        # Botões de manipulação de vetores
        add_vector_button = QPushButton("Adicionar Vetor")
        add_vector_button.clicked.connect(self.add_vector)
        layout.addWidget(add_vector_button)

        edit_vector_button = QPushButton("Editar Vetores")
        edit_vector_button.clicked.connect(self.edit_vectors)
        layout.addWidget(edit_vector_button)

        # Botão de projeção
        project_button = QPushButton("Projetar Vetores")
        project_button.clicked.connect(self.project_vectors)
        layout.addWidget(project_button)

        # Botão de reset
        reset_button = QPushButton("Resetar Transformações")
        reset_button.clicked.connect(self.reset_transformations)
        layout.addWidget(reset_button)

        # Coordenadas atuais
        self.coordinates_label = QLabel("Coordenadas dos vetores:")
        layout.addWidget(self.coordinates_label)

    def add_vector(self):
        """Abre um diálogo para adicionar um novo vetor."""
        dialog = VectorDialog()
        if dialog.exec_():
            vector = dialog.get_vector()
            self.vectors.append(vector)
            self.transformed_vectors.append(vector)

            # Escolhe uma cor não usada, ou reutiliza se todas foram usadas
            used_colors = set(self.vector_colors)
            available_colors = [c for c in self.available_colors if c not in used_colors]
            new_color = available_colors[0] if available_colors else self.available_colors[len(self.vector_colors) % len(self.available_colors)]
            self.vector_colors.append(new_color)

            self.update_plot()

    def edit_vectors(self):
        """Abre um diálogo para editar os vetores existentes."""
        dialog = VectorEditor(self.vectors)
        if dialog.exec_():
            self.vectors = dialog.get_vectors()
            self.transformed_vectors = self.vectors.copy()
            self.update_plot()

    def apply_transformations(self):
        angles = {
            axis: np.radians(self.rotation_sliders[axis].value())
            for axis in ['X', 'Y', 'Z']
        }

        rotation_matrix = self.get_rotation_matrix(angles)
        self.transformed_vectors = [np.dot(rotation_matrix, v) for v in self.vectors]
        self.update_plot()

    def get_rotation_matrix(self, angles):
        """Gera a matriz de rotação combinada para os ângulos fornecidos."""
        rx = np.array([
            [1, 0, 0],
            [0, np.cos(angles['X']), -np.sin(angles['X'])],
            [0, np.sin(angles['X']), np.cos(angles['X'])]
        ])
        ry = np.array([
            [np.cos(angles['Y']), 0, np.sin(angles['Y'])],
            [0, 1, 0],
            [-np.sin(angles['Y']), 0, np.cos(angles['Y'])]
        ])
        rz = np.array([
            [np.cos(angles['Z']), -np.sin(angles['Z']), 0],
            [np.sin(angles['Z']), np.cos(angles['Z']), 0],
            [0, 0, 1]
        ])
        return rz @ ry @ rx

    def reflect_vectors(self, plane):
        reflection_matrices = {
            'XY': np.array([[1, 0, 0], [0, 1, 0], [0, 0, -1]]),
            'XZ': np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]]),
            'YZ': np.array([[-1, 0, 0], [0, 1, 0], [0, 0, 1]])
        }
        matrix = reflection_matrices[plane]
        self.transformed_vectors = [np.dot(matrix, v) for v in self.transformed_vectors]
        self.update_plot()

    def project_vectors(self):
        """Projeta todos os vetores no primeiro vetor."""
        if not self.vectors:
            return
        base = self.vectors[0]
        base_norm = np.linalg.norm(base)
        if base_norm == 0:
            return
        base_unit = base / base_norm

        self.transformed_vectors = [
            np.dot(v, base_unit) * base_unit for v in self.vectors
        ]
        self.update_plot()

    def reset_transformations(self):
        self.transformed_vectors = self.vectors.copy()
        for slider in self.rotation_sliders.values():
            slider.setValue(0)
        self.update_plot()

    def update_plot(self):
        """Atualiza o gráfico 3D com os vetores transformados."""
        self.ax.clear()
        self.ax.set_xlim([-10, 10])
        self.ax.set_ylim([-10, 10])
        self.ax.set_zlim([-10, 10])
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

        coordinates_text = "Coordenadas dos vetores:\n"
        for i, (vector, color) in enumerate(zip(self.transformed_vectors, self.vector_colors)):
            self.ax.quiver(0, 0, 0, vector[0], vector[1], vector[2], color=color)
            coordinates_text += f"Vetor {i + 1} ({color}): {vector}\n"

        self.coordinates_label.setText(coordinates_text)
        self.canvas.draw()


class VectorDialog(QDialog):
    """Diálogo para adicionar um novo vetor."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adicionar Novo Vetor")
        self.layout = QFormLayout()

        self.x_input = QLineEdit()
        self.y_input = QLineEdit()
        self.z_input = QLineEdit()

        self.layout.addRow("Componente X:", self.x_input)
        self.layout.addRow("Componente Y:", self.y_input)
        self.layout.addRow("Componente Z:", self.z_input)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

    def get_vector(self):
        return np.array([
            float(self.x_input.text()), 
            float(self.y_input.text()), 
            float(self.z_input.text())
        ])


class VectorEditor(QDialog):
    """Diálogo para editar vetores existentes."""
    def __init__(self, vectors):
        super().__init__()
        self.setWindowTitle("Editar Vetores")
        self.layout = QVBoxLayout()
        self.inputs = []

        for i, vector in enumerate(vectors):
            form = QFormLayout()
            x_input = QLineEdit(str(vector[0]))
            y_input = QLineEdit(str(vector[1]))
            z_input = QLineEdit(str(vector[2]))
            self.inputs.append((x_input, y_input, z_input))
            form.addRow(f"Vetor {i + 1} - X:", x_input)
            form.addRow(f"Vetor {i + 1} - Y:", y_input)
            form.addRow(f"Vetor {i + 1} - Z:", z_input)
            self.layout.addLayout(form)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

    def get_vectors(self):
        vectors = []
        for x_input, y_input, z_input in self.inputs:
            vectors.append(np.array([
                float(x_input.text()), 
                float(y_input.text()), 
                float(z_input.text())
            ]))
        return vectors


if __name__ == '__main__':
    app = QApplication(sys.argv)
    simulator = TransformationSimulator()
    simulator.show()
    sys.exit(app.exec_())
