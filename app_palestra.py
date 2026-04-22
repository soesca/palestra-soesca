import streamlit as st
import qrcode
from io import BytesIO

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

            # 🔑 COLE AQUI SEU PIX COPIA E COLA (GERADO NO BANCO)
            pix_copia_cola = "00020126360014br.gov.bcb.pix0114+558199818099152040000530398654041.005802BR5911FELIPE NETO6009Sao Paulo62230519daqr25819193077360763041A36"

            qr = qrcode.make(pix_copia_cola)

            buf = BytesIO()
            qr.save(buf)
            buf.seek(0)

            st.success("PIX gerado com sucesso!")

            st.write("### Escaneie para pagar via Pix")
            st.image(buf, caption=f"{nome} - Total: R$ {total:.2f}")

            st.markdown("---")
            st.code(pix_copia_cola)

            st.info("💡 Após o pagamento, envie o comprovante para confirmação da inscrição.")

        else:
            st.warning("⚠️ Por favor, digite seu nome.")