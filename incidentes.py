import streamlit as st
import sqlite3
import pandas as pd
from datetime import date


# --- FUNÇÕES DE BANCO DE DADOS ESPECÍFICAS PARA INCIDENTES ---

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect('controle_empresa.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def buscar_funcionarios_para_incidente():
    """Busca funcionários para a lista de seleção."""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT id, nome, matricula FROM funcionarios", conn)
    conn.close()
    return df


def adicionar_incidente(funcionario_id, data_ocorrencia, gravidade, tipo_incidente, local_ocorrencia, causa_raiz,
                        partes_corpo_atingidas, dias_perdidos):
    """Adiciona um novo incidente ao banco de dados."""
    conn = get_db_connection()
    conn.execute("""
                 INSERT INTO incidentes (funcionario_id, data_ocorrencia, gravidade, tipo_incidente, local_ocorrencia,
                                         causa_raiz, partes_corpo_atingidas, dias_perdidos)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                 """, (funcionario_id, data_ocorrencia, gravidade, tipo_incidente, local_ocorrencia, causa_raiz,
                       partes_corpo_atingidas, dias_perdidos))
    conn.commit()
    conn.close()
    st.success("✅ Incidente registrado com sucesso!")


def buscar_incidentes():
    """Busca todos os incidentes registrados."""
    conn = get_db_connection()
    query = """
            SELECT i.id,
                   COALESCE(f.nome, 'Não se aplica / Terceiro') as nome_funcionario,
                   i.data_ocorrencia,
                   i.gravidade,
                   i.tipo_incidente,
                   i.local_ocorrencia,
                   i.causa_raiz,
                   i.partes_corpo_atingidas,
                   i.dias_perdidos
            FROM incidentes i
                     LEFT JOIN funcionarios f ON i.funcionario_id = f.id
            ORDER BY i.data_ocorrencia DESC
            """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# --- FUNÇÃO PRINCIPAL DA PÁGINA DE INCIDENTES ---

def show_incidentes_page():
    """Cria a interface da aba de registro de incidentes."""
    st.header("🚨 Registro de Incidentes e Acidentes")

    funcionarios_df = buscar_funcionarios_para_incidente()

    if funcionarios_df.empty:
        st.info(
            "ℹ️ Não há funcionários cadastrados. Para associar um incidente a um funcionário, cadastre um na aba 'Funcionários' primeiro.")
        map_nome_id_incidentes = {}
    else:
        map_nome_id_incidentes = {f"{row['nome']} (Mat: {row['matricula']})": row['id'] for index, row in
                                  funcionarios_df.iterrows()}

    opcoes_funcionarios = ["Não se aplica / Terceiro"] + list(map_nome_id_incidentes.keys())

    with st.form("form_incidentes", clear_on_submit=True):
        st.subheader("Detalhes da Ocorrência")

        selecao_funcionario_incidente = st.selectbox("Funcionário Envolvido", options=opcoes_funcionarios)
        data_ocorrencia = st.date_input("Data da Ocorrência", value=date.today())

        col1, col2 = st.columns(2)
        with col1:
            gravidade = st.selectbox("Gravidade", ["Leve", "Moderado", "Grave", "Fatal", "Quase Acidente"])
        with col2:
            tipo_incidente = st.text_input("Tipo de Incidente", placeholder="Ex: Queda, corte, esmagamento...")

        local_ocorrencia = st.text_input("Local da Ocorrência", placeholder="Ex: Pátio, Oficina, Almoxarifado...")
        partes_corpo_atingidas = st.text_input("Partes do Corpo Atingidas",
                                               placeholder="Ex: Mão direita, pé esquerdo, olhos...")
        causa_raiz = st.text_area("Causa Raiz / Descrição do Incidente")
        dias_perdidos = st.number_input("Dias Perdidos (Afastamento)", min_value=0, step=1)

        if st.form_submit_button("Registrar Incidente"):
            if not tipo_incidente or not local_ocorrencia:
                st.warning("Tipo de Incidente e Local da Ocorrência são campos obrigatórios.")
            else:
                id_funcionario_incidente = None
                if selecao_funcionario_incidente != "Não se aplica / Terceiro":
                    id_funcionario_incidente = map_nome_id_incidentes[selecao_funcionario_incidente]

                adicionar_incidente(id_funcionario_incidente, data_ocorrencia, gravidade, tipo_incidente,
                                    local_ocorrencia, causa_raiz, partes_corpo_atingidas, dias_perdidos)

    st.divider()
    st.header("Histórico de Incidentes Registrados")
    st.dataframe(buscar_incidentes(), use_container_width=True)
