import streamlit as st
import qrcode
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO
from datetime import datetime

# --- CONFIGURAÇÃO DO GOOGLE SHEETS (SEM ARQUIVO JSON) ---
def salvar_na_planilha(nome, qtd, total):
    try:
        escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Lendo segredos individuais para evitar erros de Base64
        info = {
            "type": st.secrets["type"],
            "project_id": st.secrets["project_id"],
            "private_key_id": st.secrets["private_key_id"],
            "private_key": st.secrets["private_key"].replace("\\n", "\n"),
            "client_email": st.secrets["client_email"],
            "client_id": st.secrets["client_id"],
            "auth_uri": st.secrets["auth_uri"],
            "token_uri": st.secrets["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["client_x509_cert_url"]
        }
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, escopo)
        cliente = gspread.authorize(creds)
        ID_PLANILHA = "1NHL4ihthnYOe_xDOGTmfLQ-I5FuyomWdTkkQbLRKKNs"
        planilha = cliente.open_by_key(ID_PLANILHA).sheet1
        
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        planilha.append_row([nome, qtd, data_hora, f"R$ {total:.2f}"])
        return True
    except Exception as e:
        st.error(f"Erro técnico: {e}")
        return False

# --- FUNÇÃO PIX ---
def gerar_payload_pix(valor, nome_recebedor, cidade_recebedor, chave_pix):
    valor_str = f"{valor:.2f}"
    payload = f"00020126330014BR.GOV.BCB.PIX0111{chave_pix}5204000053039865405{valor_str}5802BR59{len(nome_recebedor):02}{nome_recebedor}60{len(cidade_recebedor):02}{cidade_recebedor}62070503***6304"
    return payload

# --- INTERFACE ---
st.set_page_config(page_title="Inscrição SOESCA", page_icon="🎟️")
st.markdown("# 🎟️ Inscrição: Palestra SOESCA")
st.markdown("### SOESCA - Pernambuco")
st.divider()

with st.container(border=True):
    nome = st.text_input("Digite seu nome completo:")
    qtd = st.number_input("Quantos ingressos deseja?", min_value=1, max_value=10, value=1)
    
    if st.button("Confirmar e Gerar Pix", use_container_width=True):
        if nome:
            total = qtd * 50.00
            if salvar_na_planilha(nome, qtd, total):
                st.success("✅ Inscrição registrada!")
                chave_celular = "81988037205"
                payload = gerar_payload_pix(total, "JOAO FELIPE SILVA", "CABO", chave_celular)
                
                qr = qrcode.QRCode(box_size=10, border=2)
                qr.add_data(payload)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                
                buf = BytesIO()
                img.save(buf, format="PNG")
                st.image(buf, caption="Escaneie para pagar via Pix")
                st.code(payload, language="text")
        else:
            st.warning("⚠️ Digite seu nome.")
