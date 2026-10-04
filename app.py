import streamlit as st
import tempfile
import os
from main import leitura_documentos, banco_vetorial, resposta_chat

# =========================
# CONFIGURAÇÃO
# =========================

st.set_page_config(
    page_title = "Assistente Inteligênte de Documentos",
    page_icon = "🤖",
    layout = "centered"
)

st.markdown("""
<style>

.block-container {
    max-width: 1000px;
    padding-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

st.title("Geração Aumentada por Recuperação")
st.caption("Assistente Inteligênte de Documentos")


# =========================
# MEMÓRIA DO CHAT
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# UPLOAD E PROCESSAMENTO DE DOCUMENTOS
# =========================

documentos = st.file_uploader("📎 Envie seus documentos", type = ["pdf", "docx", "txt", "csv"], accept_multiple_files = True)
if documentos:
    with st.spinner('📚 Carregando e processando seus documentos...'):

        arquivos = []
        for documento in documentos:
            arquivo_temp = tempfile.NamedTemporaryFile(delete = False, suffix = '.pdf')
            arquivo_temp.write(documento.getvalue())
            arquivos.append(arquivo_temp.name)

        doc = leitura_documentos(arquivos)
        banco = banco_vetorial(doc)
        #GUARDAR O BANCO NA MEMÓRIA DO STREAMLIT
        st.session_state.banco = banco
    st.success('✅ Documentos carregados com sucesso')

# =========================
# MOSTRAR DOCUMENTOS
# =========================

    if documentos:
        st.sidebar.subheader("📚 Documentos")
        for documento in documentos:
            st.sidebar.write(f"📄 {documento.name}")

# =========================
# HISTÓRICO DO CHAT
# =========================

user_avatar = os.path.join('user.jpg')
system_avatar = os.path.join('i1046861.jpeg')

for message in st.session_state.messages:
    if message['role'] == 'user':
        with st.chat_message('user', avatar = user_avatar):
            st.markdown(message["content"])
    else:
        with st.chat_message('assistant', avatar = system_avatar):
            st.markdown(message['content'])

# =========================
# INPUT E PROCESSAMENTO DO CHAT
# =========================

prompt = st.chat_input("Digite sua mensagem...")
if prompt:
    # Mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar = user_avatar):
        st.markdown(prompt)

    # resposta da IA
    if 'banco' not in st.session_state:
        resposta = '📎 Primeiro envie pelo menos um documento.'

        with st.chat_message('assistant', avatar = system_avatar):
            st.markdown(resposta)

    else:
        with st.chat_message('assistant'):
            resposta = st.write_stream(resposta_chat(prompt, st.session_state.banco))

    # Salvar resposta
    st.session_state.messages.append({
        "role": "assistant",
        "content": resposta
    })
