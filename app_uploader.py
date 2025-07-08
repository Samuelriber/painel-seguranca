import streamlit as st
import sqlite3
import pandas as pd


# --- FUNÇÕES DE BANCO DE DADOS (Copiadas aqui para tornar o arquivo independente) ---

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    # check_same_thread=False é necessário para o Streamlit
    conn = sqlite3.connect('controle_empresa.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Garante que as tabelas existem no banco de dados."""
    # Esta função é idêntica à do arquivo principal
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS funcionarios
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       nome
                       TEXT
                       NOT
                       NULL,
                       matricula
                       TEXT
                       UNIQUE,
                       cargo
                       TEXT,
                       cnh_tipo
                       TEXT,
                       cnh_validade
                       DATE
                   )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS asos
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       funcionario_id
                       INTEGER
                       NOT
                       NULL,
                       tipo_exame
                       TEXT
                       NOT
                       NULL,
                       data_exame
                       DATE,
                       resultado
                       TEXT,
                       validade_aso
                       DATE,
                       FOREIGN
                       KEY
                   (
                       funcionario_id
                   ) REFERENCES funcionarios
                   (
                       id
                   ) ON DELETE CASCADE
                       )
                   ''')
    conn.commit()
    conn.close()


# --- FUNÇÃO PARA PROCESSAR O ARQUIVO EXCEL ---

def processar_upload_excel(df):
    """Processa o DataFrame do Excel e insere os dados no banco."""
    conn = get_db_connection()
    cursor = conn.cursor()

    registros_adicionados = 0
    registros_erros = 0

    with st.spinner("Processando arquivo... Isso pode levar alguns instantes."):
        for index, row in df.iterrows():
            try:
                matricula = str(row['MATRICULA'])
                cursor.execute("SELECT id FROM funcionarios WHERE matricula = ?", (matricula,))
                funcionario_existente = cursor.fetchone()

                if not funcionario_existente:
                    # Se o funcionário não existe, cria um novo
                    nome = row['NOME']
                    cargo = row['FUNÇÃO']
                    cnh_validade_raw = row.get('CNH')
                    cnh_validade = pd.to_datetime(cnh_validade_raw).date() if pd.notna(cnh_validade_raw) else None
                    cnh_tipo = 'N/A'

                    cursor.execute(
                        "INSERT INTO funcionarios (nome, matricula, cargo, cnh_tipo, cnh_validade) VALUES (?, ?, ?, ?, ?)",
                        (nome, matricula, cargo, cnh_tipo, cnh_validade)
                    )
                    funcionario_id = cursor.lastrowid
                else:
                    # Se já existe, apenas pega o ID
                    funcionario_id = funcionario_existente['id']

                # Insere o ASO, se os dados existirem na planilha
                if 'ASO' in df.columns and 'VALIDADE DO ASO' in df.columns and pd.notna(row['ASO']):
                    data_exame = pd.to_datetime(row['ASO']).date()

                    # Evita duplicatas de ASO para o mesmo funcionário na mesma data
                    cursor.execute("SELECT id FROM asos WHERE funcionario_id = ? AND data_exame = ?",
                                   (funcionario_id, data_exame))
                    if not cursor.fetchone():
                        validade_aso = pd.to_datetime(row['VALIDADE DO ASO']).date()
                        cursor.execute(
                            "INSERT INTO asos (funcionario_id, tipo_exame, data_exame, resultado, validade_aso) VALUES (?, ?, ?, ?, ?)",
                            (funcionario_id, 'Periódico', 'Apto', data_exame, validade_aso)
                        )

                registros_adicionados += 1
            except Exception as e:
                st.warning(f"Erro ao processar a linha {index + 2} (Matrícula: {row.get('MATRICULA', 'N/A')}): {e}")
                registros_erros += 1

        conn.commit()
        conn.close()

    st.success(f"Processamento concluído! {registros_adicionados} linhas da planilha processadas.")
    if registros_erros > 0:
        st.error(f"{registros_erros} linhas não puderam ser processadas.")


# --- INTERFACE DA APLICAÇÃO DE UPLOAD ---

init_db()

st.set_page_config(page_title="Uploader - Segurança do Trabalho", layout="centered")
st.title("⬆️ Ferramenta de Upload para Segurança do Trabalho")
st.write("Envie dados de funcionários e ASOs a partir de uma planilha Excel.")
st.info(
    "O arquivo deve conter as colunas: 'NOME', 'FUNÇÃO', 'MATRICULA'.\nColunas opcionais: 'ASO' (data do exame), 'VALIDADE DO ASO', 'CNH' (validade).")

# Widget para fazer o upload do arquivo
uploaded_file = st.file_uploader("Escolha um arquivo Excel (.xlsx)", type="xlsx")

if uploaded_file is not None:
    try:
        # Lê o arquivo excel para um dataframe
        df_upload = pd.read_excel(uploaded_file)

        st.write("### Pré-visualização dos Dados")
        st.dataframe(df_upload)

        # Botão para iniciar o processamento
        if st.button("Processar e Salvar no Banco de Dados"):
            # Verifica se as colunas obrigatórias existem
            required_cols = ['NOME', 'FUNÇÃO', 'MATRICULA']
            if all(col in df_upload.columns for col in required_cols):
                processar_upload_excel(df_upload)
            else:
                st.error(f"Erro: O arquivo precisa conter as colunas {required_cols}.")

    except Exception as e:
        st.error(f"Ocorreu um erro ao ler o arquivo: {e}")
        st.warning(
            "Verifique se o arquivo é um Excel (.xlsx) válido e se a biblioteca 'openpyxl' está instalada (`pip install openpyxl`).")

