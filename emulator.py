import os
import tarfile
import argparse
import time
import datetime


class ShellEmulator:
    def __init__(self, username, hostname, vfs, script):
        self.username = username
        self.hostname = hostname
        self.start_time = time.time()
        self.vfs_archive = tarfile.open(vfs, "r")
        self.cwd = "/"

        if script:
            self.run_script(script)

    def run_script(self, script_path):
        with open(script_path, 'r') as script:
            for line in script:
                self.execute_command(line.strip())

    def execute_command(self, command):
        if not command:
            return

        parts = command.split()
        cmd = parts[0]
        args = parts[1:]

        if cmd == "ls":
            self.ls(args)
        elif cmd == "cd":
            self.cd(args)
        elif cmd == "exit":
            self.exit_shell()
        elif cmd == "uname":
            self.uname(args)
        elif cmd == "uptime":
            self.uptime(args)
        else:
            print(f"{cmd}: command not found")

    def prompt(self):
        if self.cwd == "/":
            return f"{self.username}@{self.hostname}:{self.cwd}$ "
        else:
            return f"{self.username}@{self.hostname}:{self.cwd.rstrip('/')}$ "

    def ls(self, args):
        if not args:
            path = self.cwd
        else:
            target = args[0]
            if target == "..":
                path = os.path.dirname(self.cwd.rstrip("/"))
                if not path:
                    path = "/"
            else:
                path = os.path.join(self.cwd, target)

        path = path.lstrip('/')
        entries = [m for m in self.vfs_archive.getmembers() if m.name.startswith(path)]
        if not entries:
            return

        unique_entries = set()
        for entry in entries:
            relative_path = entry.name[len(path):].strip("/").split("/")[0]
            if relative_path:
                unique_entries.add(relative_path)
        if not unique_entries:
            return

        for entry_name in sorted(unique_entries):
            print(entry_name)

    def cd(self, args):
        if not args or args[0] == "/":
            self.cwd = "/"
            return

        target = args[0]
        if target == "..":
            if self.cwd == "/":
                return
            else:
                self.cwd = os.path.dirname(self.cwd.rstrip("/"))
                if not self.cwd:
                    self.cwd = "/"
                return
        elif target == ".":
            return

        new_dir = os.path.join(self.cwd, target).replace("\\", "/")
        new_dir = os.path.normpath(new_dir).replace("\\", "/")
        potential_dirs = [m.name for m in self.vfs_archive.getmembers() if m.isdir()]
        abs_new_dir = new_dir.lstrip("/")

        for dir_entry in potential_dirs:
            if dir_entry.strip("/") == abs_new_dir:
                self.cwd = "/" + abs_new_dir + "/"
                return

        print(f"cd: {target}: No such file or directory")

    def exit_shell(self):
        print("Exiting shell...")
        exit(0)

    def uname(self, args):
        if args:
            if args[0] == "-a":
                print(f"Linux {self.hostname} 5.15.0-1-generic x86_64 GNU/Linux")
            else:
                print(f"uname: invalid option -- '{''.join(args)}'")
        else:
            print("Linux")

    def uptime(self, args):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        users = 1  # количество пользователей - в эмуляторе считаем 1
        uptime_seconds = time.time() - self.start_time
        if args:
            if "-p" in args:
                uptime_minutes = int(uptime_seconds // 60)
                print(f"up {uptime_minutes} minutes")
                return
            elif "-s" in args:
                start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.start_time))
                print(f"Startup time: {start_time}")
                return
            else:
                print(f"uptime: invalid option -- '{''.join(args)}'")
                return

        uptime_string = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
        print(f"{current_time} | up {uptime_string} | {users} user(s)")

    def run(self):
        try:
            while True:
                command = input(self.prompt())
                self.execute_command(command.strip())
        except KeyboardInterrupt:
            self.exit_shell()


def parse_args():
    parser = argparse.ArgumentParser(description="Эмулятор оболочки UNIX-подобной ОС.")
    parser.add_argument("username", nargs='?', help="Имя пользователя для приглашения к вводу.", default="username")
    parser.add_argument("hostname", nargs='?', help="Имя компьютера для приглашения к вводу.", default="hostname")
    parser.add_argument("vfs", nargs='?', help="Путь к tar-архиву виртуальной файловой системы.", default="tartar.tar")
    parser.add_argument("script", nargs='?', help="Путь к стартовому скрипту.", default=None)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    shell = ShellEmulator(args.username, args.hostname, args.vfs, args.script)
    shell.run()
