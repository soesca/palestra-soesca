import streamlit as st
import qrcode
from io import BytesIO
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(page_title="Inscrição SOESCA", page_icon="🎟️")

# ---------------- LOGO ----------------
logo = "logo.png"
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image(logo, width=180)

st.title("🎟️ Inscrição: Palestra SOESCA")
st.subheader("SOESCA - Cabo de Santo Agostinho")
st.divider()

# ---------------- GOOGLE SHEETS ----------------
def salvar_na_planilha(nome, qtd, total):
    try:
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

        planilha = cliente.open_by_key("1NHL4ihthnYOe_xDOGTmfLQ-I5FuyomWdTkkQbLRKKNs").sheet1

        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        planilha.append_row([nome, qtd, data_hora, f"R$ {total:.2f}"])

        return True

    except Exception as e:
        st.error(f"Erro ao salvar na planilha: {e}")
        return False


# ---------------- FORMULÁRIO ----------------
with st.container(border=True):

    nome = st.text_input("Digite seu nome completo:")
    qtd = st.number_input("Quantos ingressos deseja?", min_value=1, max_value=140, value=1)

    if st.button("Confirmar e Gerar Pix", use_container_width=True):

        if nome:

            total = qtd * 50.00

            # 🔑 COLE SEU PIX REAL AQUI
            pix_copia_cola = "COLE_AQUI_SEU_PIX_REAL"

            qr = qrcode.make(pix_copia_cola)

            buf = BytesIO()
            qr.save(buf)
            buf.seek(0)

            st.success("PIX gerado com sucesso!")

            st.write("### Escaneie para pagar via Pix")
            st.image(buf, caption=f"{nome} - Total: R$ {total:.2f}")

            st.markdown("### 📋 Copiar código PIX")
            st.text_area("", pix_copia_cola, height=120)

            st.info("👉 Segure o código acima e copie no seu banco.")
            st.info("💡 Após o pagamento, clique em 'Já paguei' abaixo.")

            # salva dados
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
                st.success("✅ Pagamento confirmado e salvo na planilha!")
                st.balloons()
                st.session_state["pagamento_pendente"] = False

        else:
            st.error("❌ Senha incorreta")