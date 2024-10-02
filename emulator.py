import os
import tarfile
import argparse
import shutil
import time


class ShellEmulator:
    def __init__(self, username, hostname, vfs, startup_script):
        self.username = username
        self.hostname = hostname
        self.vfs_root = "/tmp/vfs_root"
        self.cwd = self.vfs_root
        self.start_time = time.time()

        self.extract_fs(vfs)

        if startup_script:
            self.run_script(startup_script)

    def extract_fs(self, archive_path):
        if os.path.exists(self.vfs_root):
            shutil.rmtree(self.vfs_root)
        os.makedirs(self.vfs_root)

        with tarfile.open(archive_path, "r") as tar:
            tar.extractall(self.vfs_root)

    def run_script(self, script_path):
        with open(script_path, 'r') as script:
            for line in script:
                self.execute_command(line.strip())

    def prompt(self):
        relative_path = os.path.relpath(self.cwd, self.vfs_root)

        if relative_path == ".":
            relative_path = "/"
        else:
            relative_path = "/" + relative_path.replace("\\", "/")

        return f"{self.username}@{self.hostname}:{relative_path}$ "

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
            self.uptime()
        else:
            print(f"{cmd}: command not found")

    def ls(self, args):
        path = self.cwd if not args else os.path.join(self.cwd, args[0])
        if os.path.exists(path):
            for entry in os.listdir(path):
                print(entry)
        else:
            print(f"ls: cannot access '{path}': No such file or directory")

    def cd(self, args):
        if not args:
            path = self.vfs_root
        else:
            path = os.path.join(self.cwd, args[0])

        real_path = os.path.abspath(path)

        if os.path.relpath(real_path, self.vfs_root).startswith(".."):
            print("cd: Permission denied")
        elif os.path.exists(real_path) and os.path.isdir(real_path):
            self.cwd = real_path
        else:
            print(f"cd: {real_path}: No such file or directory")

    def exit_shell(self):
        print("Exiting shell...")
        exit(0)

    def uname(self, args):
        if args and args[0] == "-a":
            print(f"Linux {self.hostname} 5.15.0-1-generic x86_64 GNU/Linux")
        else:
            print("Linux")

    def uptime(self):
        uptime_seconds = time.time() - self.start_time
        uptime_string = time.strftime("%H:%M:%S", time.gmtime(uptime_seconds))
        print(f"Uptime: {uptime_string}")

    def run(self):
        try:
            while True:
                command = input(self.prompt())
                self.execute_command(command.strip())
        except KeyboardInterrupt:
            self.exit_shell()


def parse_args():
    parser = argparse.ArgumentParser(description="Эмулятор командной оболочки")
    parser.add_argument("--username", required=True, help="Имя пользователя")
    parser.add_argument("--hostname", required=True, help="Имя компьютера")
    parser.add_argument("--vfs", required=True, help="Путь к виртуальной файловой системе (tar архив)")
    parser.add_argument("--script", required=False, help="Путь к стартовому скрипту", default=None)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    shell = ShellEmulator(args.username, args.hostname, args.vfs, args.startup_script)
    shell.run()
