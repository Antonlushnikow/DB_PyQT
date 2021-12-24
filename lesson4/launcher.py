import subprocess
import sys

processes = []


def main():
    count = 2  # число клиентов по умолчанию
    try:
        count = int(sys.argv[1])
    except TypeError:
        print('Неверный аргумент - должно быть число')
        return
    except IndexError:
        print('Не указан аргумент. Запускается два клиента')
    finally:
        # processes.append(subprocess.Popen('python ./server/app/main.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        for _ in range(count):
            processes.append(subprocess.Popen('python ./client/app/main.py', creationflags=subprocess.CREATE_NEW_CONSOLE))


if __name__ == '__main__':
    main()
