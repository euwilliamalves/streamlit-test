from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()

key = os.getenv('OPENAI_KEY')

if not key:
    key = st.secrets['OPENAI_KEY']

def leitura_documentos(documento):
    paginas = []
    for doc, nome_original in documento:
        loader = PyPDFLoader(doc)
        doc = loader.load()

        for doc in docs:
            doc.metadata['source'] = nome_original

        paginas.extend(docs)
    chunk = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 100, separators = ['\n\n', '\n', ',', '.', ''])
    separado = chunk.split_documents(paginas)
        
    return separado

def banco_vetorial(documento):
    if not documento:
        raise ValueError('Nenhum documento foi encontrado neste banco.')
    
    embed = OpenAIEmbeddings(model = 'text-embedding-3-small', api_key = key)
    vectorstore = FAISS.from_documents(documents = documento, embedding = embed)
    retriever = vectorstore.as_retriever(search_kwargs = {'k': 3}, search_type = 'mmr')

    return retriever

def resposta_chat(entrada, banco):
    llm = ChatOpenAI(model = 'gpt-3.5-turbo', api_key = key)
    texto = """
    Responda às perguntas com base no contexto dos documentos.

    O contexto possui o conteúdo dos documentos, além do nome do
    arquivo e da página onde o conteúdo foi encontrado.

    Se o usuário perguntar em qual documento está uma informação,
    informe o nome do documento e a página.

    Se não encontrar a informação no contexto, informe que não
    encontrou a informação nos documentos.

    Contexto:
    {contexto}
    """
    template = ChatPromptTemplate.from_messages([
        ('system', texto),
        ('human', '{input}')
    ])

    def formatar_documentos(docs):
        contexto = ''

        for doc in docs:
            fonte = os.path.basename(doc.metadata.get('source', 'Documento desconhecido'))
            pagina = doc.metadata.get('page', 'Página desconhecida')

            contexto = contexto + f'Documento: {fonte}\nPágina: {pagina + 1}\nConteúdo: {doc.page_content}'
            return contexto

    contexto = RunnableParallel(input = RunnablePassthrough(), contexto = banco | formatar_documentos)
    chain = contexto | template | llm | StrOutputParser()
    resposta = chain.stream(entrada)

    return resposta

