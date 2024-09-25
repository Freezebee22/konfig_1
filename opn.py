from zipfile import ZipFile

with ZipFile('qwerty.zip', 'a') as zip:
    while True:
        command = input('$ ')
        if command == 'exit':
            break
        elif command == 'test':
            print('yes')
        elif command.startswith('ls'):
            for file in zip.namelist():
                print(file)
        else:
            print('idk')