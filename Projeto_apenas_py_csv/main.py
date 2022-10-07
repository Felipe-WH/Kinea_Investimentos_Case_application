from tkinter import *
from tkinter import ttk
from tkcalendar import Calendar
import pandas as pd
from datetime import datetime
import statistics as st
import os.path

# ----------- BASE DE DADOS -------------------------------------------------
base = "Cotacao_historica_df.csv"

if os.path.isfile(base):
    print("Existe")
else:
    print("Não existe base, criando...")
    df = pd.DataFrame(columns = ["Data","Dólar"])
    df.to_csv("Cotacao_historica_df.csv")
# ------------------------------------------------------------
    
# Função 1 - Extrair o dólar da API do Banco Central a partir de uma data selecioanda pelo usuário    
    
def dolar_bcb(data):
    url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='{data}'&$top=10&$skip=0&$format=json"
    try:
        dic =  pd.read_json(url)["value"].iloc[0]
        compra, venda, data = [list(dic.values())[i] for i in (0,1,2)]
        media_dolar_dia = st.mean([compra, venda])
        
        print(f"Cotação média: {media_dolar_dia}")
        return media_dolar_dia
    except: 
        print("Hoje não é um dia útil!")
      
#Função 2 - Confere se a data já está armazenada no banco de dados e, caso não, chama a função dolar_bcb com a 
# data selecioanda no calendário, e retorna o dólar da api. Com a data e dólar novos, esses dados são salvos na 
# base de dados e retornada ao usuário  
  
def confere_e_armazena(e=""):
    df = pd.read_csv("Cotacao_historica_df.csv")
    df = df[df.filter(regex='^(?!Unnamed)').columns]
    
    data_usuario = str(cal.get_date())
    data_usuario = datetime.strptime(data_usuario, '%d/%m/%Y').strftime('%m-%d-%Y')
    
    if data_usuario in df["Data"].values:
        print(df[df["Data"] == data_usuario])
        Label(window, text = f"Data: {data_usuario}  Dólar: R${round(df['Dólar'][df['Data']== data_usuario].iloc[0],4)}",
              font=('Arial 12')).grid(row=9,column =0)
        
    else:
        try:
            dolar= dolar_bcb(data_usuario) 
            print(data_usuario, dolar)
            
            new = pd.DataFrame([[data_usuario,round(dolar,4)]], columns = ["Data", "Dólar"])   
            df = df.append(new)
            
            Label(window, text = f"Data: {data_usuario}  Dólar: R${round(dolar,4)}", font=('Arial 12')).grid(row=9,column =0)   
            
            df.to_csv("Cotacao_historica_df.csv")    
        except:
            Label(window, text = "                            ",  font=('Arial 28')).grid(row=9,column =0)
            Label(window, text = "Não é um dia útil / Feriado", font=('Arial 10')).grid(row=9,column =0)
 

# -------- TKINTER -------------------------------------------      
window = Tk()
window.geometry("500x350")

Label(window, text = "Digite a data de consulta: ").grid(row=6, column=0)

# Calendário
cal = Calendar(window, selectmode = 'day',
               year = 2020, month = 5,
               day = 22)
cal.grid(row =4)
# ------------------------------------------------------------

# Botão de enviar consulta
ttk.Button(window, text = "Consultar dólar", command= confere_e_armazena).grid(row=8, column = 0)

Label(window, text= "Selecione a data no calendário e clique em consultar ou ENTER",
      font= ('Arial 12')).grid(row=0, column=0)
window.bind('<Return>', confere_e_armazena)

window.mainloop()

