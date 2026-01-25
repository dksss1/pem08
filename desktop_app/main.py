import sys
import os
import asyncio
import base64
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTabWidget, QTextEdit, QPushButton, 
                             QLabel, QFileDialog, QLineEdit, QScrollArea, QMessageBox,
                             QProgressBar, QGroupBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QIcon
import qasync

# Добавляем корневую директорию в путь, чтобы видеть backend
# Это необходимо, если main.py запускается напрямую, но если через лаунчер в корне, это избыточно,
# однако для надежности оставим проверку.
if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if base_path not in sys.path:
        sys.path.append(base_path)

from backend.services.openai_service import openai_service
from backend.services.parser_service import parser_service

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Competitor Monitor MVP")
        self.resize(1000, 800)
        
        # Основной виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Вкладки
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Создаем вкладки
        self.create_text_tab()
        self.create_image_tab()
        self.create_url_tab()
        
        # Статус бар
        self.statusBar().showMessage("Готово")

    def create_text_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Ввод текста
        input_group = QGroupBox("Входной текст")
        input_layout = QVBoxLayout(input_group)
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Вставьте текст конкурента...")
        input_layout.addWidget(self.text_input)
        layout.addWidget(input_group)
        
        # Кнопка анализа
        self.text_analyze_btn = QPushButton("Анализ текста")
        self.text_analyze_btn.clicked.connect(self.on_analyze_text)
        layout.addWidget(self.text_analyze_btn)
        
        # Результат
        result_group = QGroupBox("Результат анализа")
        result_layout = QVBoxLayout(result_group)
        self.text_result = QTextEdit()
        self.text_result.setReadOnly(True)
        result_layout.addWidget(self.text_result)
        layout.addWidget(result_group)
        
        self.tabs.addTab(tab, "Анализ текста")

    def create_image_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Выбор файла
        file_layout = QHBoxLayout()
        self.image_path_label = QLineEdit()
        self.image_path_label.setReadOnly(True)
        browse_btn = QPushButton("Выбрать...")
        browse_btn.clicked.connect(self.browse_image)
        file_layout.addWidget(self.image_path_label)
        file_layout.addWidget(browse_btn)
        layout.addLayout(file_layout)
        
        # Превью
        self.image_preview = QLabel("Изображение не выбрано")
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setMinimumHeight(200)
        self.image_preview.setStyleSheet("border: 1px dashed gray;")
        layout.addWidget(self.image_preview)
        
        # Кнопка анализа
        self.image_analyze_btn = QPushButton("Анализ изображения")
        self.image_analyze_btn.clicked.connect(self.on_analyze_image)
        self.image_analyze_btn.setEnabled(False)
        layout.addWidget(self.image_analyze_btn)
        
        # Результат
        result_group = QGroupBox("Результат анализа")
        result_layout = QVBoxLayout(result_group)
        self.image_result = QTextEdit()
        self.image_result.setReadOnly(True)
        result_layout.addWidget(self.image_result)
        layout.addWidget(result_group)
        
        self.tabs.addTab(tab, "Анализ изображения")

    def create_url_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Ввод URL
        url_layout = QHBoxLayout()
        layout.addWidget(QLabel("URL конкурента:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)
        
        # Кнопка парсинга
        self.url_analyze_btn = QPushButton("Спарсить и проанализировать сайт")
        self.url_analyze_btn.clicked.connect(self.on_analyze_url)
        layout.addWidget(self.url_analyze_btn)
        
        # Прогресс
        self.url_progress = QProgressBar()
        self.url_progress.setVisible(False)
        layout.addWidget(self.url_progress)
        
        # Результат (скролл)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.url_result_layout = QVBoxLayout(scroll_content)
        
        self.url_result_text = QTextEdit()
        self.url_result_text.setReadOnly(True)
        self.url_result_layout.addWidget(self.url_result_text)
        
        self.url_screenshot_label = QLabel()
        self.url_screenshot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.url_result_layout.addWidget(self.url_screenshot_label)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        self.tabs.addTab(tab, "Парсинг сайта")

    @qasync.asyncSlot()
    async def on_analyze_text(self):
        text = self.text_input.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите текст для анализа")
            return
            
        self.text_analyze_btn.setEnabled(False)
        self.statusBar().showMessage("Анализ текста...")
        
        try:
            analysis = await openai_service.analyze_text(text)
            
            # Форматируем вывод
            output = f"РЕЗЮМЕ:\n{analysis.summary}\n\n"
            output += f"ОЦЕНКА ДИЗАЙНА: {analysis.design_score}/10\n\n"
            
            output += "СИЛЬНЫЕ СТОРОНЫ:\n" + "\n".join(f"- {x}" for x in analysis.strengths) + "\n\n"
            output += "СЛАБЫЕ СТОРОНЫ:\n" + "\n".join(f"- {x}" for x in analysis.weaknesses) + "\n\n"
            output += "УНИКАЛЬНЫЕ ПРЕДЛОЖЕНИЯ:\n" + "\n".join(f"- {x}" for x in analysis.unique_offers) + "\n\n"
            output += "РЕКОМЕНДАЦИИ:\n" + "\n".join(f"- {x}" for x in analysis.recommendations) + "\n\n"
            output += f"ПОТЕНЦИАЛ АНИМАЦИИ:\n{analysis.animation_potential}"
            
            self.text_result.setText(output)
            self.statusBar().showMessage("Анализ текста завершён")
            
        except Exception as e:
            msg = str(e)
            if "401" in msg or "User not found" in msg:
                QMessageBox.warning(self, "Ошибка авторизации", "LLM анализ недоступен: проверьте OPENROUTER_API_KEY в .env")
            else:
                QMessageBox.critical(self, "Ошибка", msg)
            self.statusBar().showMessage("Произошла ошибка")
        finally:
            self.text_analyze_btn.setEnabled(True)

    def browse_image(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Файлы изображений (*.png *.jpg *.jpeg *.bmp *.webp)")
        if fname:
            self.image_path_label.setText(fname)
            pixmap = QPixmap(fname)
            self.image_preview.setPixmap(pixmap.scaled(self.image_preview.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.image_analyze_btn.setEnabled(True)

    @qasync.asyncSlot()
    async def on_analyze_image(self):
        path = self.image_path_label.text()
        if not path:
            return
            
        self.image_analyze_btn.setEnabled(False)
        self.statusBar().showMessage("Анализ изображения...")
        
        try:
            with open(path, "rb") as image_file:
                content = image_file.read()
                image_base64 = base64.b64encode(content).decode('utf-8')
                # Определяем mime type по расширению (простое решение)
                ext = os.path.splitext(path)[1].lower()
                mime_type = "image/jpeg"
                if ext == ".png": mime_type = "image/png"
                elif ext == ".webp": mime_type = "image/webp"
                elif ext == ".gif": mime_type = "image/gif"
            
            analysis = await openai_service.analyze_image(image_base64, mime_type)
            
            # Форматируем вывод
            output = f"ОПИСАНИЕ:\n{analysis.description}\n\n"
            output += f"ОЦЕНКА ДИЗАЙНА: {analysis.design_score}/10\n\n"
            output += f"ВИЗУАЛЬНЫЙ СТИЛЬ:\n{analysis.visual_style_analysis}\n\n"
            
            output += "МАРКЕТИНГОВЫЕ ИНСАЙТЫ:\n" + "\n".join(f"- {x}" for x in analysis.marketing_insights) + "\n\n"
            output += "РЕКОМЕНДАЦИИ:\n" + "\n".join(f"- {x}" for x in analysis.recommendations) + "\n\n"
            output += f"ПОТЕНЦИАЛ АНИМАЦИИ:\n{analysis.animation_potential}"
            
            self.image_result.setText(output)
            self.statusBar().showMessage("Анализ изображения завершён")
            
        except Exception as e:
            msg = str(e)
            if "401" in msg or "User not found" in msg:
                QMessageBox.warning(self, "Ошибка авторизации", "LLM анализ недоступен: проверьте OPENROUTER_API_KEY в .env")
            else:
                QMessageBox.critical(self, "Ошибка", msg)
            self.statusBar().showMessage("Произошла ошибка")
        finally:
            self.image_analyze_btn.setEnabled(True)

    @qasync.asyncSlot()
    async def on_analyze_url(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Ошибка", "Введите URL сайта конкурента")
            return
            
        self.url_analyze_btn.setEnabled(False)
        self.url_progress.setVisible(True)
        self.url_progress.setRange(0, 0) # Infinite loading
        self.statusBar().showMessage("Парсинг сайта (это может занять время)...")
        self.url_result_text.clear()
        self.url_screenshot_label.clear()
        
        try:
            # 1. Parse URL
            title, h1, first_paragraph, screenshot_bytes, error = await parser_service.parse_url(url)
            
            if error:
                raise Exception(error)
                
            self.statusBar().showMessage("Анализ содержимого...")
            
            # Display screenshot if available
            screenshot_base64 = None
            if screenshot_bytes:
                pixmap = QPixmap()
                pixmap.loadFromData(screenshot_bytes)
                self.url_screenshot_label.setPixmap(pixmap.scaled(600, 400, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                screenshot_base64 = parser_service.screenshot_to_base64(screenshot_bytes)
            
            # 2. Analyze
            analysis = None
            try:
                if screenshot_base64:
                    analysis = await openai_service.analyze_website_screenshot(
                        screenshot_base64=screenshot_base64,
                        url=url,
                        title=title,
                        h1=h1,
                        first_paragraph=first_paragraph
                    )
                else:
                    analysis = await openai_service.analyze_parsed_content(
                        title=title,
                        h1=h1,
                        paragraph=first_paragraph
                    )
            except Exception as e:
                msg = str(e)
                if "401" in msg or "User not found" in msg:
                    QMessageBox.warning(self, "Ошибка авторизации", "LLM анализ недоступен: проверьте OPENROUTER_API_KEY в .env")
                else:
                    QMessageBox.critical(self, "Ошибка", msg)
                # Продолжаем без LLM-анализа, показываем только базовые данные парсинга
                analysis = None
                
            # Форматируем вывод
            output = f"ЗАГОЛОВОК (title): {title}\n"
            output += f"H1: {h1}\n"
            output += "-" * 30 + "\n"
            if analysis:
                output += f"РЕЗЮМЕ:\n{analysis.summary}\n\n"
                output += f"ОЦЕНКА ДИЗАЙНА: {analysis.design_score}/10\n\n"
                output += "СИЛЬНЫЕ СТОРОНЫ:\n" + "\n".join(f"- {x}" for x in analysis.strengths) + "\n\n"
                output += "СЛАБЫЕ СТОРОНЫ:\n" + "\n".join(f"- {x}" for x in analysis.weaknesses) + "\n\n"
                output += "УНИКАЛЬНЫЕ ПРЕДЛОЖЕНИЯ:\n" + "\n".join(f"- {x}" for x in analysis.unique_offers) + "\n\n"
                output += "РЕКОМЕНДАЦИИ:\n" + "\n".join(f"- {x}" for x in analysis.recommendations)
            else:
                output += "LLM-анализ недоступен. Проверьте API ключ в .env.\n"
            
            self.url_result_text.setText(output)
            self.statusBar().showMessage("Анализ сайта завершён")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            self.statusBar().showMessage("Произошла ошибка")
        finally:
            self.url_analyze_btn.setEnabled(True)
            self.url_progress.setVisible(False)

def run_app():
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    window = MainWindow()
    window.show()
    
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    run_app()
