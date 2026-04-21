import streamlit as st
import qrcode
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO
import requests
from datetime import datetime

# --- CONFIGURAÇÃO DA LOGO NO FORMULÁRIO ---
# URL da sua logo no GitHub (A imagem deve estar no mesmo repositório do código)
# Substitua 'soesca' pelo seu usuário e 'palestra_soesca' pelo nome do seu repositório
URL_LOGO_GITHUB = "https://raw.githubusercontent.com/soesca/palestra_soesca/main/logo.png"

def carregar_logo():
    try:
        response = requests.get(URL_LOGO_GITHUB)
        image_bytes = BytesIO(response.content)
        return image_bytes
    except Exception as e:
        # Se der erro na logo, o app continua sem a imagem
        st.warning("⚠️ Não foi possível carregar a logo.")
        return None

# --- CONFIGURAÇÃO DO GOOGLE SHEETS COM SANITIZAÇÃO DE CHAVE ---
def salvar_na_planilha(nome, qtd, total):
    try:
        escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # Lendo segredos individuais e sanitizando o Base64 (\n -> quebra de linha real)
        info = {
            "type": st.secrets["google_sheets"]["type"],
            "project_id": st.secrets["google_sheets"]["project_id"],
            "private_key_id": st.secrets["google_sheets"]["private_key_id"],
            "private_key": st.secrets["google_sheets"]["private_key"].replace("\\n", "\n"),
            "client_email": st.secrets["google_sheets"]["client_email"],
            "client_id": st.secrets["google_sheets"]["client_id"],
            "auth_uri": st.secrets["google_sheets"]["auth_uri"],
            "token_uri": st.secrets["google_sheets"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["google_sheets"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["google_sheets"]["client_x509_cert_url"]
        }
        
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, escopo)
        cliente = gspread.authorize(creds)
        ID_PLANILHA = "1NHL4ihthnYOe_xDOGTmfLQ-I5FuyomWdTkkQbLRKKNs"
        planilha = cliente.open_by_key(ID_PLANILHA).sheet1
        
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        planilha.append_row([nome, qtd, data_hora, f"R$ {total:.2f}"])
        return True
    except Exception as e:
        # Se der erro de Base64, vai aparecer aqui
        st.error(f"Erro técnico: {e}")
        return False

# --- FUNÇÃO PIX PARA GERAR O PAYLOAD ---
def gerar_payload_pix(valor, nome_recebedor, cidade_recebedor, chave_pix):
    valor_str = f"{valor:.2f}"
    # Payload estático Pix para QR Code
    payload = f"00020126330014BR.GOV.BCB.PIX0111{chave_pix}5204000053039865405{valor_str}5802BR59{len(nome_recebedor):02}{nome_recebedor}60{len(cidade_recebedor):02}{cidade_recebedor}62070503***6304"
    return payload

# --- INTERFACE ---
st.set_page_config(page_title="Inscrição SOESCA", page_icon="🎟️")

# --- CONFIGURAÇÃO DA LOGO ---
def carregar_logo():
    try:
        # Tenta carregar o arquivo local chamado 'logo.png'
        with open("logo.png", "rb") as f:
            return f.read()
    except:
        return None

# No corpo do código:
logo_data = carregar_logo()
if logo_data:
    st.image(logo_data, width=200)

st.markdown("# 🎟️ Inscrição: Palestra SOESCA")
st.markdown("### SOESCA - Cabo de Santo Agostinho")
st.divider()

with st.container(border=True):
    nome = st.text_input("Digite seu nome completo:")
    qtd = st.number_input("Quantos ingressos deseja?", min_value=1, max_value=140, value=1)
    
    if st.button("Confirmar e Gerar Pix", use_container_width=True):
        if nome:
            total = qtd * 50.00
            # Tenta salvar na planilha antes de mostrar o Pix
            if salvar_na_planilha(nome, qtd, total):
                st.success("✅ Inscrição registrada com sucesso na planilha!")
                
                chave_celular = "81988037205"
                payload = gerar_payload_pix(total, "JOAO FELIPE SILVA", "CABO", chave_celular)
                
                qr = qrcode.QRCode(box_size=10, border=2)
                qr.add_data(payload)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                
                buf = BytesIO()
                img.save(buf, format="PNG")
                
                st.write("### Escaneie para pagar via Pix")
                st.image(buf, caption=f"Pix para {nome} - Valor Total: R$ {total:.2f}")
                
                st.markdown("---")
                st.code(payload, language="text")
                st.info("💡 Após escanear, confirme o valor de R$ 50,00 por ingresso e o nome JOAO FELIPE SILVA no seu app de banco.")
        else:
            st.warning("⚠️ Por favor, digite seu nome.")
