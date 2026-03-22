from tkinter import *
from tkinter import ttk
import tkinter as tk
import random

'''
обработчик кнопки начала игры
подтягивает глобальные переменные для игрового процесса инструкцией global
получает имя игрока из текстового поля - если ввода в поле нет, используется имя по умолчанию
и вызывает отрисовку основного экрана игры  main_game_screen
'''
def start_game():
    global player_name
    player_name = ''
    global player_win
    global ii_win
    player_win = False
    ii_win = False
    global counter_steps
    global game_run
    global counter_full_fields
    counter_steps = 0
    counter_full_fields = 0
    game_run = True
    # Получаем текст из поля ввода
    player_name = pname_entry.get()
    if player_name == '':
        pname_label_welcome.config(text=f'Привет, username и поехали')
        player_name = 'username'
        main_game_screen()
    else:
        pname_label_welcome.config(text=f'Привет, {player_name[0:8]} и поехали')
        main_game_screen()

'''
функция проверяет условие победы
если по горизонтали, вертикали или диагонали есть поля, заполненные одинаково(крестики или нолики),
то диагональ красится розовым и в зависимости от знака передается флаг победы игрока или компьютера
'''
def check_win(field,smb):
    global game_run
    global player_win
    global ii_win
    for n in range(3):
        if field[n][0].cget('text') == smb and field[n][1].cget('text') == smb and field[n][2].cget('text') == smb:
           game_run = False
           field[n][0].config(bg ='pink')
           field[n][1].config(bg ='pink')
           field[n][2].config(bg ='pink')
           if smb == "X":
               player_win = True
               return
           if smb == "O":
               ii_win = True
               return
                   
           
        if field[0][n].cget('text') == smb and field[1][n].cget('text') == smb and field[2][n].cget('text') == smb:
 
           game_run = False
           field[0][n].config(bg ='pink')
           field[1][n].config(bg ='pink')
           field[2][n].config(bg ='pink')
           if smb == "X":
               player_win = True
               return
           if smb == "O":
               ii_win = True
               return

        if field[0][0].cget('text') == smb and field[1][1].cget('text') == smb and field[2][2].cget('text') == smb:

            game_run = False
            field[0][0].config(bg ='pink')
            field[1][1].config(bg ='pink')
            field[2][2].config(bg ='pink')
            if smb == "X":
               player_win = True
               return
            if smb == "O":
               ii_win = True
               return

        if field[2][0].cget('text') == smb and field[1][1].cget('text') == smb and field[0][2].cget('text') == smb:
 
            game_run = False
            field[2][0].config(bg ='pink')
            field[1][1].config(bg ='pink')
            field[0][2].config(bg ='pink')
            if smb == "X":
               player_win = True
               return
            if smb == "O":
               ii_win = True
               return

'''
функция реализует обработку нажатия на кнопки игрового поля
осуществляет контроль состояния игры
Алгоритм простой:
- игрок кликает на пустой клетке, клетка перекрашивается в красный цвет, в ней проставляется крестик и она становится неактивной
-проверяем условия победы функцией check_win, если успех, то объявляем победу игрока
- компьютер выбирает случайную незанятую клетку, проставляет в ней нолик, закрашивает в синий цвет
-проверяе условие победы функцией check_win, если успех, объявляем победу компьютера
- если заполнено 8 полей и никто низ соперников не создал условий победы - объявляется ничья
'''
def make_step(r,c, buttons,count_steps_main):
    global counter_steps
    global game_run
    global counter_full_fields
    global player_win
    global ii_win
    if game_run == True and counter_full_fields != 8:
        if buttons[r][c].cget("text") == "":
            buttons[r][c].config(bg="red",text = "X", state='disabled')
            counter_steps += 1
            counter_full_fields += 1
            count_steps_main.config(text = str(counter_steps))
        check_win(buttons,"X")
            
        if game_run == False and player_win == True:
            winner = tk.Label(master = window, text = f'Победил {player_name}', font=('Arial', 20, 'bold'), bg='#FFDAB9')
            winner.grid(row = 4, column = 0)
        tmp_r = 0
        tmp_c = 0
        while buttons[tmp_r][tmp_c].cget("text") == "X" or buttons[tmp_r][tmp_c].cget("text") == "O":
            tmp_r = random.randint(0,2)
            tmp_c = random.randint(0,2)
        buttons[tmp_r][tmp_c].config(bg="blue",text = "O", state='disabled')
        counter_full_fields += 1
        check_win(buttons,"O")
        if game_run == False and ii_win == True:
            winner = tk.Label(master = window, text = 'Победил компьютер', font=('Arial', 20, 'bold'), bg='#FFDAB9')
            winner.grid(row = 4, column = 0)

    if counter_full_fields == 8 and player_win == False and ii_win == False:
        winner = tk.Label(master = window, text = 'Ничья', font=('Arial', 20, 'bold'), bg='#FFDAB9')
        winner.grid(row = 4, column = 0)
        
'''
функция очищает окно от виджетов стартового окна функцией clear_window
заполняет окно виджетами основного окна и игровым полем 3 на 3
позволяет  сбросить игровой процесс кнопкой "Начать сначала" с обработчиком retry
позволяет выйти на стартовый экран кнопкой "Выход" c обработчиком back
реализует слушатель клика на кнопки игрового поля и обрабатывает нажатия функцией make_step
'''
def main_game_screen():
    clear_window()
    global player_name
    counter_steps = 0
    elapsed_time = 0
    player_name_lbl_dec = tk.Label(master = window, text = 'Имя игрока:', font=('Arial', 12, 'bold'), bg='#FFDAB9')
    player_name_lbl_dec.grid(row = 0, column = 0)
    player_name_lbl_main = tk.Label(master = window, text = player_name, font=('Arial', 12, 'bold'), bg='#FFDAB9')
    player_name_lbl_main.grid(row = 0, column = 1)

    
    count_steps_dec = tk.Label(master = window, text = 'Сделано ходов:', font=('Arial', 12, 'bold'), bg='#FFDAB9')
    count_steps_dec.grid(row = 1, column = 0)
    
    count_steps_main =  tk.Label(master = window, text = str(counter_steps), font=('Arial', 12, 'bold'), bg='#FFDAB9')
    count_steps_main.grid(row = 1, column = 1)

    
    button_help = Button(master = window, width = 12, text="Начать сначала", command=retry,  font=('Arial', 18, 'bold'))
    button_help.grid(row = 2, column = 0,padx = 5, pady = 5)
    button_exit = Button(master = window, width = 12, text="Выход", command=back, font=('Arial', 18, 'bold'))
    button_exit.grid(row = 3, column = 0, padx = 5, pady = 5)
    counter = 0
    counter1 = 5

    game_field = [[None for _ in range(3)] for _ in range(3)]
    for r in range(3):
        for c in range(3):
            game_field[r][c] = tk.Button(window, text="",command=lambda r=r, c=c: make_step(r, c, game_field, count_steps_main), width = 10, height = 5)
            game_field[r][c].grid(row=r, column=c+2)
'''
функция возврата в стартовое меню
очищает экран от виджетов игрового поля и вызывает отрисовку стартового окна
'''
def back():
    clear_window()
    init()
'''
функция вызывается при нажатии на кнопку 'Начать сначала' основного экрана
стирает все виджеты основного экрана для сброса их состояния
зануляет все переменные игрового состояния и вызывает отрисовку заново
'''
def retry():
    clear_window()
    global player_win
    global ii_win
    player_win = False
    ii_win = False
    global counter_steps
    global game_run
    global counter_full_fields
    counter_steps = 0
    counter_full_fields = 0
    game_run = True
    main_game_screen()
    
    
        
def clear_window():
    # Удалить все объекты из окна
    for widget in window.winfo_children():
        widget.destroy()
'''
первая вызываемая функция игры
наносит разметку стартового окна и содержит обработчик кнопки начала игры: start_game
'''
def init():
    #надпись главного меню
    global lbl_title
    lbl_title = tk.Label(master = window, text = 'Крестики - нолики', font=('Arial', 24, 'bold'),bg='#FFDAB9')
    lbl_title.grid(row = 0, column = 0, padx = 5, pady = 5)

    global lbl_pname
    lbl_pname = tk.Label(master = window, text = 'Имя игрока(не более 8 символов):', font=('Arial', 18, 'bold'),bg='#FFDAB9')
    lbl_pname.grid(row = 1, column = 0, padx = 5, pady = 5)
    #поле ввода имени игрока
    global pname_entry
    pname_entry = ttk.Entry(master = window, width = 20, font = ('Arial', 18, 'bold'))
    pname_entry.grid(row = 2, column = 0, padx = 5, pady = 5)

    global pname_label_welcome
    pname_label_welcome = tk.Label(master = window, width = 50, font = ('Arial', 18, 'bold'),bg='#FFDAB9')


    # Создаем кнопку для получения текста из поля ввода имени игрока
    global start_button
    start_button = Button(master = window, width = 20, text="Начать игру", command=start_game, font=('Arial', 18, 'bold'))
    start_button.grid(row = 3, column = 0, padx = 5, pady = 5)

    pname_label_welcome.grid(row = 5, column = 0, padx = 5, pady = 5)
    
    
'''
объявляем объект окна, задаем параметры:
-заголовок
-размер
-отключаем возможность изменения размера
-цвет фона
'''
window = Tk()
window.title("Крестики - нолики")
window.geometry("700x500")
window.resizable(False, False)
window.config(bg='#FFDAB9')
'''
объявляем виджеты для экрана меню
'''
lbl_title = ''
lbl_pname = ''
pname_entry = ''
start_button = ''
records_button = ''
pname_label_welcome = ''

'''
вызываем отрисовку главного экрана
это основная функция ,которая запускает весь процесс отрисовки и игры
остальные вызываются внутри нее
'''

init()

'''
объявляем виджеты для экрана непосредственно игры
'''
player_name_lbl_dec = ''
player_name_lbl_main = ''
count_steps_dec = ''
count_steps_main = ''
button_help = ''
button_exit = ''
'''
вспомогательные переменные для получени состояния игры
'''
#число сделанных ходов игрока
counter_steps = 0
#флаг запущена ли игрв
game_run = True
#подсчет заполненных полей чтобы понять, когда объявлять ничью
counter_full_fields = 0
#переменная имени игрока для передачи в поле игры
player_name = ''
#флаг, проверяющий победил игрок или нет
player_win = False
#флаг, проверяющий победил компьютер или нет
ii_win = False

window.mainloop()
