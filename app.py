import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, timedelta
from incidentes import show_incidentes_page


# --- CONFIGURAÇÃO DO BANCO DE DADOS (BACK-END) ---

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect('controle_empresa.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Inicializa o banco de dados e cria as tabelas se não existirem."""
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
                   CREATE TABLE IF NOT EXISTS treinamentos
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
                       nome_treinamento
                       TEXT
                       NOT
                       NULL,
                       data_realizacao
                       DATE,
                       validade
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
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS incidentes
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       funcionario_id
                       INTEGER,
                       data_ocorrencia
                       DATE
                       NOT
                       NULL,
                       gravidade
                       TEXT
                       NOT
                       NULL,
                       tipo_incidente
                       TEXT
                       NOT
                       NULL,
                       local_ocorrencia
                       TEXT,
                       causa_raiz
                       TEXT,
                       partes_corpo_atingidas
                       TEXT,
                       dias_perdidos
                       INTEGER
                       DEFAULT
                       0,
                       FOREIGN
                       KEY
                   (
                       funcionario_id
                   ) REFERENCES funcionarios
                   (
                       id
                   ) ON DELETE SET NULL
                       )
                   ''')
    conn.commit()
    conn.close()


# --- FUNÇÕES CRUD (Create, Read, Update, Delete) ---

# --- Funcionários ---
def adicionar_funcionario(nome, matricula, cargo, cnh_tipo, cnh_validade):
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO funcionarios (nome, matricula, cargo, cnh_tipo, cnh_validade) VALUES (?, ?, ?, ?, ?)",
                     (nome, matricula, cargo, cnh_tipo, cnh_validade))
        conn.commit()
        st.success("✅ Funcionário adicionado com sucesso!")
    except sqlite3.IntegrityError:
        st.error("⚠️ Erro: A matrícula fornecida já existe.")
    finally:
        conn.close()


def buscar_funcionarios():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM funcionarios", conn)
    conn.close()
    return df


def atualizar_funcionario(id, nome, matricula, cargo, cnh_tipo, cnh_validade):
    conn = get_db_connection()
    try:
        conn.execute(
            "UPDATE funcionarios SET nome = ?, matricula = ?, cargo = ?, cnh_tipo = ?, cnh_validade = ? WHERE id = ?",
            (nome, matricula, cargo, cnh_tipo, cnh_validade, id))
        conn.commit()
        st.success("✅ Dados do funcionário atualizados com sucesso!")
    except sqlite3.IntegrityError:
        st.error("⚠️ Erro: A matrícula informada já pertence a outro funcionário.")
    finally:
        conn.close()


def deletar_funcionario(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM funcionarios WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    st.success("🗑️ Funcionário deletado com sucesso.")


# --- Treinamentos ---
def adicionar_treinamento(funcionario_id, nome_treinamento, data_realizacao, validade):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO treinamentos (funcionario_id, nome_treinamento, data_realizacao, validade) VALUES (?, ?, ?, ?)",
        (funcionario_id, nome_treinamento, data_realizacao, validade))
    conn.commit()
    conn.close()
    st.success("✅ Treinamento registrado com sucesso!")


def buscar_treinamentos():
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT t.id, f.nome as nome_funcionario, t.nome_treinamento, t.data_realizacao, t.validade FROM treinamentos t JOIN funcionarios f ON t.funcionario_id = f.id",
        conn)
    conn.close()
    return df


def buscar_treinamentos_por_funcionario(funcionario_id):
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT id, nome_treinamento, data_realizacao, validade FROM treinamentos WHERE funcionario_id = ?", conn,
        params=(funcionario_id,))
    conn.close()
    return df


def deletar_treinamento(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM treinamentos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    st.success("🗑️ Treinamento deletado com sucesso.")


# --- ASOs ---
def adicionar_aso(funcionario_id, tipo_exame, data_exame, resultado, validade_aso):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO asos (funcionario_id, tipo_exame, data_exame, resultado, validade_aso) VALUES (?, ?, ?, ?, ?)",
        (funcionario_id, tipo_exame, data_exame, resultado, validade_aso))
    conn.commit()
    conn.close()
    st.success("✅ ASO registrado com sucesso!")


def buscar_asos():
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT a.id, f.nome as nome_funcionario, a.tipo_exame, a.data_exame, a.resultado, a.validade_aso FROM asos a JOIN funcionarios f ON a.funcionario_id = f.id",
        conn)
    conn.close()
    return df


def buscar_asos_por_funcionario(funcionario_id):
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT id, tipo_exame, data_exame, resultado, validade_aso FROM asos WHERE funcionario_id = ?", conn,
        params=(funcionario_id,))
    conn.close()
    return df


def deletar_aso(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM asos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    st.success("🗑️ ASO deletado com sucesso.")


# --- FUNÇÃO DE DASHBOARD UNIFICADA ---
def buscar_dados_dashboard(cargo=None):
    """Busca todos os dados para o dashboard, com filtro opcional por cargo."""
    conn = get_db_connection()
    hoje = date.today()
    data_limite = hoje + timedelta(days=30)

    # Cláusula WHERE para o filtro de cargo
    where_clause = ""
    params = {}
    if cargo:
        where_clause = "WHERE f.cargo = :cargo"
        params['cargo'] = cargo

    # Consultas
    query_trein_venc = f"SELECT f.nome as nome_funcionario, t.nome_treinamento, t.validade FROM treinamentos t JOIN funcionarios f ON t.funcionario_id = f.id WHERE t.validade < :hoje {'AND f.cargo = :cargo' if cargo else ''}"
    query_asos_venc = f"SELECT f.nome as nome_funcionario, a.tipo_exame, a.validade_aso FROM asos a JOIN funcionarios f ON a.funcionario_id = f.id WHERE a.validade_aso < :hoje {'AND f.cargo = :cargo' if cargo else ''}"
    query_cnh_venc = f"SELECT nome, matricula, cnh_tipo, cnh_validade FROM funcionarios f WHERE cnh_validade < :hoje {'AND f.cargo = :cargo' if cargo else ''}"

    query_trein_prox = f"SELECT f.nome as nome_funcionario, t.nome_treinamento, t.validade FROM treinamentos t JOIN funcionarios f ON t.funcionario_id = f.id WHERE t.validade BETWEEN :hoje AND :data_limite {'AND f.cargo = :cargo' if cargo else ''}"
    query_asos_prox = f"SELECT f.nome as nome_funcionario, a.tipo_exame, a.validade_aso FROM asos a JOIN funcionarios f ON a.funcionario_id = f.id WHERE a.validade_aso BETWEEN :hoje AND :data_limite {'AND f.cargo = :cargo' if cargo else ''}"
    query_cnh_prox = f"SELECT nome, matricula, cnh_tipo, cnh_validade FROM funcionarios f WHERE cnh_validade BETWEEN :hoje AND :data_limite {'AND f.cargo = :cargo' if cargo else ''}"

    query_incidentes = f"SELECT i.gravidade, i.tipo_incidente FROM incidentes i LEFT JOIN funcionarios f ON i.funcionario_id = f.id {where_clause}"

    # Parâmetros para as consultas
    base_params = {'hoje': hoje, 'data_limite': data_limite}
    if cargo:
        base_params['cargo'] = cargo

    # Execução das consultas
    df_treinamentos_vencidos = pd.read_sql_query(query_trein_venc, conn, params=base_params)
    df_asos_vencidos = pd.read_sql_query(query_asos_venc, conn, params=base_params)
    df_cnh_vencidas = pd.read_sql_query(query_cnh_venc, conn, params=base_params)

    df_treinamentos_prox = pd.read_sql_query(query_trein_prox, conn, params=base_params)
    df_asos_prox = pd.read_sql_query(query_asos_prox, conn, params=base_params)
    df_cnh_prox = pd.read_sql_query(query_cnh_prox, conn, params=base_params)

    df_incidentes = pd.read_sql_query(query_incidentes, conn, params={'cargo': cargo} if cargo else {})

    conn.close()

    return {
        "trein_venc": df_treinamentos_vencidos, "asos_venc": df_asos_vencidos, "cnh_venc": df_cnh_vencidas,
        "trein_prox": df_treinamentos_prox, "asos_prox": df_asos_prox, "cnh_prox": df_cnh_prox,
        "incidentes": df_incidentes
    }


# --- FUNÇÃO PARA UPLOAD DE ARQUIVO ---
def processar_upload_excel(df):
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
                    nome = row['NOME']
                    cargo = row['FUNÇÃO']
                    cnh_validade_raw = row.get('CNH')
                    cnh_validade = pd.to_datetime(cnh_validade_raw).date() if pd.notna(cnh_validade_raw) else None
                    cnh_tipo = 'N/A'
                    cursor.execute(
                        "INSERT INTO funcionarios (nome, matricula, cargo, cnh_tipo, cnh_validade) VALUES (?, ?, ?, ?, ?)",
                        (nome, matricula, cargo, cnh_tipo, cnh_validade))
                    funcionario_id = cursor.lastrowid
                else:
                    funcionario_id = funcionario_existente['id']
                if 'ASO' in df.columns and 'VALIDADE DO ASO' in df.columns and pd.notna(row['ASO']):
                    data_exame = pd.to_datetime(row['ASO']).date()
                    cursor.execute("SELECT id FROM asos WHERE funcionario_id = ? AND data_exame = ?",
                                   (funcionario_id, data_exame))
                    if not cursor.fetchone():
                        validade_aso = pd.to_datetime(row['VALIDADE DO ASO']).date()
                        cursor.execute(
                            "INSERT INTO asos (funcionario_id, tipo_exame, data_exame, resultado, validade_aso) VALUES (?, ?, ?, ?, ?)",
                            (funcionario_id, 'Periódico', 'Apto', data_exame, validade_aso))
                registros_adicionados += 1
            except Exception as e:
                st.warning(f"Erro ao processar a linha {index + 2} (Matrícula: {row.get('MATRICULA', 'N/A')}): {e}")
                registros_erros += 1
        conn.commit()
        conn.close()
    st.success(f"Processamento concluído! {registros_adicionados} linhas da planilha processadas.")
    if registros_erros > 0:
        st.error(f"{registros_erros} linhas não puderam ser processadas.")


# --- PÁGINAS DA APLICAÇÃO ---

def show_dashboard():
    st.title("📊 Dashboard Interativo de Segurança")
    st.write("Visão geral das pendências e incidentes, com filtro por função.")

    # Filtro por Função
    lista_cargos = ["Todos os Cargos"] + buscar_funcionarios()['cargo'].unique().tolist()
    cargo_selecionado = st.selectbox("Filtrar por Função (Cargo):", options=lista_cargos)

    # Lógica de filtro
    filtro_cargo = None if cargo_selecionado == "Todos os Cargos" else cargo_selecionado
    dados = buscar_dados_dashboard(cargo=filtro_cargo)

    st.divider()

    # KPIs
    st.subheader("Resumo de Pendências")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Treinamentos Vencidos", value=len(dados["trein_venc"]), delta_color="inverse")
    col2.metric(label="ASOs Vencidos", value=len(dados["asos_venc"]), delta_color="inverse")
    col3.metric(label="CNHs Vencidas", value=len(dados["cnh_venc"]), delta_color="inverse")

    st.subheader("Alertas de Vencimento (Próximos 30 dias)")
    col1_prox, col2_prox, col3_prox = st.columns(3)
    col1_prox.metric(label="Treinamentos a Vencer", value=len(dados["trein_prox"]))
    col2_prox.metric(label="ASOs a Vencer", value=len(dados["asos_prox"]))
    col3_prox.metric(label="CNHs a Vencer", value=len(dados["cnh_prox"]))

    st.divider()

    # Gráficos
    st.subheader("Análise de Incidentes")
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.write("**Incidentes por Gravidade**")
        if not dados["incidentes"].empty:
            chart_data = dados["incidentes"]['gravidade'].value_counts()
            st.bar_chart(chart_data)
        else:
            st.info("Nenhum incidente registrado para a seleção atual.")

    with col_graf2:
        st.write("**Incidentes por Tipo**")
        if not dados["incidentes"].empty:
            chart_data = dados["incidentes"]['tipo_incidente'].value_counts()
            st.bar_chart(chart_data)
        else:
            st.info("Nenhum incidente registrado para a seleção atual.")

    st.divider()

    # Tabelas de Detalhes
    with st.expander("Ver Detalhes das Pendências"):
        st.error("Lista de Itens Vencidos")
        st.write("**Treinamentos Vencidos**")
        st.dataframe(dados["trein_venc"], use_container_width=True)
        st.write("**ASOs Vencidos**")
        st.dataframe(dados["asos_venc"], use_container_width=True)
        st.write("**CNHs Vencidas**")
        st.dataframe(dados["cnh_venc"], use_container_width=True)

        st.warning("Lista de Itens Próximos do Vencimento")
        st.write("**Treinamentos a Vencer**")
        st.dataframe(dados["trein_prox"], use_container_width=True)
        st.write("**ASOs a Vencer**")
        st.dataframe(dados["asos_prox"], use_container_width=True)
        st.write("**CNHs a Vencer**")
        st.dataframe(dados["cnh_prox"], use_container_width=True)


def show_funcionarios():
    st.title("👥 Gestão de Funcionários")

    with st.expander("➕ Adicionar Novo Funcionário"):
        with st.form("form_funcionarios", clear_on_submit=True):
            st.subheader("Dados do Funcionário")
            nome = st.text_input("Nome Completo")
            matricula = st.text_input("Matrícula")
            cargo = st.text_input("Cargo")
            cnh_tipo = st.selectbox("Tipo de CNH", ["N/A", "A", "B", "C", "D", "E", "AB", "AC", "AD", "AE"])
            cnh_validade = st.date_input("Validade da CNH", min_value=date(1990, 1, 1))
            if st.form_submit_button("Adicionar Funcionário", use_container_width=True):
                if not nome or not matricula or not cargo:
                    st.warning("Nome, Matrícula e Cargo são obrigatórios.")
                else:
                    adicionar_funcionario(nome, matricula, cargo, cnh_tipo, cnh_validade)

    st.divider()
    st.subheader("Lista de Funcionários Cadastrados")
    st.dataframe(buscar_funcionarios(), use_container_width=True)


def show_treinamentos():
    st.title("🎓 Gestão de Treinamentos")

    funcionarios_df = buscar_funcionarios()
    map_nome_id = {f"{row['nome']} (Mat: {row['matricula']})": row['id'] for index, row in funcionarios_df.iterrows()}

    if not map_nome_id:
        st.warning("Cadastre um funcionário primeiro para poder registrar um treinamento.")
    else:
        st.subheader("Registrar Novo Treinamento")
        nome_selecionado = st.selectbox("Selecione o Funcionário", options=map_nome_id.keys(), key="trein_func_select")
        id_selecionado = map_nome_id[nome_selecionado]

        with st.expander("Ver Histórico de Treinamentos deste Funcionário"):
            st.dataframe(buscar_treinamentos_por_funcionario(id_selecionado), use_container_width=True)

        with st.form("form_treinamentos", clear_on_submit=True):
            nome_treinamento = st.text_input("Nome do Novo Treinamento")
            col1, col2 = st.columns(2)
            data_realizacao = col1.date_input("Data de Realização", value=date.today())
            validade = col2.date_input("Data de Validade", min_value=date.today())
            if st.form_submit_button("Registrar Treinamento", use_container_width=True):
                if not nome_treinamento:
                    st.warning("O nome do treinamento é obrigatório.")
                else:
                    adicionar_treinamento(id_selecionado, nome_treinamento, data_realizacao, validade)

    st.divider()
    st.subheader("Todos os Treinamentos Registrados")
    st.dataframe(buscar_treinamentos(), use_container_width=True)


def show_asos():
    st.title("⚕️ Gestão de ASOs")

    funcionarios_df = buscar_funcionarios()
    map_nome_id = {f"{row['nome']} (Mat: {row['matricula']})": row['id'] for index, row in funcionarios_df.iterrows()}

    if not map_nome_id:
        st.warning("Cadastre um funcionário primeiro.")
    else:
        st.subheader("Registrar Novo ASO")
        nome_selecionado_aso = st.selectbox("Selecione o Funcionário", options=map_nome_id.keys(),
                                            key="aso_func_select")
        id_selecionado_aso = map_nome_id[nome_selecionado_aso]
        with st.form("form_asos", clear_on_submit=True):
            tipo_exame = st.selectbox("Tipo de Exame", ["Admissional", "Periódico", "Demissional", "Mudança de Risco",
                                                        "Retorno ao Trabalho"])
            resultado = st.selectbox("Resultado", ["Apto", "Inapto"])
            col1, col2 = st.columns(2)
            data_exame = col1.date_input("Data do Exame", value=date.today())
            validade_aso = col2.date_input("Validade do ASO", min_value=date.today())
            if st.form_submit_button("Registrar ASO", use_container_width=True):
                adicionar_aso(id_selecionado_aso, tipo_exame, data_exame, resultado, validade_aso)

    st.divider()
    st.subheader("Todos os ASOs Registrados")
    st.dataframe(buscar_asos(), use_container_width=True)


def show_editar_deletar():
    st.title("✏️ Editar ou Deletar Registros")

    funcionarios_para_editar_df = buscar_funcionarios()
    map_nome_id_edit = {f"{row['nome']} (Mat: {row['matricula']})": row['id'] for index, row in
                        funcionarios_para_editar_df.iterrows()}

    if not map_nome_id_edit:
        st.warning("Nenhum funcionário cadastrado para editar.")
    else:
        selecao_funcionario_edit = st.selectbox("Selecione um funcionário para ver/editar seus dados",
                                                options=map_nome_id_edit.keys())
        id_func_edit = map_nome_id_edit[selecao_funcionario_edit]
        dados_atuais = funcionarios_para_editar_df.loc[funcionarios_para_editar_df['id'] == id_func_edit].iloc[0]

        with st.container(border=True):
            st.subheader(f"Editando: {dados_atuais['nome']}")
            with st.form("form_edit_funcionario"):
                nome_edit = st.text_input("Nome", value=dados_atuais['nome'])
                matricula_edit = st.text_input("Matrícula", value=dados_atuais['matricula'])
                cargo_edit = st.text_input("Cargo", value=dados_atuais['cargo'])
                cnh_tipo_edit = st.selectbox("Tipo CNH", ["N/A", "A", "B", "C", "D", "E", "AB", "AC", "AD", "AE"],
                                             index=["N/A", "A", "B", "C", "D", "E", "AB", "AC", "AD", "AE"].index(
                                                 dados_atuais['cnh_tipo']))
                cnh_validade_edit = st.date_input("Validade CNH",
                                                  value=pd.to_datetime(dados_atuais['cnh_validade']).date())

                col_save, col_delete = st.columns([3, 1])
                if col_save.form_submit_button("Salvar Alterações", use_container_width=True):
                    atualizar_funcionario(id_func_edit, nome_edit, matricula_edit, cargo_edit, cnh_tipo_edit,
                                          cnh_validade_edit)
                    st.rerun()

                if col_delete.form_submit_button("🚨 Deletar"):
                    deletar_funcionario(id_func_edit)
                    st.rerun()

        st.divider()

        col_trein, col_aso = st.columns(2)
        with col_trein:
            with st.container(border=True):
                st.subheader("Deletar Treinamento")
                treinamentos_func = buscar_treinamentos_por_funcionario(id_func_edit)
                if not treinamentos_func.empty:
                    map_trein_id = {f"{row['nome_treinamento']} (Val: {row['validade']})": row['id'] for index, row in
                                    treinamentos_func.iterrows()}
                    trein_a_deletar = st.selectbox("Selecione um treinamento para deletar", options=map_trein_id.keys())
                    if st.button("Deletar Treinamento Selecionado", use_container_width=True):
                        deletar_treinamento(map_trein_id[trein_a_deletar])
                        st.rerun()
                else:
                    st.info("Este funcionário não possui treinamentos.")

        with col_aso:
            with st.container(border=True):
                st.subheader("Deletar ASO")
                asos_func = buscar_asos_por_funcionario(id_func_edit)
                if not asos_func.empty:
                    map_aso_id = {f"{row['tipo_exame']} (Val: {row['validade_aso']})": row['id'] for index, row in
                                  asos_func.iterrows()}
                    aso_a_deletar = st.selectbox("Selecione um ASO para deletar", options=map_aso_id.keys())
                    if st.button("Deletar ASO Selecionado", use_container_width=True):
                        deletar_aso(map_aso_id[aso_a_deletar])
                        st.rerun()
                else:
                    st.info("Este funcionário não possui ASOs.")


def show_upload():
    st.title("⬆️ Upload de Planilha Excel")
    st.write("Faça o upload de um arquivo Excel para adicionar múltiplos registros de uma vez.")

    with st.container(border=True):
        st.info(
            "O arquivo deve conter as colunas: 'NOME', 'FUNÇÃO', 'MATRICULA'. Colunas opcionais: 'ASO' (data do exame), 'VALIDADE DO ASO', 'CNH' (validade).")
        uploaded_file = st.file_uploader("Escolha um arquivo Excel (.xlsx)", type="xlsx")
        if uploaded_file is not None:
            try:
                df_upload = pd.read_excel(uploaded_file)
                st.write("### Pré-visualização dos Dados")
                st.dataframe(df_upload.head())
                if st.button("Processar e Salvar no Banco de Dados", use_container_width=True):
                    required_cols = ['NOME', 'FUNÇÃO', 'MATRICULA']
                    if all(col in df_upload.columns for col in df_upload.columns):
                        processar_upload_excel(df_upload)
                    else:
                        st.error(f"Erro: O arquivo precisa conter as colunas {required_cols}.")
            except Exception as e:
                st.error(f"Ocorreu um erro ao ler o arquivo: {e}")


# --- ESTRUTURA PRINCIPAL DA APLICAÇÃO ---

def main():
    init_db()

    st.set_page_config(page_title="Segurança do Trabalho", layout="wide", page_icon="🛡️")

    with st.sidebar:
        st.title("🛡️ Gestão de Segurança")
        st.write("Navegue pelas seções abaixo.")

        page = st.radio(
            "Menu Principal",
            ("📊 Dashboard", "🚨 Incidentes", "👥 Funcionários", "🎓 Treinamentos", "⚕️ ASOs", "✏️ Editar / Deletar",
             "⬆️ Upload de Arquivo"),
            label_visibility="collapsed"
        )

    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "🚨 Incidentes":
        show_incidentes_page()
    elif page == "👥 Funcionários":
        show_funcionarios()
    elif page == "🎓 Treinamentos":
        show_treinamentos()
    elif page == "⚕️ ASOs":
        show_asos()
    elif page == "✏️ Editar / Deletar":
        show_editar_deletar()
    elif page == "⬆️ Upload de Arquivo":
        show_upload()


if __name__ == "__main__":
    main()
