import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date


con = sqlite3.connect('base.db', check_same_thread = False)
db = con.cursor()

st.markdown("<p style='font-size:13px;border:2px solid;padding:12px;border-radius: 30px;'>Felipe Wendling Heidenfelder - Case Kinea - 01/10/2022</p>", unsafe_allow_html=True)
st.markdown("<div style='font-size: 30px;'>Descrição:</div> <p>Mini sistema de alimentação de dados para um banco de dados SQL a partir de consultas realizadas pelo usuário.</p>", unsafe_allow_html=True)

st.markdown("###")
st.markdown("- Frontend: <u>Streamlit</u>\n - Backend: <u>API</u>\n - Banco de dados: <u>SQLite3</u>\n- Deploy: <u>Heroku</u>", unsafe_allow_html=True)
st.markdown("#")
def form():
  
    st.title("Formulário de consulta por data")
    
    with st.form(key = "include_date"):
        #Input date 
        input_date = st.date_input(label="Digite a data de consulta: ", max_value=pd.Timestamp(date.today().strftime("%Y-%m-%d")), min_value=pd.Timestamp("1984-12-03"))
        
        #Botões
        consulta = st.form_submit_button("Consultar dólar")
        exibir_sql = st.form_submit_button("Exibir base de dados (SQL)")
        
        remover = st.form_submit_button("Limpar base de dados")
        senha = st.text_input("Digite a senha para apagar a base de dados: ", max_chars=3)    
        
    if consulta:
        consultar_e_exibir(input_date)
            
    if remover:
        teste(senha)
        
    if exibir_sql:
       exibe_sql()
 
def teste(senha):
    if senha == "adm": 
        st.success("Parabéns! Você acertou a senha!")
        st.balloons()
        remove()
    else: st.warning("Senha errada! Tente novamente quando descobrir como funciona o código", icon="⚠️")
            
def remove():
    db.execute("DELETE FROM base;")
    con.commit()
    con.close()
    st.error("Todos os dados foram apagados!")
    
def add(data, dol):
    if dol != 0:
       
        db.execute("INSERT INTO base VALUES (?,?)", (data, dol))
        con.commit()
    
    st.success("Dados adicionados com sucesso!")
    st.markdown('#', unsafe_allow_html=True)    
    
def dolar_bcb(data):
    url = f"https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='{data}'&$top=10&$skip=0&$format=json"
    try:
        dic =  pd.read_json(url)["value"].iloc[0]
        compra, venda, data = [list(dic.values())[i] for i in (0,1,2)]
        st.title("Dados da API do Banco Central")
        st.write("- Data encontrada: ", str(data).split(" ")[0], "\n- dol compra: ", round(compra,4),"\n- dol venda: ", round(venda,4))
        media_dolar_dia = (compra+venda)/2
        
        if media_dolar_dia != float('nan'):
            return round(media_dolar_dia,4)
    except: 
        st.warning("Hoje não é um dia útil... Tente outra data!")
        return 0
    
def consultar_e_exibir(data):
    sql_query = pd.read_sql('SELECT * from base', con)
    df = pd.DataFrame(sql_query, columns = ["Data", "Dolar"])
    
    #st.write("Data digitada: ",data)
    data_usuario = datetime.strftime(data, '%d/%m/%Y')
    data_bcb = datetime.strftime(data, '%m-%d-%Y')
    
    # ------- Confere na base de dados se o valor
    if data_bcb in df["Data"].values:
        dol = df[df['Data'] == data_bcb]["Dolar"].iloc[0]
        st.success("Registro encontrado na base de dados!")
        #st.markdown('#') 
        
        st.markdown(f"<h4>O dólar do dia </mark>{data_usuario} é: </h4>",unsafe_allow_html=True)
        st.markdown(f"<h1>R${str(dol).replace('.',',')}</h1>", unsafe_allow_html=True)
    else: 
        st.warning("Não possui registro na base de dados!\n Buscando na API...")
        dol= dolar_bcb(data_bcb)
        
        if dol != 0:
            add(data_bcb, dol)
            
            st.markdown(f"<h3>O dólar do dia {data_usuario} é: </h3>",unsafe_allow_html=True)
            st.markdown(f"<h1>R${str(dol).replace('.',',')}</h1>", unsafe_allow_html=True)

def exibe_sql():
    sql_query = pd.read_sql('SELECT * from base', con)
    df = pd.DataFrame(sql_query, columns = ["Data", "Dolar"])
    st.write(df)
    
form()
         