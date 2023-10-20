import librosa
import keyfinder
import eyed3
import os
import shutil

import sqlite3


import logging
import io

log_stream = io.StringIO()
logging.basicConfig(stream=log_stream, level=logging.INFO)

from alive_progress import alive_bar


def find_bpm(File: str):
    #print("-----------------------")
    global track_id
    global folder_cover
    y, sr = librosa.load(File)
    #print("Файл: " + File + " Номер трека: " + str(track_id))
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    first_beat_time, last_beat_time = librosa.frames_to_time((beats[0], beats[-1]), sr=sr)
    tempo = (60 / ((last_beat_time - first_beat_time) / (len(beats) - 1)))
    #print(round(tempo))
    return round(tempo)

def find_key(File: str):
    y, sr = librosa.load(File, duration=120)
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    unebarque_fsharp_maj = keyfinder.Tonal_Fragment(y_harmonic, sr, tend=22)
    key = str(unebarque_fsharp_maj.print_key())
    #print("Тональность: " + key)
    return key

log_stream = io.StringIO()
logging.basicConfig(stream=log_stream, level=logging.INFO)

from progress.bar import Bar

read_folder = "D:/"   #"/Volumes/Danon_work"
save_folder =  "F:/" #"/Volumes/USB DISK"
track_id = 0
folder_cover = ""
folder_mp3 = ""
def i_mp_file(save_folder, name, file: str, folder):
    global folder_cover
    global folder_mp3
    audiofile = eyed3.load(file)
    images = audiofile.tag.images
    if not os.path.isdir(save_folder):
        os.mkdir(save_folder)

    if not os.path.isdir(f"{save_folder}/{name}"):
        os.mkdir(f"{save_folder}/{name}")

    shutil.copy2(file, f"{save_folder}/{name}")

    with open(f'{save_folder}/{name}/{name}.jpg', 'wb+') as file:
        file.write(images[0].image_data)
    folder_cover = f'{folder}/{name}/{name}.jpg'
    folder_mp3 = f'{folder}/{name}/{name}.mp3'

def forlder_down(folder: str):
    global track_id
    global folder_cover
    global folder_mp3
    directory = f"{read_folder}/{folder}"
    folder_save = f"{save_folder}/{folder}"

    list_mp = [_ for _ in os.listdir(directory) if
               (not ("._" in os.path.splitext(_)[0] or "." == os.path.splitext(_)[0][0]))]
    with alive_bar(len(list_mp)) as bar:
        for filename in list_mp:
            try:
                name_file = os.path.splitext(filename)[0]
                path_file = os.path.join(directory, filename)
                i_mp_file(folder_save, name_file, path_file, folder)
                bpm = find_bpm(path_file)
                key = find_key(path_file)
                db.insert_data("music", (track_id, folder_cover,folder_mp3, bpm, key))
                track_id = track_id + 1
                bar()
            except Exception as e:
                # handle the exception
                print("An exception occurred:", e)  # An exception occurred: division by zero


def start():
    for i in os.listdir(f"{read_folder}"):
        try:
            forlder_down(i)
        except:
            ...


class Database:
    def __init__(self):
        self.db_name = "tracks.db"
        self.connection = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            print(f"Успешное подключение к базе данных {self.db_name}")
        except sqlite3.Error as e:
            print(f"Ошибка подключения к базе данных: {e}")

    def create_table(self, table_name, columns):
        try:
            create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
            self.cursor.execute(create_table_query)
            self.connection.commit()
            print(f"Таблица {table_name} успешно создана")
        except sqlite3.Error as e:
            print(f"Ошибка при создании таблицы: {e}")

    def insert_data(self, table_name, data):
        try:
            insert_query = f"INSERT INTO {table_name} VALUES ({', '.join(['?'] * len(data))})"
            self.cursor.execute(insert_query, data)
            self.connection.commit()
            #print("Данные успешно вставлены")
        except sqlite3.Error as e:
            print(f"Ошибка при вставке данных: {e}")

    def select_data(self, table_name, condition="1"):
        try:
            select_query = f"SELECT * FROM {table_name} WHERE {condition}"
            self.cursor.execute(select_query)
            result = self.cursor.fetchall()
            return result
        except sqlite3.Error as e:
            print(f"Ошибка при выборке данных: {e}")
            return []

    def close(self):
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных закрыто")


if __name__ == "__main__":
    db = Database()
    db.connect()
    db.create_table("music", "id INTEGER PRIMARY KEY, path_cover TEXT,path_mp3 TEXT, bpm INTEGER, key INTEGER")
    start()
    db.close()