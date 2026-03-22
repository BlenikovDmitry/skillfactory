import streamlit as st
import config as cnf
import statistics
import datetime
import pandas as pd

#функция проверки ввода поля 'на лету'
def input_check_digit(value):
    if value.isdigit():
        return ':blue[Ввод верный!]'
    else:
        return ':red[Ошибка! Введите целое положительное число число]'
    
#функция проверки ввода всех полей ввода перед расчетом 
def input_check_all(*argc):
    for i in argc:
        if input_check_digit(i) == ':red[Ошибка! Введите целое положительное число число]':
            return False
    return True

#функция расчета ежемесячного платежа по кредиту с аннуитетным платежом
def annuitet_payment(credit_sum, interest, period):
    i = interest / 12 / 100
    n = period * 12
    k = (i * (1 + i)**n) / ((1+i)**n - 1)
    res = credit_sum * k
    return round(res,2)

#функция расчета ежемесячного платежа по кредиту с аннуитетным платежом
def differ_payment(credit_sum, interest, period):
    res = []
    period_month = period * 12
    fix = credit_sum / period_month
    i = interest / 12 / 100
    counter = 1
    while counter < period_month:
        tmp = fix + (credit_sum - fix * (counter - 1)) * i
        res.append(tmp)
        counter += 1
    return res

#функция расчета переплаты по кредиту для аннуитетного платежа
def overpaid(payment, period, credit_sum):
    sum_all = payment * period * 12
    res = sum_all - credit_sum
    return round(res,2)

#функция расчета переплаты по кредиту для аннуитетного платежа
def overpaid_diff(period, credit_sum, interest):
    i = interest / 12 / 100
    period_month = period * 12
    return round((credit_sum * i * (period_month + 1)) / 2,2)

#функция генерации графика платежей с аннуитетной схемой
#общий принцип - генерируем датафрейм с датами платежей
#считаем отдельно в списках:
#остаток долга, 
#ежемесячный платеж,
#процентная часть,
#долговая часть,
#остаток долга на конец периода;
#забиваем это в датафрейм df
#объединяем с датами и выводим с интерфейс

def payment_graphic_ann(start_date, months, payment, interest, credit_sum):
    dates = [(start_date + pd.DateOffset(months=i)).date() for i in range(months)]
    dates = pd.DataFrame(dates, columns=['Дата платежа'])
    debt_ost = []
    payments = []
    payments_interest = []
    payments_main_debt = []
    main_debt = []
    credit_sum_ost = credit_sum
    i = interest / 12 / 100
    for j in range(months):
        debt_ost.append(credit_sum_ost)
        month_interest = credit_sum_ost * i
        main_debt_payment = payment - month_interest
        credit_sum_ost = credit_sum_ost - main_debt_payment

        
        payments.append(round(payment,2))
        payments_interest.append(round(month_interest,2))
        payments_main_debt.append(round(main_debt_payment,2))
        main_debt.append(round(credit_sum_ost,2))


    df = pd.DataFrame({
        'Остаток долга(руб.)': debt_ost,
        'Ежемесячный платеж(руб.)': payments,
        'Процентная часть(руб.)': payments_interest,
        'Долговая часть(руб.)': payments_main_debt,
        'Остаток долга на конец периода(руб.)': main_debt
            })
    df = pd.concat([dates,df], axis = 1)
    df = df.reset_index(drop=True) 
    st.dataframe(df)
#функция генерации графика платежей с дифференцированной схемой
#общий принцип тот же, только не нужно передавать платеж, его можно считать на лету
def payment_graphic_diff(start_date, months, interest, credit_sum):
    dates = [(start_date + pd.DateOffset(months=i)).date() for i in range(months)]
    dates = pd.DataFrame(dates, columns=['Дата платежа'])

    fix = credit_sum / months
    debt_ost = []
    payments = []
    payments_interest = []
    payments_main_debt = []
    main_debt = []
    credit_sum_ost = credit_sum
    i = interest / 12 / 100
    for j in range(months):
        debt_ost.append(credit_sum_ost)
        month_interest = credit_sum_ost * i
        credit_sum_ost = credit_sum_ost - fix
        
        payments.append(round((fix + month_interest),2))
        payments_interest.append(round(month_interest,2))
        payments_main_debt.append(round(fix,2))
        main_debt.append(round(credit_sum_ost,2))


    df = pd.DataFrame({
        'Остаток долга(руб.)': debt_ost,
        'Ежемесячный платеж(руб.)': payments,
        'Процентная часть(руб.)': payments_interest,
        'Долговая часть(руб.)': payments_main_debt,
        'Остаток долга на конец периода(руб.)': main_debt
            })
    df = pd.concat([dates,df], axis = 1)
    df = df.reset_index(drop=True) 
    st.dataframe(df)
    

#чуть расширяем функционал
#делаем одну вкладку интерфейса и функционала по требованию задачи
#вторую с продвинутым интерфейсом и расчетами
#идею продвинутого подсмотрел у банков - конкурентов
#дублирующиеся элементы на разных вкладках имеют уникальные ключи, чтобы избежать ошибок отрисовки
interface_req, interface_adv = st.tabs(['Упрощенный формат', 'Продвинутый интерфейс'])
#Отрисовываем интерфейс.
#Общий принцип:
#- отрисовываем элемент ввода
#- после ввода проверяем на корректность
#-отрисовываем кнопку расчета, при нажатии на которую идет финальная проверка
#и если все успешно, то начинаем расчет
with interface_req:
    st.header("Кредитный калькулятор")
    st.subheader("Параметры для расчета:")

    credit_sum = st.text_input(f'Сумма кредита в рублях')
    if credit_sum:
        st.write(input_check_digit(credit_sum))
    else:
        st.write(':red[Ошибка! Вышли за границы]')

    repayment_period = st.text_input(f'Срок кредита(лет)')
    if repayment_period:
        st.write(input_check_digit(repayment_period))

    interest = st.text_input('Процентная ставка в % годовых')
    if interest:
        st.write(input_check_digit(interest))

    type_payment = st.selectbox('Вид платежа:',
                            ('Аннуитетный', 'Дифференцированный'), key = 'selectbox_calc_tab_req')

    start_date = st.date_input('Выберите дату первого платежа',
                               datetime.date(2026,2,7), key = 'select_date_req')
    if st.button("Рассчитать", key = 'button_calc_tab_req'):
        
        if input_check_all(credit_sum, repayment_period, interest):
            st.subheader('Расчеты:')
            if type_payment == 'Аннуитетный':
                payment = annuitet_payment(int(credit_sum), float(interest), int(repayment_period))
                st.info(f'Ежемесячный платеж: {payment} рублей')
                st.info(f'Переплата за весь срок составит: {overpaid(payment, int(repayment_period), int(credit_sum))} рублей')

                payment_graphic_ann(start_date, (int(repayment_period) * 12), payment, float(interest), int(credit_sum))

                with st.expander("Просмотреть важную информацию:"):
                    st.write('Последний платеж является корректирующим и может быть чуть больше, чем нужно для погашения остатка долга и начисленных процентов')
                    st.write('Неиспользованный остаток останется на Вашем счете погашения')
                    
                
            if type_payment == 'Дифференцированный':
                payments = differ_payment(int(credit_sum), float(interest), int(repayment_period))
                st.info(f'Максимальный платеж: {round(max(payments),2)} рублей')
                st.info(f'Минимальный платеж: {round(min(payments),2)} рублей')
                st.info(f'Средний платеж: {round(statistics.mean(payments),2)} рублей')
                st.info(f'Переплата составит: {round(overpaid_diff(int(repayment_period), int(credit_sum), int(interest)),2)} рублей')
                payment_graphic_diff(start_date, (int(repayment_period) * 12), float(interest), int(credit_sum))

                with st.expander("Просмотреть важную информацию:"):
                    st.write('Последний платеж является корректирующим и может быть чуть больше, чем нужно для погашения остатка долга и начисленных процентов')
                    st.write('Неиспользованный остаток останется на Вашем счете погашения')

                
        else:
            st.subheader(':red[Одно или несколько полей введено неверно]')
            
        #здесь будет функция расчета
#Отрисовываем интерфейс.
#Общий принцип:
#- отрисовываем элемент ввода и подтягиваем параметры
#-отрисовываем кнопку расчета, при нажатии на которую идет расчет   
with interface_adv:
    #параметры для выбора подтягиваем из конфига(файл config.py)
    #хорошо тем, что не нужно звать разработчика каждый раз, когда что - то поменялось и не нужна проверка ввода, если конфиг составлен верно
    st.header("Рассчитайте свой кредит")
    credit_sum = st.slider('Сколько Вам нужно', cnf.credit_from, cnf.credit_to)
    repayment_period = st.slider('На срок(лет)', cnf.repament_period_from,cnf.repayment_period_to)
    category = st.radio(
    "Категория заемщика",
    ["Получаю зарплату на РСХБ", "Я пенсионер", 'Обычный заемщик'],
    index=2, key = 'interface_adv')
    interest = cnf.interest
    type_payment = st.selectbox('Вид платежа:',
                            ('Аннуитетный', 'Дифференцированный'), key = 'selectbox_calc_tab_adv')
    start_date = st.date_input('Выберите дату первого платежа',
                               datetime.date(2026,2,7), key = 'select_date_adv')
    #при нажатии на кнопку 'Рассчитать' срабатывает обработчик и в зависимости от выбранных параметров
    #выбирает ставку и делает расчет
    if st.button("Рассчитать", key = 'button_calc_tab_adv'):
        st.subheader('Расчеты:')
        
        #при аннуитетном платеже
        if type_payment == 'Аннуитетный':
            if category == "Получаю зарплату на РСХБ":
                payment = annuitet_payment(int(credit_sum), float(interest[0]), int(repayment_period))
                st.info(f'Процентная ставка: {interest[0]} %')
                st.info(f'Ежемесячный платеж: {payment} рублей')
                st.info(f'Переплата за весь срок составит: {overpaid(payment, int(repayment_period), int(credit_sum))} рублей')
                payment_graphic_ann(start_date, (int(repayment_period) * 12), payment, float(interest[0]), int(credit_sum))

                with st.expander("Просмотреть важную информацию:"):
                    st.write('Последний платеж является корректирующим и может быть чуть больше, чем нужно для погашения остатка долга и начисленных процентов')
                    st.write('Неиспользованный остаток останется на Вашем счете погашения')
                    
            elif category == "Я пенсионер":
                payment = annuitet_payment(int(credit_sum), float(interest[1]), int(repayment_period))
                st.info(f'Процентная ставка: {interest[1]} %')
                st.info(f'Ежемесячный платеж: {payment} рублей')
                st.info(f'Переплата за весь срок составит: {overpaid(payment, int(repayment_period), int(credit_sum))} рублей')
                payment_graphic_ann(start_date, (int(repayment_period) * 12), payment, float(interest[1]), int(credit_sum))

                with st.expander("Просмотреть важную информацию:"):
                    st.write('Последний платеж является корректирующим и может быть чуть больше, чем нужно для погашения остатка долга и начисленных процентов')
                    st.write('Неиспользованный остаток останется на Вашем счете погашения')
                    
            elif category == "Обычный заемщик":
                payment = annuitet_payment(int(credit_sum), float(interest[2]), int(repayment_period))
                st.info(f'Процентная ставка: {interest[2]} %')
                st.info(f'Ежемесячный платеж: {payment} рублей')
                st.info(f'Переплата за весь срок составит: {overpaid(payment, int(repayment_period), int(credit_sum))} рублей')
                payment_graphic_ann(start_date, (int(repayment_period) * 12), payment, float(interest[2]), int(credit_sum))

                with st.expander("Просмотреть важную информацию:"):
                    st.write('Последний платеж является корректирующим и может быть чуть больше, чем нужно для погашения остатка долга и начисленных процентов')
                    st.write('Неиспользованный остаток останется на Вашем счете погашения')
                    
        #при дифференцированном платеже
        if type_payment == 'Дифференцированный':
            if category == "Получаю зарплату на РСХБ":
                payments = differ_payment(int(credit_sum), float(interest[0]), int(repayment_period))
                st.info(f'Процентная ставка: {interest[0]} %')
                st.info(f'Максимальный платеж: {round(max(payments),2)} рублей')
                st.info(f'Минимальный платеж: {round(min(payments),2)} рублей')
                st.info(f'Средний платеж: {round(statistics.mean(payments),2)} рублей')
                st.info(f'Переплата составит: {round(overpaid_diff(int(repayment_period), int(credit_sum), int(interest[0])),2)} рублей')
                payment_graphic_diff(start_date, (int(repayment_period) * 12), float(interest[0]), int(credit_sum))

                with st.expander("Просмотреть важную информацию:"):
                    st.write('Последний платеж является корректирующим и может быть чуть больше, чем нужно для погашения остатка долга и начисленных процентов')
                    st.write('Неиспользованный остаток останется на Вашем счете погашения')
                    
                
            elif category == "Я пенсионер":
                payments = differ_payment(int(credit_sum), float(interest[1]), int(repayment_period))
                st.info(f'Процентная ставка: {interest[1]} %')
                st.info(f'Максимальный платеж: {round(max(payments),2)} рублей')
                st.info(f'Минимальный платеж: {round(min(payments),2)} рублей')
                st.info(f'Средний платеж: {round(statistics.mean(payments),2)} рублей')
                st.info(f'Переплата составит: {round(overpaid_diff(int(repayment_period), int(credit_sum), int(interest[1])),2)} рублей')
                payment_graphic_diff(start_date, (int(repayment_period) * 12), float(interest[1]), int(credit_sum))

                with st.expander("Просмотреть важную информацию:"):
                    st.write('Последний платеж является корректирующим и может быть чуть больше, чем нужно для погашения остатка долга и начисленных процентов')
                    st.write('Неиспользованный остаток останется на Вашем счете погашения')
                    

            elif category == "Обычный заемщик":
                payments = differ_payment(int(credit_sum), float(interest[2]), int(repayment_period))
                st.info(f'Процентная ставка: {interest[2]} %')
                st.info(f'Максимальный платеж: {round(max(payments),2)} рублей')
                st.info(f'Минимальный платеж: {round(min(payments),2)} рублей')
                st.info(f'Средний платеж: {round(statistics.mean(payments),2)} рублей')
                st.info(f'Переплата составит: {round(overpaid_diff(int(repayment_period), int(credit_sum), int(interest[2])),2)} рублей')
                payment_graphic_diff(start_date, (int(repayment_period) * 12), float(interest[2]), int(credit_sum))

                with st.expander("Просмотреть важную информацию:"):
                    st.write('Последний платеж является корректирующим и может быть чуть больше, чем нужно для погашения остатка долга и начисленных процентов')
                    st.write('Неиспользованный остаток останется на Вашем счете погашения')
                    


