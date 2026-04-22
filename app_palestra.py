import streamlit as st
import qrcode
from io import BytesIO
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(page_title="Inscrição SOESCA", page_icon="🎟️")

# ---------------- CONFIG ----------------
TOTAL_INGRESSOS = 140

# ---------------- LOGO ----------------
logo = "logo.png"
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image(logo, width=180)

st.title("🎟️ Inscrição: Palestra SOESCA")
st.subheader("SOESCA - Cabo de Santo Agostinho")
st.divider()

# ---------------- GOOGLE SHEETS ----------------
def conectar_planilha():
    escopo = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

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

    return cliente.open_by_key("1NHL4ihthnYOe_xDOGTmfLQ-I5FuyomWdTkkQbLRKKNs").sheet1


def contar_inscritos():
    try:
        planilha = conectar_planilha()
        dados = planilha.get_all_records()
        total = sum(int(linha["Quantidade"]) for linha in dados)
        return total
    except:
        return 0


def salvar_na_planilha(nome, qtd, total):
    try:
        planilha = conectar_planilha()
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        planilha.append_row([nome, qtd, data_hora, f"R$ {total:.2f}"])
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False


# ---------------- CONTADOR ----------------
vendidos = contar_inscritos()
restantes = TOTAL_INGRESSOS - vendidos

if restantes <= 0:
    st.error("❌ Ingressos esgotados!")
    st.stop()

st.info(f"🎟️ Restam {restantes} ingressos disponíveis")

# ---------------- FORMULÁRIO ----------------
with st.container(border=True):

    nome = st.text_input("Digite seu nome completo:")
    qtd = st.number_input("Quantos ingressos deseja?", min_value=1, max_value=restantes, value=1)

    if st.button("Confirmar e Gerar Pix", use_container_width=True):

        if nome:

            total = qtd * 50.00

            # 🔑 COLE SEU PIX REAL AQUI
            pix_copia_cola = "00020126360014br.gov.bcb.pix0114+558199818099152040000530398654041.005802BR5911FELIPE NETO6009Sao Paulo62230519daqr25819193077360763041A36"

            qr = qrcode.make(pix_copia_cola)

            buf = BytesIO()
            qr.save(buf)
            buf.seek(0)

            st.success("PIX gerado com sucesso!")

            st.write("### Escaneie para pagar via Pix")
            st.image(buf, caption=f"{nome} - Total: R$ {total:.2f}")

            # 🔥 BOTÃO COPIAR PROFISSIONAL
            st.markdown("### 📋 Copiar código PIX")

            st.markdown(f"""
            <input type="text" value="{pix_copia_cola}" id="pixCode" style="width:100%; padding:10px; font-size:14px;" readonly>
            <button onclick="navigator.clipboard.writeText(document.getElementById('pixCode').value)" 
            style="margin-top:10px; padding:12px; background-color:#16a34a; color:white; border:none; border-radius:6px; width:100%; font-size:16px;">
            📋 Copiar código PIX
            </button>
            """, unsafe_allow_html=True)

            st.info("💡 Após o pagamento, clique em 'Já paguei' abaixo.")

            st.session_state["nome"] = nome
            st.session_state["qtd"] = qtd
            st.session_state["total"] = total

        else:
            st.warning("⚠️ Por favor, digite seu nome.")

# ---------------- BOTÃO CLIENTE ----------------
if st.button("Já paguei"):
    st.warning("Aguardando confirmação do administrador...")
    st.session_state["pagamento_pendente"] = True


# ---------------- ADMIN ----------------
if st.session_state.get("pagamento_pendente"):

    st.markdown("### 🔐 Confirmação do administrador")

    senha = st.text_input("Digite a senha:", type="password")

    if st.button("Confirmar pagamento"):

        if senha == "soesca2026":

            if salvar_na_planilha(
                st.session_state["nome"],
                st.session_state["qtd"],
                st.session_state["total"]
            ):
                st.success("✅ Pagamento confirmado!")
                st.balloons()
                st.session_state["pagamento_pendente"] = False

        else:
            st.error("❌ Senha incorreta")