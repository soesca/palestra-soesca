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
        # Usa os Secrets do Streamlit
        creds_dict = dict(st.secrets["google_sheets"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, escopo)
        cliente = gspread.authorize(creds)
        ID_PLANILHA = "1NHL4ihthnYOe_xDOGTmfLQ-I5FuyomWdTkkQbLRKKNs"
        planilha = cliente.open_by_key(ID_PLANILHA).sheet1
        
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        planilha.append_row([nome, qtd, data_hora, f"R$ {total:.2f}"])
        return True
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return False

# --- INTERFACE VISUAL (Estilo WhatsApp) ---
st.set_page_config(page_title="Inscrição SOESCA", page_icon="🎟️")

st.markdown("# 🎟️ Inscrição: Palestra Técnica")
st.markdown("### SOESCA - Pernambuco")
st.divider()

# Exibição de Valor e Vagas lado a lado
col1, col2 = st.columns(2)
with col1:
    st.write("Valor do Ingresso")
    st.markdown("## R$ 50,00")
with col2:
    st.write("Vagas Totais")
    st.markdown("## 140")

# Formulário com borda
with st.container(border=True):
    nome = st.text_input("Digite seu nome completo:")
    qtd = st.number_input("Quantos ingressos deseja?", min_value=1, max_value=10, value=1)
    
    if st.button("Confirmar e Gerar Pix", use_container_width=True):
        if nome:
            total = qtd * 50.00
            if salvar_na_planilha(nome, qtd, total):
                st.success("✅ Inscrição registrada com sucesso!")
                st.write(f"### Total a pagar: R$ {total:.2f}")
                
                # Gera QR Code para o pagamento
                img_qr = qrcode.make(f"PIX SOESCA;VALOR:{total};NOME:{nome}")
                buf = BytesIO()
                img_qr.save(buf, format="PNG")
                st.image(buf, caption="Aponte a câmera do banco para o QR Code", width=250)
        else:
            st.warning("⚠️ Por favor, digite seu nome.")
