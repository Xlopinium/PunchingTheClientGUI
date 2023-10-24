import tkinter as tk
from tkinter import filedialog
import pandas as pd
import time
import requests
from bs4 import BeautifulSoup
import re

# HEX and dehex
hex_inn = r'\u0418\u041d\u041d'
decoded_inn = bytes(hex_inn, "utf-8").decode("unicode_escape")
hex_OGRN = r'\u041e\u0413\u0420\u041d'
decoded_OGRN = bytes(hex_OGRN, "utf-8").decode("unicode_escape")

def validate_ogrn(ogrn):
    # Checking the length and first digit
    if len(ogrn) != 15:
        return False
    if ogrn[0] not in ['1', '3', '5']:
        return False
    return True  

def search_inn_via_ogrn(domain):
    # Step 1: Search for OGRN
    url = f"https://ya.ru/search/?text=site:{domain}+{decoded_OGRN}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        texts = soup.stripped_strings 

        for text in texts:
            match = re.search(r'\b\d{13,15}\b', text)
            if match:
                ogrn = match.group(0)
                print(ogrn)
                if validate_ogrn(ogrn):
                    return ogrn #Возвращаю найденный огрн из сниппета
                    ## Step 2: Using the OGRN, we look for the INN
                    #if ogrn[0] in ['1', '5']:
                    #    inn_length = 10
                    #else:
                    #    inn_length = 12
                    #inn_pattern = fr'{decoded_OGRN}\s?{ogrn}\D*\s?\d{inn_length}'
                    #time.sleep(2)
                    #url_inn = f"https://duckduckgo.com/html/?q={decoded_OGRN}+{ogrn}"
                    #response_inn = requests.get(url_inn, headers=headers)
                    #if response_inn.status_code == 200:
                    #    soup_inn = BeautifulSoup(response_inn.text, 'html.parser')
                    #    texts_inn = soup_inn.stripped_strings 
                    #    for text_inn in texts_inn:
                    #        match_inn = re.search(inn_pattern, text_inn)
                    #        print(text_inn)
                    #        if match_inn:
                    #            return match_inn.group(0)[-inn_length:]
    return None  

def search_inn(domain):
    time.sleep(5)
    url = f"https://duckduckgo.com/html/?q=site:{domain}+{decoded_inn}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        texts = soup.stripped_strings 

        for text in texts:
            print(text)
            match = re.findall(r'\d{10,12}', text) ### Верное решение согласно, которому есть ИНН
            if match:
                return match[0]
    return None 

## Чтение CSV файла
#df = pd.read_csv('SoonSnippit.csv')  # Файл для чтения domain

# Применение функций парсинга к каждому домену
def run_processing():
    global df
    text_widget.delete(1.0, tk.END)  # очистить виджет Text
    file_path = filedialog.askopenfilename()
    if file_path:
        df = pd.read_csv(file_path)
        text_widget.insert(tk.END, df.head().to_string())  # показать первые несколько строк
        for index, row in df.iterrows():
            domain = row['Domain']
            print(f"Processing {domain}...")
            ogrn_snippet = search_inn_via_ogrn(domain)
            inn_snippet = search_inn(domain)
            df.at[index, 'OGRN_Snippet'] = ogrn_snippet
            df.at[index, 'INN_Snippet'] = inn_snippet
            time.sleep(5)
        text_widget.delete(1.0, tk.END)  # очистить виджет Text
        text_widget.insert(tk.END, df.head().to_string())  # показать обновленные первые несколько строк

# Сохранение обновленного DataFrame в новый CSV файл
# Функция для сохранения результатов в CSV файл
def save_csv():
    global df
    file_path = filedialog.asksaveasfilename(defaultextension=".csv")
    if file_path:
        df.to_csv(file_path, index=False)

# Инициализация Tkinter
root = tk.Tk()

run_button = tk.Button(root, text="Run process", command=run_processing)
run_button.pack()

save_button = tk.Button(root, text="Save CSV", command=save_csv)
save_button.pack()

# Виджет Text для отображения данных CSV
text_frame = tk.Frame(root)
text_frame.pack()

text_widget = tk.Text(text_frame, wrap=tk.NONE, width=50, height=10)
text_widget.grid(row=0, column=0, sticky="nsew")

# Добавляем ползунки
text_scroll_y = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
text_scroll_y.grid(row=0, column=1, sticky="ns")
text_widget.config(yscrollcommand=text_scroll_y.set)

text_scroll_x = tk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
text_scroll_x.grid(row=1, column=0, sticky="ew")
text_widget.config(xscrollcommand=text_scroll_x.set)

root.mainloop()
