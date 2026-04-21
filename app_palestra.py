import streamlit as st
import qrcode
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO
from datetime import datetime

# --- CONFIGURAÇÃO DO GOOGLE SHEETS ---
def salvar_na_planilha(nome, qtd, total):
    try:
        # Define o escopo e as credenciais
        escopo = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # O arquivo deve estar na mesma pasta com este nome exato:
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', escopo)
        cliente = gspread.authorize(creds)
        
        # Abre a planilha pelo ID que pegamos da sua URL
        ID_PLANILHA = "1NHL4ihthnYOe_xDOGTmfLQ-I5FuyomWdTkkQbLRKKNs"
        planilha = cliente.open_by_key(ID_PLANILHA).sheet1
        
        # Prepara a linha para inserir
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        planilha.append_row([nome, qtd, agora, total])
        return True
    except Exception as e:
        st.error(f"Erro técnico ao salvar: {e}")
        return False

# --- INTERFACE VISUAL ---
st.set_page_config(page_title="Inscrição Palestra SOESCA", page_icon="🎟️")

st.title("🎟️ Inscrição: Palestra Técnica")
st.markdown("### SOESCA - Pernambuco")
st.write("---")

# Informações fixas na tela
col1, col2 = st.columns(2)
col1.metric("Valor do Ingresso", "R$ 50,00")
col2.metric("Vagas Totais", "140")

with st.form("venda_form"):
    nome_comprador = st.text_input("Digite seu nome completo:")
    quantidade = st.number_input("Quantos ingressos deseja?", min_value=1, max_value=10, value=1)
    botao_enviar = st.form_submit_button("Confirmar e Gerar Pix")

if botao_enviar:
    if nome_comprador.strip() != "":
        valor_total = quantidade * 50.00
        
        # Tenta salvar na planilha
        with st.spinner('Processando sua inscrição...'):
            if salvar_na_planilha(nome_comprador, quantidade, valor_total):
                st.success(f"Excelente, {nome_comprador}! Sua reserva foi salva na planilha.")
                
                # Exibe o QR Code
                st.write(f"### Total a pagar: R$ {valor_total:.2f}")
                
                # Aqui você pode colocar sua chave PIX real no lugar do texto abaixo
                texto_pix = f"Chave: seu-email@exemplo.com\nValor: R${valor_total}\nNome: {nome_comprador}"
                qr = qrcode.make(texto_pix)
                
                buf = BytesIO()
                qr.save(buf, format="PNG")
                st.image(buf, caption="Aponte o app do seu banco para este QR Code", width=300)
                
                st.warning("⚠️ Após o pagamento, o comprovante deve ser apresentado na entrada.")
    else:
        st.error("Por favor, informe seu nome para continuar.")