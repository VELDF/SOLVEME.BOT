import os
import logging
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# Vamos manter a importação atualizada para a nova biblioteca
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def create_and_save_faiss_index(knowledge_base_path: str, faiss_index_path: str):
    """
    Carrega documentos, cria embeddings e salva um índice FAISS no disco.
    """
    logging.info(f"Buscando documentos em: {knowledge_base_path}...")
    
    loader = DirectoryLoader(knowledge_base_path, glob="**/*.*", show_progress=True, use_multithreading=True)
    
    try:
        docs = loader.load()
        if not docs:
            logging.warning("Nenhum documento foi carregado. A base de conhecimento está vazia?")
            return False
    except Exception as e:
        logging.error(f"Erro crítico ao carregar documentos com LangChain: {e}")
        return False

    logging.info(f"{len(docs)} documento(s) carregado(s) com sucesso.")
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(docs)
    logging.info(f"Documentos divididos em {len(split_docs)} chunks.")

    print("Criando embeddings dos documentos. Isso pode levar um momento na primeira vez...")
    logging.info("Iniciando a criação de embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name='paraphrase-multilingual-mpnet-base-v2')
    
    db = FAISS.from_documents(split_docs, embeddings)
    
    # ===================================================================
    #               CORREÇÃO FINAL (CRIAR A PASTA)
    # ===================================================================
    # Garante que a pasta de destino exista antes de tentar salvar.
    os.makedirs(faiss_index_path, exist_ok=True)
    # ===================================================================
    
    # Salva o índice FAISS no disco
    db.save_local(faiss_index_path)
    logging.info(f"Índice FAISS salvo com sucesso em: {faiss_index_path}")
    print("Índice da base de conhecimento criado e salvo com sucesso!")
    
    return True