# backup_manager.py
import os
import shutil
import zipfile
import datetime


class MuseumBackupManager:
    def __init__(self, db_path='db/museum.db', backup_dir='db_backups', max_backups=5):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.max_backups = max_backups
        self.log_history = []

    def ensure_directories(self):
        """Проверка существования необходимых папок для работы модуля"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            self.log_history.append(f"Создана директория для резервных копий: {self.backup_dir}")

    def create_database_backup(self):
        """Создание сжатого zip-архива текущей базы данных SQLite"""
        self.ensure_directories()
        
        if not os.path.exists(self.db_path):
            msg = f"Ошибка резервного копирования: файл базы данных '{self.db_path}' не найден."
            self.log_history.append(msg)
            return False, msg

        # Формируем имя файла на основе текущей даты и времени
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"museum_backup_{timestamp}.zip"
        backup_full_path = os.path.join(self.backup_dir, backup_filename)

        try:
            # Записываем файл БД внутрь защищенного архива
            with zipfile.ZipFile(backup_full_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                zip_file.write(self.db_path, os.path.basename(self.db_path))
                
            success_msg = f"Резервная копия успешно создана: {backup_full_path}"
            self.log_history.append(success_msg)
            
            # После успешного создания чистим старые бэкапы
            self.rotate_old_backups()
            return True, success_msg
            
        except Exception as e:
            error_msg = f"Произошел системный сбой при архивации: {str(e)}"
            self.log_history.append(error_msg)
            return False, error_msg

    def rotate_old_backups(self):
        """Удаление наиболее старых резервных копий, если превышен лимит max_backups"""
        all_backups = []
        for filename in os.listdir(self.backup_dir):
            if filename.startswith("museum_backup_") and filename.endswith(".zip"):
                full_path = os.path.join(self.backup_dir, filename)
                all_backups.append(full_path)

        # Сортируем файлы по времени их изменения (от старых к новым)
        all_backups.sort(key=os.path.getmtime)

        # Если копий больше, чем разрешено — удаляем излишки
        while len(all_backups) > self.max_backups:
            oldest_backup = all_backups.pop(0)
            try:
                os.remove(oldest_backup)
                self.log_history.append(f"Удалена устаревшая копия базы данных: {oldest_backup}")
            except Exception as e:
                self.log_history.append(f"Не удалось удалить файл {oldest_backup}: {e}")

    def get_backup_report(self):
        """Возвращает структурированный текстовый лог работы менеджера"""
        report = [
            "=== ОТЧЕТ МЕНЕДЖЕРА РЕЗЕРВНОГО КОПИРОВАНИЯ ===",
            f"Целевой файл БД: {self.db_path}",
            f"Максимальное количество копий хранения: {self.max_backups}",
            "История последних операций:"
        ]
        for event in self.log_history:
            report.append(f" - {event}")
        return "\n".join(report)


def execute_scheduled_backup():
    """Точка запуска скрипта бэкапа в автономном режиме"""
    print("Инициализация резервного копирования...")
    manager = MuseumBackupManager()
    status, message = manager.create_database_backup()
    print(f"Статус: {'Успех' if status else 'Ошибка'}")
    print(f"Детали: {message}")


if __name__ == '__main__':
    execute_scheduled_backup()