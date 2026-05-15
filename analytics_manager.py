import os
import re
import datetime


class MuseumAnalytics:
    def __init__(self, log_filename='museum_system.log'):
        self.log_filename = log_filename
        self.total_requests = 0
        self.error_count = 0
        self.page_views = {}
        self.hourly_activity = {"Ночь (0-6)": 0, "Утро (6-12)": 0, "День (12-18)": 0, "Вечер (18-24)": 0}
        self.suspicious_requests = 0

    def analyze_logs(self):
        """Парсинг файла логов сервера с автоматическим определением кодировки Windows/Linux"""
        if not os.path.exists(self.log_filename):
            return "Файл логов еще не создан сервером."

        self.total_requests = 0
        self.error_count = 0
        self.suspicious_requests = 0
        self.page_views = {}
        for key in self.hourly_activity:
            self.hourly_activity[key] = 0

        view_pattern = re.compile(r"Посещение главной страницы|exhibit/\d+|showcase")
        error_pattern = re.compile(r"ERROR|CRITICAL|Страница не найдена")
        time_pattern = re.compile(r"(\d{4}-\d{2}-\d{2}) (\d{2}):\d{2}:\d{2}")
        hack_pattern = re.compile(r"wp-admin|config|eval|select|union|\.env", re.IGNORECASE)

        # Пробуем открыть файл в utf-8, если падает с UnicodeDecodeError — переключаемся на cp1251
        try:
            with open(self.log_filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(self.log_filename, 'r', encoding='cp1251') as f:
                lines = f.readlines()

        for line in lines:
            self.total_requests += 1
            
            if error_pattern.search(line):
                self.error_count += 1
            
            if hack_pattern.search(line):
                self.suspicious_requests += 1

            # Анализ временных диапазонов активности
            time_match = time_pattern.search(line)
            if time_match:
                hour = int(time_match.group(2))
                if 0 <= hour < 6:
                    self.hourly_activity["Ночь (0-6)"] += 1
                elif 6 <= hour < 12:
                    self.hourly_activity["Утро (6-12)"] += 1
                elif 12 <= hour < 18:
                    self.hourly_activity["День (12-18)"] += 1
                else:
                    self.hourly_activity["Вечер (18-24)"] += 1
            
            # Поиск просмотренных разделов
            match = view_pattern.search(line)
            if match:
                page = match.group(0)
                if "exhibit" in page:
                    page = "Просмотр экспоната"
                elif "showcase" in page:
                    page = "Зал витрин"
                elif "главной" in page:
                    page = "Главная страница"
                    
                self.page_views[page] = self.page_views.get(page, 0) + 1

    def generate_text_report(self, output_filename='museum_report.txt'):
        """Формирование и запись подробного структурированного отчета"""
        self.analyze_logs()
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report_lines = [
            "==================================================",
            f" РАСШИРЕННЫЙ АНАЛИТИЧЕСКИЙ ОТЧЕТ СИСТЕМЫ МУЗЕЯ",
            f" Дата генерации: {now}",
            "==================================================",
            f"Всего обработано сырых лог-записей: {self.total_requests}",
            f"Обнаружено программных сбоев (ошибок): {self.error_count}",
            f"Выявлено подозрительных сетевых запросов: {self.suspicious_requests}",
            "--------------------------------------------------",
            "РАСПРЕДЕЛЕНИЕ ТРАФИКА ПО ВРЕМЕНИ СУТОК:"
        ]

        for period, count in self.hourly_activity.items():
            report_lines.append(f" - {period}: {count} событий")

        report_lines.append("--------------------------------------------------")
        report_lines.append("СТАТИСТИКА ПОПУЛЯРНОСТИ ВИРТУАЛЬНЫХ ЗАЛОВ:")

        if self.page_views:
            for page, count in self.page_views.items():
                report_lines.append(f" - {page}: {count} раз(а)")
        else:
            report_lines.append(" - Посещения интерактивных зон пока не зафиксированы.")

        report_lines.extend([
            "--------------------------------------------------",
            "РЕКОМЕНДАЦИИ ДЛЯ СИСТЕМНОГО АДМИНИСТРАТОРА:",
            " 1. При росте подозрительных запросов обновите фильтрацию роутов.",
            " 2. Пиковые часы требуют стабильного интернет-соединения хоста.",
            "=================================================="
        ])

        try:
            with open(output_filename, 'w', encoding='utf-8') as rep_file:
                rep_file.write("\n".join(report_lines))
            return f"Отчет успешно сформирован и сохранен в: {output_filename}"
        except Exception as e:
            return f"Критическая ошибка сохранения файла отчета: {e}"


def run_standalone_analytics():
    """Интерфейсный запуск аналитики из консоли разработчика"""
    print("Инициализация автономного разбора файлов логирования...")
    analyzer = MuseumAnalytics()
    result = analyzer.generate_text_report()
    print(result)
    
    print("\n--- КРАТКАЯ СВОДКА СЕРВЕРА ---")
    print(f"Всего строк в логе: {analyzer.total_requests}")
    print(f"Ошибок бэкенда (404/500): {analyzer.error_count}")
    print(f"Атаки/Подозрительный трафик: {analyzer.suspicious_requests}")


if __name__ == '__main__':
    run_standalone_analytics()