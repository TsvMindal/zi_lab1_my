import os
import random
import re
import subprocess
import time
import signal
import sys

def signal_handler(sig, frame):
    end_time = time.time()
    total_time = end_time - start_time
    created_files = iteration - 1

    print(f"Программа была прервана.")
    print(f"Время выполнения программы: {total_time} секунд")
    print(f"Количество созданных файлов: {created_files}")

    # Удаляем все новые файлы, кроме последнего
    for i in range(1, created_files):
        file_to_delete = f'modified_files/modified_leasing_{i}.txt'
        os.remove(file_to_delete)

    sys.exit(0)

# Устанавливаем обработчик прерывания Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Запоминаем время начала выполнения программы
start_time = time.time()

# Функция для случайной замены регистра букв в слове
def random_change_case(word):
    return ''.join(random.choice([c.upper(), c.lower()]) for c in word)

# Функция для случайного удаления символов "." и ";"
def random_remove_chars(text):
    return re.sub(r'[.;]', '', text, random.randint(0, 5))

# Функция для случайного замены "млн" на "миллиона(-ов)" с вероятностью 10%
def random_replace_mln(text):
    return re.sub(r'\bмлн\b', 'миллиона(-ов)', text, random.randint(0, 5), flags=re.IGNORECASE)


# Функция для случайной замены "и" на "и/или" с вероятностью 10%
def random_replace_and(text):
    return re.sub(r'\b и \b', ' и/или ', text, random.randint(0, 5), flags=re.IGNORECASE)

# Метод для создания нового модифицированного файла на основе предыдущего файла
def create_modified_file(previous_file_name, iteration):
    with open(previous_file_name, 'r', encoding='utf-8') as previous_file:
        previous_text = previous_file.read()

    # Разбиваем текст на строки и отделяем отступы от текста
    original_lines = previous_text.splitlines()
    indents = [re.match(r'^\s*', line).group(0) for line in original_lines]
    text_lines = [line.lstrip() for line in original_lines]

    # Случайно меняем регистр букв, удаляем символы и добавляем пробелы в каждой строке
    modified_lines = []
    for line in text_lines:
        modified_line = random_remove_chars(line)
        words = modified_line.split()
        for j in range(len(words)):
            if random.random() < 0.1:  # Вероятность изменения регистра - 10%
                words[j] = random_change_case(words[j])
            if random.random() < 0.1:  # Вероятность добавления пробела - 10%
                words[j] += ' '
        modified_line = ' '.join(words)
        modified_lines.append(modified_line)

    # Случайно заменяем "млн" на "миллиона(-ов)" с вероятностью 10%
    for j in range(len(modified_lines)):
        if random.random() < 0.1:
            modified_lines[j] = random_replace_mln(modified_lines[j])

    # Случайно заменяем "и" на "и/или" с вероятностью 10%
    for j in range(len(modified_lines)):
        if random.random() < 0.1:
            modified_lines[j] = random_replace_and(modified_lines[j])

    # Восстанавливаем форматирование (отступы)
    modified_text = [indents[j] + modified_line for j, modified_line in enumerate(modified_lines)]
    modified_text = '\n'.join(modified_text)

    # Создаем папку modified_files, если её нет
    if not os.path.exists('modified_files'):
        os.makedirs('modified_files')

    # Открываем файл для записи измененного текста с сохранением отступов
    modified_file_name = f'modified_files/modified_leasing_{iteration}.txt'
    with open(modified_file_name, 'w', encoding='utf-8') as modified_file:
        modified_file.write(modified_text)

    # Генерируем хеш-код SHA-1 для текущего модифицированного файла с использованием OpenSSL
    try:
        openssl_output = subprocess.check_output(['openssl', 'dgst', '-sha1', modified_file_name])
        modified_hash = openssl_output.decode('utf-8').split()[-1]
    except subprocess.CalledProcessError:
        modified_hash = None

    return modified_file_name, modified_hash

# Чтение оригинального текста из leasing.txt
with open('leasing.txt', 'r', encoding='utf-8') as original_file:
    original_text = original_file.read()

# Генерируем хеш-код SHA-1 для оригинального файла leasing.txt с использованием OpenSSL
try:
    openssl_output = subprocess.check_output(['openssl', 'dgst', '-sha1', 'leasing.txt'])
    original_hash = openssl_output.decode('utf-8').split()[-1]
    print(f"Хеш-код оригинального файла leasing.txt: {original_hash}")
except subprocess.CalledProcessError:
    original_hash = None
    print("Не удалось создать хеш-код для оригинального файла leasing.txt.")

if original_hash is None:
    print("Программа завершена из-за ошибки в создании хеш-кода для оригинального файла.")
else:
    original_file_size = os.path.getsize('leasing.txt')
    print(f"Размер оригинального файла: {original_file_size} байт")
    # Создаем модифицированные файлы до обнаружения коллизии
    previous_file = 'leasing.txt'
    iteration = 1
    while True:
        modified_file, modified_hash = create_modified_file(previous_file, iteration)
        modified_file_size = os.path.getsize(modified_file)
        print(f"Создан файл номер {iteration}: {modified_file}. Размер файла: {modified_file_size} байт")
        # Сравниваем текущий модифицированный хеш-код с хеш-кодом оригинального файла
        if modified_hash == original_hash:
            print(f"Коллизия обнаружена при создании файла {modified_file}: {modified_hash}. Программа завершена.")
            end_time = time.time()
            total_time = end_time - start_time
            print(f"Время выполнения программы: {total_time} секунд")
            break

        previous_file = modified_file
        iteration += 1
