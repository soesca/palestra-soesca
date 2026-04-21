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

# --- FUNÇÃO PIX COPIA E COLA ---
def gerar_payload_pix(valor, nome_recebedor, cidade_recebedor, chave_pix):
    valor_str = f"{valor:.2f}"
    # Payload simplificado para Pix Estático
    payload = f"00020126330014BR.GOV.BCB.PIX0111{chave_pix}5204000053039865405{valor_str}5802BR59{len(nome_recebedor):02}{nome_recebedor}60{len(cidade_recebedor):02}{cidade_recebedor}62070503***6304"
    return payload

# --- INTERFACE ---
st.set_page_config(page_title="Inscrição SOESCA", page_icon="🎟️")
st.markdown("# 🎟️ Ingresso: Palestra SOESCA")
st.markdown("### SOESCA - Cabo de Santo Agostinho")
st.divider()

col1, col2 = st.columns(2)
col1.metric("Valor do Ingresso", "R$ 50,00")
col2.metric("Vagas Totais", "140")

with st.container(border=True):
    nome = st.text_input("Digite seu nome completo:")
    qtd = st.number_input("Quantos ingressos deseja?", min_value=1, max_value=10, value=1)
    
    if st.button("Confirmar e Gerar Pix", use_container_width=True):
        if nome:
            total = qtd * 50.00
            if salvar_na_planilha(nome, qtd, total):
                st.success("✅ Inscrição registrada!")
                
                # Dados para o seu Pix
                chave_celular = "81988037205"
                payload = gerar_payload_pix(total, "JOAO FELIPE SILVA", "CABO", chave_celular)
                
                st.write(f"### Total: R$ {total:.2f}")
                
                # Gerar QR Code
                qr = qrcode.QRCode(box_size=10, border=2)
                qr.add_data(payload)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                
                buf = BytesIO()
                img.save(buf, format="PNG")
                st.image(buf, caption="Aponte o app do Banco para pagar")
                st.code(payload, language="text") # Opção Copia e Cola
                st.info("Após pagar, envie o comprovante para o instrutor.")
        else:
            st.warning("⚠️ Digite seu nome.")
