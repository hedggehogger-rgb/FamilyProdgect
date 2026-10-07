import os
import time
from pathlib import Path

OUTPUT_FILE = "project_dump.txt"

# Папки, которые полностью исключаются (добавлены кэши Gradle, Android, Maven и JVM)
IGNORE_DIRS = {
    # Git & IDE
    ".git", ".idea", ".vscode",
    # Python & JS (на случай смешанных проектов)
    ".venv", "venv", "env", "__pycache__", "node_modules", "dist",
    # Kotlin / Java / Gradle / Android
    ".gradle", "gradle", "build", "out", "target",
    ".cxx", "captures", ".externalNativeBuild",
    # Тесты и покрытие (по аналогии с вашей исходной версией)
    "tests", "test", "coverage", ".pytest_cache"
}

# Файлы, которые исключаются из сборки
IGNORE_FILES = {
    # Конфиги и секреты
    ".env", ".env.example", "local.properties",  # local.properties содержит локальные пути к SDK/секреты
    # Скрипты и дампы
    OUTPUT_FILE, "bundle.py", "project_dump.txt", "project_code_dump.txt",
    # Локи и бинарные обертки Gradle (при необходимости gradlew можно убрать из игнора)
    "gradlew", "gradlew.bat", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"
}

# Расширения файлов (добавлены скомпилированные классы, архивы и бинарники JVM/Android)
IGNORE_EXTENSIONS = {
    # Базы данных и медиа
    ".db", ".sqlite", ".sqlite3",
    ".png", ".jpg", ".jpeg", ".svg", ".ico", ".webp",
    ".woff", ".woff2", ".ttf", ".eot", ".map", ".log", ".xlsx", ".pdf",
    # Python
    ".pyc", ".pyo", ".pyd",
    # JVM / Kotlin / Android артефакты
    ".class",       # Байткод
    ".jar", ".aar", # Скомпилированные библиотеки
    ".apk", ".aab", # Сборки Android
    ".dex",         # Исполняемый байткод Dalvik/ART
    ".klib",        # Библиотеки Kotlin Multiplatform
    ".keystore", ".jks", # Ключи подписи
    ".hprof",       # Дампы памяти
    ".so", ".dylib", ".dll" # Нативные библиотеки
}

def should_ignore(path: Path) -> bool:
    if path.name in IGNORE_FILES:
        return True
    if path.is_dir() and path.name in IGNORE_DIRS:
        return True
    if path.is_file() and path.suffix.lower() in IGNORE_EXTENSIONS:
        return True
    return False

def build_tree(dir_path: Path, prefix: str = "") -> list[str]:
    lines = []
    try:
        entries = sorted(
            [e for e in dir_path.iterdir() if not should_ignore(e)],
            key=lambda x: (not x.is_dir(), x.name.lower()),
        )
    except PermissionError:
        return lines

    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{entry.name}{'/' if entry.is_dir() else ''}")

        if entry.is_dir():
            sub_prefix = prefix + ("    " if is_last else "│   ")
            lines.extend(build_tree(entry, sub_prefix))
    return lines

def collect_files(root_dir: Path) -> list[Path]:
    file_paths = []
    for root, dirs, files in os.walk(root_dir):
        # Модифицируем dirs in-place, чтобы os.walk не заходил в игнорируемые папки
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for f in files:
            p = Path(root) / f
            if not should_ignore(p):
                file_paths.append(p)
    return sorted(file_paths, key=lambda x: str(x).lower())

def main():
    root = Path(__file__).resolve().parent
    print(f"🔍 Сканирование проекта: {root.name} ...")

    tree_lines = [f"{root.name}/"] + build_tree(root)
    files = collect_files(root)

    total_lines_of_code = 0
    file_stats = []

    for f in files:
        try:
            with open(f, "r", encoding="utf-8", errors="replace") as file_obj:
                count = sum(1 for _ in file_obj)
                total_lines_of_code += count
                rel_path = f.relative_to(root).as_posix()
                status = "OK" if count <= 300 else "ТРЕБУЕТСЯ РАСПИЛ (> 300)"
                file_stats.append((rel_path, count, status))
        except Exception:
            pass

    out_path = root / OUTPUT_FILE
    with open(out_path, "w", encoding="utf-8") as out:
        out.write("=" * 80 + f"\n ПОЛНЫЙ ДАМП ПРОЕКТА: {root.name}\n Дата: {time.strftime('%Y-%m-%d %H:%M:%S')}\n Всего файлов: {len(files)}\n Всего строк: {total_lines_of_code}\n" + "=" * 80 + "\n\n")
        out.write("=" * 80 + "\n КАРТА ПРОЕКТА (TREE)\n" + "=" * 80 + "\n" + "\n".join(tree_lines) + "\n\n")
        out.write("=" * 80 + "\n АУДИТ ФАЙЛОВ НА 300 СТРОК\n" + "=" * 80 + "\n")
        for path_str, line_count, status in file_stats:
            flag = "[!]" if "РАСПИЛ" in status else "   "
            out.write(f"{flag} {path_str:<50} : {line_count:>4} строк [{status}]\n")
        out.write("\n" + "=" * 80 + "\n ИСХОДНЫЙ КОД ВСЕХ ФАЙЛОВ\n" + "=" * 80 + "\n\n")

        for f in files:
            rel_path = f.relative_to(root).as_posix()
            out.write("=" * 80 + f"\n START OF FILE: {rel_path}\n" + "=" * 80 + "\n")
            try:
                with open(f, "r", encoding="utf-8", errors="replace") as content_file:
                    out.write(content_file.read())
            except Exception as e:
                out.write(f"\n[ОШИБКА ЧТЕНИЯ: {e}]\n")
            # Заменили Python-специфичный '#' на нейтральный разделитель
            out.write(f"\n\n--- END OF FILE: {rel_path} ---\n\n\n")

    print(f"✓ Готово! Дамп {OUTPUT_FILE} (Файлов: {len(files)}, Строк: {total_lines_of_code})")

if __name__ == "__main__":
    main()