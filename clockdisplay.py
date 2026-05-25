import sys
import threading
from typing import Callable, Optional
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QObject, QRect, QSize
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor, QFontDatabase, QImage

class WindowSignalContainer(QObject):
    change_text = pyqtSignal(str)
    trigger_close = pyqtSignal()

class BottomCenterOverlay(QMainWindow):
    def __init__(self, image_path: str, font_file_path: str, initial_text: str, 
                 text_x: int, text_y: int, font_size: int, font_color: str, 
                 fullscreen: bool, aspect_ratio_mode: Qt.AspectRatioMode):
        super().__init__()
        
        self.image_path = image_path
        self.text_x = text_x
        self.text_y = text_y
        self.font_size = font_size
        self.font_color = font_color
        self.fullscreen = fullscreen
        self.aspect_ratio_mode = aspect_ratio_mode
        self.current_text = initial_text
        
        # --- Internal Scaling State ---
        self._scaled_image_rect = QRect()
        self._scale_factor_x = 1.0
        self._scale_factor_y = 1.0
        
        # 1. Base window properties (Borderless, click-through background)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 2. Asset loading and validation
        self.source_pixmap = QPixmap(self.image_path)
        if self.source_pixmap.isNull():
            raise FileNotFoundError(f"Could not load image: {image_path}")

        font_id = QFontDatabase.addApplicationFont(font_file_path)
        if font_id == -1:
            raise FileNotFoundError(f"Could not load font: {font_file_path}")
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        self.font_family = font_families[0] if font_families else "Arial"

        # 3. Create display canvas
        self.label = QLabel(self)
        self.label.setScaledContents(False) # Handle scaling manually in paintEvent
        
        # 4. Connect signals
        self.signals = WindowSignalContainer()
        self.signals.change_text.connect(self._on_text_changed)
        self.signals.trigger_close.connect(self.close)

        # 5. Initialize Geometry
        self._update_geometry()
        
        # Trigger initial draw
        self.update()

    def _update_geometry(self):
        """Calculates window positioning and internal image scaling factors."""
        screen = QApplication.primaryScreen().geometry()
        img_size = self.source_pixmap.size()

        if self.fullscreen:
            # Window covers the entire screen
            self.setFixedSize(screen.width(), screen.height())
            self.move(0, 0)
            target_rect = screen
        else:
            # Locked window size to image aspect ratio (or simple stretch) at bottom-center
            # For simplicity in non-fullscreen, we align the window itself at bottom center.
            if self.aspect_ratio_mode == Qt.AspectRatioMode.IgnoreAspectRatio:
                 # In "stretch" mode but not fullscreen, we assume it still takes native size for bottom alignment
                 self.setFixedSize(img_size)
            else:
                 # (Keep aspect ratio modes for window size if needed - here we simplify to native size)
                 self.setFixedSize(img_size)
            
            self.position_at_bottom_center()
            target_rect = self.rect()

        # --- Calculate Scaling Target and Factors ---
        
        # Determine the rect of the scaled image within the window canvas
        scaled_size = img_size.scaled(target_rect.size(), self.aspect_ratio_mode)
        
        # Center the scaled rect within the window
        self._scaled_image_rect = QRect(
            target_rect.x() + (target_rect.width() - scaled_size.width()) // 2,
            target_rect.y() + (target_rect.height() - scaled_size.height()) // 2,
            scaled_size.width(),
            scaled_size.height()
        )
        
        # Store scale factors for mapping text coordinates
        # Map original asset X/Y to the scaled asset X/Y
        self._scale_factor_x = scaled_size.width() / img_size.width()
        self._scale_factor_y = scaled_size.height() / img_size.height()

    def _on_text_changed(self, text: str):
        """Signal handler for real-time text updates."""
        self.current_text = text
        self.update() # Force repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # --- FIX: Force clean alpha clearing ---
        # Using Source mode tells Qt to completely overwrite pixels with our transparent brush,
        # rather than attempting to blend transparent color over an existing RGB buffer.
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
        painter.eraseRect(self.rect())
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
        
        # Switch back to SourceOver so the PNG alpha layers blend properly onto the window
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        
        # Draw the banner image (respecting its native PNG alpha channels)
        #painter.setOpacity(self.image_opacity)
        painter.drawPixmap(self._scaled_image_rect, self.source_pixmap)
        
        # Reset opacity back to 1.0 for completely crisp text
        painter.setOpacity(1.0)
        
        # Draw text overlay
        font = QFont(self.font_family, self.font_size)
        painter.setFont(font)
        painter.setPen(QColor(self.font_color))
        
        mapped_x = self._scaled_image_rect.x() + int(self.text_x * self._scale_factor_x)
        mapped_y = self._scaled_image_rect.y() + int(self.text_y * self._scale_factor_y)
        
        painter.drawText(QPoint(mapped_x, mapped_y), self.current_text)
        painter.end()

    def resizeEvent(self, event):
        """Handle screen resolution changes or window state changes."""
        self._update_geometry()
        self.update()
        super().resizeEvent(event)

    def position_at_bottom_center(self):
        """Fallback for non-fullscreen mode, aligned at bottom-center."""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() - self.height()
        self.move(x, y)


class OverlayEngine:
    # --- Exposure of standard Qt scaling modes for convenience ---
    STRETCH_TO_FILL = Qt.AspectRatioMode.IgnoreAspectRatio # Distorts to fill entire window
    KEEP_ASPECT_RATIO = Qt.AspectRatioMode.KeepAspectRatio  # Letterbox/Pillarbox (No distortion)
    FILL_AND_CROP = Qt.AspectRatioMode.KeepAspectRatioByExpanding # Zooms to fill entire window (Crops edges, no distortion)

    def __init__(self, image_path: str, font_file_path: str, initial_text: str = "", 
                 text_x: int = 10, text_y: int = 30, font_size: int = 24, font_color: str = "white", 
                 fullscreen: bool = False, aspect_ratio_mode: Qt.AspectRatioMode = KEEP_ASPECT_RATIO, params: dict = {}):
        
        # Normalize the main thread warning safety
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.params = params
        self.overlay = BottomCenterOverlay(image_path, font_file_path, initial_text, 
                                          text_x, text_y, font_size, font_color, 
                                          fullscreen, aspect_ratio_mode)
        self._done_event = threading.Event()
        
    def update_text(self, new_text: str):
        if self.overlay:
            self.overlay.signals.change_text.emit(str(new_text))

    def close(self):
        if self.overlay:
            self.overlay.signals.trigger_close.emit()
        self._done_event.set()

    def launch(self, target_logic_function: Callable[['OverlayEngine'], None]):
        """Runs your UI logic sequence non-blockingly on the main thread."""
        self.overlay.show()
        
        worker_thread = threading.Thread(target=target_logic_function, args=(self,), daemon=True)
        worker_thread.start()
        
        while not self._done_event.is_set():
            self.app.processEvents()
            threading.Event().wait(0.01)