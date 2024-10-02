import unittest
import time
from emulator import ShellEmulator

class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        """Подготовка перед каждым тестом"""
        self.emulator = ShellEmulator(username="testuser", hostname="localhost", vfs="tartar.tar", script=None)

    def test_ls_root(self):
        """Тест команды ls в корневой директории"""
        result = self._capture_output(self.emulator.ls, [])
        self.assertIn('papka', result)  # Проверяем, что 'papka' присутствует в выводе

    def test_cd_and_ls(self):
        """Тест команды cd и ls внутри папки"""
        self.emulator.cd(["papka"])  # Переходим в папку 'papka'
        result = self._capture_output(self.emulator.ls, [])
        self.assertIn('mama', result)  # Проверяем, что 'mama' находится в 'papka'

    def test_cd_back_to_root(self):
        """Тест команды cd для возвращения в корневую директорию"""
        self.emulator.cd(["papka"])  # Переходим в папку 'papka'
        self.emulator.cd([".."])  # Возвращаемся в корневую директорию
        self.assertEqual(self.emulator.cwd, "/")  # Проверяем, что текущая директория - это корень

    def test_uname(self):
        """Тест команды uname"""
        result = self._capture_output(self.emulator.uname, [])
        self.assertEqual(result.strip(), "Linux")  # Проверяем, что команда uname возвращает 'Linux'

    def test_uname_with_a(self):
        """Тест команды uname с опцией -a"""
        result = self._capture_output(self.emulator.uname, ["-a"])
        self.assertIn("Linux localhost 5.15.0-1-generic", result)  # Проверяем вывод с опцией -a

    def test_uptime(self):
        """Тест команды uptime"""
        result = self._capture_output(self.emulator.uptime, [])
        self.assertIn("user(s)", result)  # Проверяем стандартный вывод команды uptime

    def test_uptime_with_p(self):
        """Тест команды uptime с опцией -p (в минутах)"""
        time.sleep(2)  # Ждём несколько секунд для корректного времени работы
        result = self._capture_output(self.emulator.uptime, ["-p"])
        self.assertIn("up 0 minutes", result)  # Проверяем вывод времени работы в минутах

    def test_uptime_with_s(self):
        """Тест команды uptime с опцией -s (время запуска программы)"""
        result = self._capture_output(self.emulator.uptime, ["-s"])
        self.assertIn("Startup time:", result)  # Проверяем вывод времени старта программы

    def test_cd_nonexistent_directory(self):
        """Тест ошибки при переходе в несуществующую директорию"""
        result = self._capture_output(self.emulator.cd, ["nonexistent"])
        self.assertIn("No such file or directory", result)  # Проверяем, что выводится сообщение об ошибке

    def test_exit(self):
        """Тест команды exit"""
        with self.assertRaises(SystemExit):  # Ожидаем завершения программы
            self.emulator.exit_shell()

    def _capture_output(self, func, args):
        from io import StringIO
        import sys
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            func(args)
            return out.getvalue()
        finally:
            sys.stdout = saved_stdout

if __name__ == '__main__':
    unittest.main()
