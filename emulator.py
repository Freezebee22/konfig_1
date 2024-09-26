import os
import tarfile
import time
import sys
import argparse

class ShellEmulator:
    def __init__(self, username, hostname, vfs_path, start_script):
        self.username = username
        self.hostname = hostname
        self.cwd = "/"
        self.vfs = {}
        self.load_vfs(vfs_path)
        self.start_script = start_script
        self.start_time = time.time()

    def load_vfs(self, vfs_path):
        """Загрузка виртуальной файловой системы из архива tar."""
        with tarfile.open(vfs_path, 'r') as tar:
            for member in tar.getmembers():
                self.vfs[member.name] = member
        print(f"Файловая система загружена из {vfs_path}")

    def prompt(self):
        """Возвращает строку приглашения для ввода."""
        return f"{self.username}@{self.hostname}:{self.cwd}$ "

    def run(self):
        """Запуск эмулятора оболочки."""
        if self.start_script:
            self.run_script(self.start_script)

        while True:
            try:
                command = input(self.prompt()).strip()
                if command:
                    self.execute_command(command)
            except (EOFError, KeyboardInterrupt):
                print("\nВыход из эмулятора.")
                break

    def execute_command(self, command):
        parts = command.split()
        if not parts:
            return
        cmd = parts[0]
        args = parts[1:]

        if cmd == "ls":
            self.ls()
        elif cmd == "cd":
            self.cd(args)
        elif cmd == "exit":
            sys.exit(0)
        elif cmd == "uname":
            self.uname()
        elif cmd == "uptime":
            self.uptime()
        else:
            print(f"Команда '{cmd}' не найдена.")

    def ls(self):
        if self.cwd == "/":
            path = ""
        else:
            path = self.cwd.strip("/")

        found_items = []
        for member in self.vfs:
            member_path = member.strip("/")
            if member_path.startswith(path) and len(member_path.split("/")) == len(path.split("/")) + 1:
                found_items.append(os.path.basename(member_path))

        if found_items:
            for item in sorted(found_items):
                print(item)
        else:
            print("Ошибка: каталог не найден")

    def cd(self, args):
        if len(args) != 1:
            print("Ошибка: команда cd требует одного аргумента")
            return

        new_dir = args[0]

        if new_dir == "..":
            if self.cwd != "/":
                self.cwd = os.path.dirname(self.cwd.rstrip("/"))
                if not self.cwd:
                    self.cwd = "/"
            return

        if new_dir.startswith("/"):
            target_path = new_dir.rstrip("/")
        else:
            target_path = os.path.join(self.cwd, new_dir).rstrip("/")

        target_path_vfs = target_path.strip("/")

        if target_path_vfs in self.vfs:
            self.cwd = "/" + target_path_vfs
        else:
            print("Ошибка: каталог не найден или не является директорией")

    def uname(self):
        print("Unix-like shell emulator")

    def uptime(self):
        uptime_seconds = time.time() - self.start_time
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"Время работы: {int(hours)} часов, {int(minutes)} минут, {int(seconds)} секунд")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Эмулятор командной оболочки")
    parser.add_argument("--username", required=True, help="Имя пользователя")
    parser.add_argument("--hostname", required=True, help="Имя компьютера")
    parser.add_argument("--vfs", required=True, help="Путь к виртуальной файловой системе (tar архив)")
    parser.add_argument("--script", required=False, help="Путь к стартовому скрипту", default=None)

    args = parser.parse_args()

    shell = ShellEmulator(args.username, args.hostname, args.vfs, args.script)
    shell.run()
