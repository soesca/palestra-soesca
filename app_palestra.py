import streamlit as st
import mercadopago
import base64
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 🔐 TOKEN MERCADO PAGO (coloque no secrets depois)
ACCESS_TOKEN = st.secrets["mercado_pago"]["access_token"]

sdk = mercadopago.SDK(ACCESS_TOKEN)

# ---------------- GOOGLE SHEETS ----------------
def salvar_na_planilha(nome, qtd, total):
    try:
        escopo = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        info = json.loads(st.secrets["google_sheets"]["json_key"])

        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, escopo)
        cliente = gspread.authorize(creds)

        planilha = cliente.open_by_key("1NHL4ihthnYOe_xDOGTmfLQ-I5FuyomWdTkkQbLRKKNs").sheet1

        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        planilha.append_row([nome, qtd, data_hora, f"R$ {total:.2f}"])

        return True

    except Exception as e:
        st.error(f"Erro ao salvar na planilha: {e}")
        return False


# ---------------- INTERFACE ----------------
st.set_page_config(page_title="Inscrição SOESCA", page_icon="🎟️")

st.title("🎟️ Inscrição: Palestra SOESCA")
st.subheader("SOESCA - Cabo de Santo Agostinho")
st.divider()

with st.container(border=True):

    nome = st.text_input("Digite seu nome completo:")
    qtd = st.number_input("Quantos ingressos deseja?", min_value=1, max_value=140, value=1)

    if st.button("Confirmar e Gerar Pix", use_container_width=True):

        if nome:

            total = qtd * 50.00

            # 🔥 CRIA PAGAMENTO PIX REAL
            import qrcode
            from io import BytesIO

            # 🔑 COLE SEU PIX AQUI (copia e cola do banco)
            pix_copia_cola = "00020126360014br.gov.bcb.pix0114+558199818099152040000530398654041.005802BR5911FELIPE NETO6009Sao Paulo62230519daqr25819193077360763041A36"  # <-- aqui entra o código REAL

            qr = qrcode.make(pix_copia_cola)

            buf = BytesIO()
            qr.save(buf)
            buf.seek(0)  # 👈 IMPORTANTE

            st.success("PIX gerado com sucesso!")

            st.write("### Escaneie para pagar via Pix")
            st.image(buf)

            st.markdown("---")
            st.code(pix_copia_cola)

            # 💾 SALVA ID NA SESSÃO
            st.session_state["payment_id"] = payment_id
            st.session_state["nome"] = nome
            st.session_state["qtd"] = qtd
            st.session_state["total"] = total

            st.success("PIX gerado com sucesso!")

            st.write("### Escaneie para pagar via Pix")
            st.image(base64.b64decode(qr_base64))
            st.code(qr_code)

        else:
            st.warning("Digite seu nome.")

# ---------------- VALIDAR PAGAMENTO ----------------

if "payment_id" in st.session_state:

    if st.button("Já paguei, verificar pagamento"):

        payment_id = st.session_state["payment_id"]

        status = sdk.payment().get(payment_id)["response"]["status"]

        if status == "approved":

            st.success("✅ Pagamento confirmado!")

            salvar_na_planilha(
                st.session_state["nome"],
                st.session_state["qtd"],
                st.session_state["total"]
            )

            st.balloons()

        else:
            st.warning(f"Pagamento ainda não confirmado. Status: {status}")