import streamlit as st
import qrcode
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO
from datetime import datetime

# --- CONFIGURAÇÃO DO GOOGLE SHEETS ---
def salvar_na_planilha(nome, qtd, total):
    try:
        escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # MUDANÇA REAL: Lê dos Secrets do Streamlit em vez do arquivo local
        if "google_sheets" in st.secrets:
            creds_info = st.secrets["google_sheets"]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_info), escopo)
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', escopo)
            
        cliente = gspread.authorize(creds)
        ID_PLANILHA = "1NHL4ihthnYOe_xDOGTmfLQ-I5FuyomWdTkkQbLRKKNs"
        planilha = cliente.open_by_key(ID_PLANILHA).sheet1
        
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        planilha.append_row([nome, qtd, data_hora, str(total)])
        return True
    except Exception as e:
        st.error(f"Erro técnico: {e}")
        return False

# --- INTERFACE ---
st.set_page_config(page_title="Inscrição Palestra SOESCA", page_icon="🎟️")
st.title("🎟️ Inscrição: Palestra Técnica")
st.markdown("### SOESCA - Pernambuco")

with st.form("venda"):
    nome = st.text_input("Nome Completo:")
    qtd = st.number_input("Quantidade de ingressos:", min_value=1, max_value=10, value=1)
    submit = st.form_submit_button("Gerar Pagamento Pix")

if submit:
    if nome:
        total = qtd * 50.00
        with st.spinner('Processando...'):
            if salvar_na_planilha(nome, qtd, total):
                st.success("Inscrição registrada!")
                st.write(f"### Total: R$ {total:.2f}")
                img_qr = qrcode.make(f"Pix Palestra SOESCA - {nome} - R${total}")
                buf = BytesIO()
                img_qr.save(buf, format="PNG")
                st.image(buf, width=300)
    else:
        st.error("Preencha seu nome.")
