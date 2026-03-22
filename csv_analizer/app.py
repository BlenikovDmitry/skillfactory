import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import csv


#функция загрузки графика по одному полю
#просто отдает файл на выгрузку при нажатии на кнопку
def download_single(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)

    st.download_button(
        label="Скачать график как PNG",
        data=buf,
        file_name='distribution.png',
        mime="image/png",
        #on_click=remove_plot_after_download_single
    )

#функция загрузки графика по двум полям
#просто отдает файл на выгрузку при нажатии на кнопку
def download_double(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)

    st.download_button(
        label="Скачать график как PNG",
        data=buf,
        file_name='dependence.png',
        mime="image/png",
    )

#функция отрисовки гистограммы и код для отправки графика на скачивание пользователю
#Аргументы:
#data - отрисовываемые данные
#name - название гистограммы
#color - цвет гистограммы
def single_field_hist(data, name, color):
    fig, ax = plt.subplots(figsize=(10, 10))
    
    ax.set_title(name)
    ax.set_xlabel("Виды значений")
    ax.set_ylabel("Число значений")



    ax.hist(data, bins=30, linewidth=2, color=color, edgecolor="black", rwidth=0.9)
    ax.grid(True)

    st.pyplot(fig)

    return fig

#функция отрисовки линейного графика и код для отправки графика на скачивание пользователю
#Аргументы:
#data - название столбцов выбранных пользователем
#df - датафрейм
def double_field_line(data, df):
    if len(data) < 2:
        st.write('Выберите еще один столбец')
        return
    
    x = df[data[0]]
    y = df[data[1]]
    
    fig, ax = plt.subplots(figsize=(25,10))
    ax.set_title('Зависимость данных')
    ax.set_xlabel(data[0])
    ax.set_ylabel(data[1])
    ax.plot(x, y, '-bo', linewidth=2, markersize=6, markerfacecolor='red')
    ax.legend([data[0]])
    ax.grid()

    st.pyplot(fig)

    return fig

    
#функция отрисовки рассеяния точек и код для отправки графика на скачивание пользователю
#Аргументы:
#data - название столбцов выбранных пользователем
#df - датафрейм
def double_field_scatter(data, df):
    if len(data) < 2:
        st.write('Выберите еще один столбец')
        return
    
    x = df[data[0]]
    y = df[data[1]]
    
    fig, ax = plt.subplots(figsize=(25,10))
    ax.set_title('Зависимость данных')
    ax.set_xlabel(data[0])
    ax.set_ylabel(data[1])
    ax.scatter(x, y, s=60, c='blue', edgecolors='black', alpha=0.7)
    ax.legend([data[0]])
    ax.grid()

    st.pyplot(fig)

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)

    return fig


#функция для парсинга колонок в форматы:
#числа
#даты
#если не числа и не даты - то строки
def parse_df_cols(columns, df):
    for col in columns:
        try:
            num = pd.to_numeric(df[col].str.replace(',', '.'))
            if len(num) > 0:
                df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors = 'coerce')          
                continue
        except:
            pass
#непонятно только какое может быть особое внимание к парсингу дат, если формат может быть разным и мы отдаем его на откуп парсеру
        try:
            dat = pd.to_datetime(df[col])
            if len(dat) > 0:
                df[col] = pd.to_datetime(df[col], errors = 'coerce')
                continue
        except:
            pass
    return df
#функция для фильтрации столбцов - выбирает только числовые метрики
def filter_cols(columns, df):
    res = []
    for col in columns:
        if (str(df[col].dtype)[0:3] == 'Flo' or str(df[col].dtype)[0:3] == 'Int') and col != 'Unnamed: 0': # дополнительно проверяем чтобы не попал столбец 0(индекс)
            res.append(col)
    return res

st.header("Статистический анализ датасета")

uploaded_file = st.file_uploader("Выберите CSV файл", type="csv")
#через выбор приколачиваем кодировку
#позволит перебором анализировать разные файлы с разными кодировками
user_enc = st.radio("Кодировка:", ["utf-8", "cp1251"], horizontal=True)
#если удалось прочитать файл, то есть он не битый, едем дальше
if uploaded_file is not None:
    #пробуем прочитать файл в выбранной пользователем кодировке
    #если получается - едем дальше
    #если нет - выдаем исключение UnicodeDecodeError и позволяем пользователю изменить выбор
    try:
                        
        df =  pd.read_csv(uploaded_file, sep=None, engine='python', encoding=user_enc)
        st.dataframe(df)

        #инициализация переменной состояния для сохранения данных перед отрисовкой
        #данные для графика по одному столбцу
        if 'data' not in st.session_state:
            st.session_state.data = ''
        #флаг, что нажата кнопка для отрисовки графика по 1 столбцу - нужно при перерисовке
        if  'single_press' not in st.session_state:
            st.session_state.single_press = False
        #выбранный столбец графика по одному столбцу - нужно при перерисовке
        if  'select_column' not in st.session_state:
            st.session_state.select_column = ''
        #флаг, что нажата кнопка 
        #if  'double_press' not in st.session_state:
         #   st.session_state.double_press = False
        #список столбцов дл отрисовки графика по нескольким столбцам 
        if "selected_columns" not in st.session_state:
            st.session_state.selected_columns = []


            
        #выбор столбца и рассчитываемой статистики
        st.header("Расчет базовых статистик")
        df_tmp = df.astype('string')
        #заполняем значения nan строкой '0' во избежание ошибок при распознавании столбца и преобразовании
        df_tmp = df_tmp.fillna('0')
        df_tmp = parse_df_cols(df_tmp.columns, df_tmp)
        cols = filter_cols(df_tmp.columns, df_tmp)
        st.session_state.cols = cols
        select_column = st.selectbox('Выберите столбец:',(cols))
        select_statistic = st.selectbox('Выберите статистику:',('среднее значение', 'медиана', 'среднеквадратичное отклонение'))
        
        #если уже нажималась кнопка - перерисовываем график при очередном rerun
        #позволяет при изменении столбца/метрики перерировать график/значение
        if st.session_state.single_press == True:
            if select_statistic == 'среднее значение':
                st.write(f'Среднее значение: {round(df_tmp[select_column].mean(),2)}')
                st.session_state.data = df_tmp[select_column]
                st.session_state.select_column = select_column
                download_single(single_field_hist(st.session_state.data, 'Распределение столбца ' + st.session_state.select_column, 'blue'))
            if select_statistic == 'медиана':
                st.write(f'Медиана: {round(df_tmp[select_column].median(),2)}')
                st.session_state.data = df_tmp[select_column]
                st.session_state.select_column = select_column
                download_single(single_field_hist(st.session_state.data, 'Распределение столбца ' + st.session_state.select_column, 'blue'))
            if select_statistic == 'среднеквадратичное отклонение':
                st.write(f'Среднеквадратичное отклонение: {round(df_tmp[select_column].std(),2)}')
                st.session_state.data = df_tmp[select_column]
                st.session_state.select_column = select_column
                download_single(single_field_hist(st.session_state.data, 'Распределение столбца ' + st.session_state.select_column, 'blue'))
                
            
                

                
                    
        #при нажатии на кнопку "Анализ" все данные заранее приведены к нужным типам
        #а также данные в выпадающем списке только числовые
        #делаем расчет - графики не отрисовываем - они будут рисоваться при rerun - а тут только задаем переменные сессии
        if st.button("Анализ"):
            
            if select_statistic == 'среднее значение':
                    df_tmp[select_column] = pd.to_numeric(df_tmp[select_column], errors = 'coerce')
                    st.write(f'Среднее значение: {round(df_tmp[select_column].mean(),2)}')
                    st.session_state.data = df_tmp[select_column]
                    st.session_state.single_press = True
                    st.session_state.select_column = select_column
                    st.rerun()

            if select_statistic == 'медиана':
                    df_tmp[select_column] = pd.to_numeric(df_tmp[select_column], errors = 'coerce')
                    st.write(f'Медиана: {round(df_tmp[select_column].median(),2)}')
                    st.session_state.data = df_tmp[select_column]
                    st.session_state.single_press = True
                    st.session_state.select_column = select_column
                    st.rerun()

            if select_statistic == 'среднеквадратичное отклонение':
                    df_tmp[select_column] = pd.to_numeric(df_tmp[select_column], errors = 'coerce')
                    result = round(df_tmp[select_column].mean(),2)
                    st.write(f'Среднеквадратичное отклонение: {round(df_tmp[select_column].std(),2)}')
                    st.session_state.data = df_tmp[select_column]
                    st.session_state.single_press = True
                    st.session_state.select_column = select_column
                    st.rerun()

                        
            
        #код для отрисовки графиков пар столбцов
        #пользователь выбирает два столбца, передаем в функции отрисовки и экспорта
        #есть проверка на число столбцов максимальное и минимальное
        #тут нет хитрой перерисовки, при нажатии на кнопку скачивания график выгружается и пропадает
        st.header("Графики для пар столбцов")
        selected_columns = st.multiselect('Выберите колонки для графика:', cols, max_selections=2, key ='selected_columns')
        select_graphics = st.selectbox('Выберите график:',('Линейный', 'Диаграмма рассеяния'))

        if len(st.session_state.selected_columns) == 2:
            if st.button("Построить график"):
                if select_graphics == 'Линейный':
                    download_double(double_field_line(st.session_state.selected_columns, df_tmp))
                if select_graphics == 'Диаграмма рассеяния':
                    download_double(double_field_scatter(st.session_state.selected_columns, df_tmp))
        else:
            st.info('Выберите два столбца')
        


    #отлавливаем ошибки кодировки
    except UnicodeDecodeError:
        st.write('Некорректная кодировка')
    #отлавливаем ошибки - битый файл и его не распарсить
    except csv.Error:
        st.write('Файл битый - ошибка парсинга')
    #отлавливаем ошибки - файл битый и не удалось определить разделитель
    except pd.errors.ParserError:
        st.write('Файл битый - не удалось определить разделитель')
    #отлавливаем все остальные ошибки
    except Exception as e:
        st.error(f"Произошла неизвестная ошибка: {e}")
        
        
        




        

    


   

