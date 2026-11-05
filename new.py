import sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QRectF
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QSlider, QLabel, QComboBox, QSpinBox, QFileDialog,
    QSplitter, QFrame, QMessageBox, QDoubleSpinBox
)
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QFont
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# Character Sets
CHAR_SETS = {
    "Binary / CMatrix": "01",
    "Standard": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "Detailed": "@$B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "Blocks": "█▓▒░ ",
    "Simple": "@#*+:-. "
}

COLOR_SCHEMES = {
    "Original Colors": "ORIGINAL",
    "Matrix Green": (50, 205, 50),
    "Cyberpunk Green": (0, 255, 170),
    "Retro Amber": (255, 176, 0),
    "Cyan": (0, 229, 255),
    "White": (240, 240, 240)
}


def process_ascii_frame(frame, viewport_w, viewport_h, density_cols, char_set_name, color_mode, effect_name="None"):
    """
    Renders ASCII frames sized to match 100% of viewport dimensions,
    mimicking web canvas scaling.
    """
    ascii_chars = CHAR_SETS.get(char_set_name, CHAR_SETS["Binary / CMatrix"])

    if effect_name == "Invert Colors":
        frame = cv2.bitwise_not(frame)
    elif effect_name == "Edge Detect (Neon)":
        edges = cv2.Canny(frame, 100, 200)
        frame = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    elif effect_name == "Glitch Noise":
        noise = np.random.randint(0, 50, frame.shape, dtype='uint8')
        frame = cv2.add(frame, noise)

    # Ensure minimum viewport bounds
    vw = max(viewport_w, 320)
    vh = max(viewport_h, 240)

    # Grid dimensions based on density setting
    cols = density_cols
    cell_w = max(1.0, vw / cols)
    
    # Text ratio compensation (typically standard monospace font height is ~1.8x width)
    cell_h = max(1.0, cell_w * 1.8)
    rows = max(1, int(vh / cell_h))

    # Resize input frame to exact ASCII grid matrix size
    small_frame = cv2.resize(frame, (cols, rows), interpolation=cv2.INTER_AREA)
    gray_enhanced = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)

    # Calculate optimal font point size dynamically
    font_size = max(6, int(cell_h * 0.75))
    try:
        font = ImageFont.truetype("cour.ttf", font_size)
    except OSError:
        font = ImageFont.load_default()

    img_ascii = Image.new("RGB", (vw, vh), color=(10, 10, 12))
    draw = ImageDraw.Draw(img_ascii)

    num_chars = len(ascii_chars)
    is_original = (color_mode == "ORIGINAL")

    for y in range(rows):
        for x in range(cols):
            brightness = gray_enhanced[y, x]
            char_idx = int((brightness / 256) * num_chars)
            char = ascii_chars[min(char_idx, num_chars - 1)]

            if is_original:
                b, g, r = small_frame[y, x]
                fill_color = (r, g, b)
            else:
                fill_color = color_mode

            pos_x = int(x * cell_w)
            pos_y = int(y * cell_h)
            draw.text((pos_x, pos_y), char, fill=fill_color, font=font)

    return img_ascii


class StreamWorker(QThread):
    frame_processed = pyqtSignal(QImage)

    def __init__(self, app_inst):
        super().__init__()
        self.app = app_inst
        self.running = False

    def run(self):
        self.running = True
        while self.running and self.app.cap and self.app.cap.isOpened():
            ret, frame = self.app.cap.read()
            if not ret:
                break

            vw = self.app.viewport.width()
            vh = self.app.viewport.height()

            density, char_set, color_mode, effect = self.app.get_render_settings()
            pil_img = process_ascii_frame(frame, vw, vh, density, char_set, color_mode, effect)

            data = pil_img.tobytes("raw", "RGB")
            qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGB888)
            self.frame_processed.emit(qimg)

            self.msleep(33)

    def stop(self):
        self.running = False
        self.wait()


class VideoViewport(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.pixmap = None
        self.zoom_factor = 1.0
        self.setStyleSheet("background-color: #0A0A0C;")

    def update_pixmap(self, qimage):
        self.pixmap = QPixmap.fromImage(qimage)
        self.update()

    def set_zoom(self, zoom_val):
        self.zoom_factor = max(0.2, min(zoom_val, 5.0))
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.zoom_factor = min(self.zoom_factor + 0.1, 5.0)
        else:
            self.zoom_factor = max(self.zoom_factor - 0.1, 0.2)
            
        self.main_window.spin_zoom.setValue(self.zoom_factor)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        if self.pixmap and not self.pixmap.isNull():
            vw, vh = self.width(), self.height()
            target_w = vw * self.zoom_factor
            target_h = vh * self.zoom_factor
            
            x = (vw - target_w) / 2.0
            y = (vh - target_h) / 2.0

            target_rect = QRectF(x, y, target_w, target_h)
            painter.drawPixmap(target_rect, self.pixmap, QRectF(self.pixmap.rect()))
        else:
            painter.setPen(QColor("#00FFAA"))
            painter.setFont(QFont("Arial", 16))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Select an input source to begin")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aasishi - ASCII Video & Image Studio")
        self.resize(1280, 720)

        self.cap = None
        self.worker = None
        self.current_frame = None
        self.current_mode = None

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        top_layout = QVBoxLayout(central_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        # Header Bar
        top_bar = QFrame()
        top_bar.setStyleSheet("background-color: #121215; border-bottom: 1px solid #24242A;")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(10, 5, 10, 5)

        self.btn_toggle_sidebar = QPushButton("◄ Aasishi Panel")
        self.btn_toggle_sidebar.setStyleSheet(
            "background-color: #00FFAA; color: #000; border: none; padding: 6px 14px; font-weight: bold; border-radius: 4px;"
        )
        self.btn_toggle_sidebar.clicked.connect(self.toggle_sidebar)
        top_bar_layout.addWidget(self.btn_toggle_sidebar)

        lbl_app_title = QLabel("Aasishi ASCII Studio")
        lbl_app_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00FFAA;")
        top_bar_layout.addWidget(lbl_app_title)
        top_bar_layout.addStretch()

        top_layout.addWidget(top_bar)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        top_layout.addWidget(self.splitter)

        # Left Controls Sidebar
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(240)
        self.sidebar.setStyleSheet("background-color: #16161A; color: white;")
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(10)

        # Density Control
        sidebar_layout.addWidget(QLabel("Density / Detail:"))
        density_box = QHBoxLayout()
        self.slider_density = QSlider(Qt.Orientation.Horizontal)
        self.slider_density.setRange(40, 300)
        self.slider_density.setValue(140)

        self.spin_density = QSpinBox()
        self.spin_density.setRange(40, 300)
        self.spin_density.setValue(140)
        self.spin_density.setStyleSheet("background-color: #24242A; color: white; padding: 2px;")

        self.slider_density.valueChanged.connect(self.spin_density.setValue)
        self.spin_density.valueChanged.connect(self.slider_density.setValue)
        self.slider_density.valueChanged.connect(self.on_setting_changed)

        density_box.addWidget(self.slider_density)
        density_box.addWidget(self.spin_density)
        sidebar_layout.addLayout(density_box)

        # Zoom Control
        sidebar_layout.addWidget(QLabel("Zoom View:"))
        zoom_box = QHBoxLayout()
        btn_zoom_out = QPushButton("-")
        btn_zoom_out.setStyleSheet("background-color: #24242A; font-weight: bold; padding: 4px;")
        btn_zoom_out.clicked.connect(lambda: self.adjust_zoom(-0.1))

        self.spin_zoom = QDoubleSpinBox()
        self.spin_zoom.setRange(0.2, 5.0)
        self.spin_zoom.setSingleStep(0.1)
        self.spin_zoom.setValue(1.0)
        self.spin_zoom.setStyleSheet("background-color: #24242A; color: white; padding: 2px;")
        self.spin_zoom.valueChanged.connect(self.on_zoom_changed)

        btn_zoom_in = QPushButton("+")
        btn_zoom_in.setStyleSheet("background-color: #24242A; font-weight: bold; padding: 4px;")
        btn_zoom_in.clicked.connect(lambda: self.adjust_zoom(0.1))

        zoom_box.addWidget(btn_zoom_out)
        zoom_box.addWidget(self.spin_zoom)
        zoom_box.addWidget(btn_zoom_in)
        sidebar_layout.addLayout(zoom_box)

        # Character Style
        sidebar_layout.addWidget(QLabel("Character Style:"))
        self.combo_palette = QComboBox()
        self.combo_palette.addItems(list(CHAR_SETS.keys()))
        self.combo_palette.setStyleSheet("background-color: #24242A; color: white; padding: 4px;")
        self.combo_palette.currentTextChanged.connect(self.on_setting_changed)
        sidebar_layout.addWidget(self.combo_palette)

        # Text Color (With Original Option)
        sidebar_layout.addWidget(QLabel("Text Color:"))
        self.combo_color = QComboBox()
        self.combo_color.addItems(list(COLOR_SCHEMES.keys()))
        self.combo_color.setStyleSheet("background-color: #24242A; color: white; padding: 4px;")
        self.combo_color.currentTextChanged.connect(self.on_setting_changed)
        sidebar_layout.addWidget(self.combo_color)

        # Effects
        sidebar_layout.addWidget(QLabel("Cool Effects:"))
        self.combo_effect = QComboBox()
        self.combo_effect.addItems(["None", "Invert Colors", "Edge Detect (Neon)", "Glitch Noise"])
        self.combo_effect.setStyleSheet("background-color: #24242A; color: white; padding: 4px;")
        self.combo_effect.currentTextChanged.connect(self.on_setting_changed)
        sidebar_layout.addWidget(self.combo_effect)

        # Actions
        sidebar_layout.addSpacing(10)
        btn_webcam = QPushButton("📹 Live Webcam")
        btn_webcam.setStyleSheet("background-color: #1F538D; padding: 8px; border-radius: 4px;")
        btn_webcam.clicked.connect(self.start_webcam)
        sidebar_layout.addWidget(btn_webcam)

        btn_photo = QPushButton("🖼️ Open Photo")
        btn_photo.setStyleSheet("background-color: #1F538D; padding: 8px; border-radius: 4px;")
        btn_photo.clicked.connect(self.load_photo)
        sidebar_layout.addWidget(btn_photo)

        btn_video = QPushButton("🎥 Open Video")
        btn_video.setStyleSheet("background-color: #1F538D; padding: 8px; border-radius: 4px;")
        btn_video.clicked.connect(self.load_video)
        sidebar_layout.addWidget(btn_video)

        btn_stop = QPushButton("⏹️ Stop Feed")
        btn_stop.setStyleSheet("background-color: #8D1F1F; padding: 8px; border-radius: 4px;")
        btn_stop.clicked.connect(self.stop_feed)
        sidebar_layout.addWidget(btn_stop)

        sidebar_layout.addStretch()

        self.viewport = VideoViewport(self)

        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.viewport)
        self.splitter.setSizes([240, 1040])

    def toggle_sidebar(self):
        sizes = self.splitter.sizes()
        if sizes[0] > 0:
            self.saved_sidebar_size = sizes[0]
            self.splitter.setSizes([0, sizes[0] + sizes[1]])
            self.btn_toggle_sidebar.setText("► Aasishi Panel")
        else:
            restore_w = getattr(self, 'saved_sidebar_size', 240)
            self.splitter.setSizes([restore_w, 1040])
            self.btn_toggle_sidebar.setText("◄ Aasishi Panel")

    def adjust_zoom(self, step):
        new_zoom = round(self.spin_zoom.value() + step, 1)
        self.spin_zoom.setValue(new_zoom)

    def on_zoom_changed(self, val):
        self.viewport.set_zoom(val)

    def get_render_settings(self):
        density = self.spin_density.value()
        char_set = self.combo_palette.currentText()
        color_name = self.combo_color.currentText()
        color_mode = COLOR_SCHEMES.get(color_name, (50, 205, 50))
        effect = self.combo_effect.currentText()
        return density, char_set, color_mode, effect

    def on_setting_changed(self):
        if self.current_mode == "photo" and self.current_frame is not None:
            vw = self.viewport.width()
            vh = self.viewport.height()
            density, char_set, color_mode, effect = self.get_render_settings()
            pil_img = process_ascii_frame(self.current_frame, vw, vh, density, char_set, color_mode, effect)
            data = pil_img.tobytes("raw", "RGB")
            qimg = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGB888)
            self.viewport.update_pixmap(qimg)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.on_setting_changed()

    def stop_feed(self):
        if self.worker:
            self.worker.stop()
            self.worker = None
        if self.cap and self.cap.isOpened():
            self.cap.release()

        self.player.stop()
        self.current_mode = None
        self.viewport.pixmap = None
        self.viewport.update()

    def start_webcam(self):
        self.stop_feed()
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "Could not access webcam.")
            return

        self.current_mode = "webcam"
        self.worker = StreamWorker(self)
        self.worker.frame_processed.connect(self.viewport.update_pixmap)
        self.worker.start()

    def load_photo(self):
        self.stop_feed()
        file_dialog = QFileDialog(self, "Select Photo")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Image Files (*.png *.jpg *.jpeg *.bmp *.webp)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                frame = cv2.imread(file_path)
                if frame is not None:
                    self.current_mode = "photo"
                    self.current_frame = frame
                    self.on_setting_changed()

    def load_video(self):
        self.stop_feed()
        file_dialog = QFileDialog(self, "Select Video File")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("Video Files (*.mp4 *.avi *.mov *.mkv)")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]

                self.cap = cv2.VideoCapture(file_path)
                if not self.cap.isOpened():
                    QMessageBox.critical(self, "Error", "Could not open video file.")
                    return

                self.player.setSource(QUrl.fromLocalFile(file_path))
                self.player.play()

                self.current_mode = "video"
                self.worker = StreamWorker(self)
                self.worker.frame_processed.connect(self.viewport.update_pixmap)
                self.worker.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
