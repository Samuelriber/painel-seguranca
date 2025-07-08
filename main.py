import sqlite3
from faker import Faker
import random
from datetime import date, timedelta

# Inicializa o Faker para gerar dados em português do Brasil
fake = Faker('pt_BR')


def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados SQLite."""
    # Conecta ao mesmo banco de dados da sua aplicação principal
    conn = sqlite3.connect('controle_empresa.db')
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Inicializa o banco de dados e cria as tabelas se não existirem."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabela de Funcionários
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

    # Tabela de Treinamentos
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

    # Tabela de ASOs
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
    # Tabela de Incidentes
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


def gerar_data_aleatoria():
    """Gera uma data aleatória nos últimos 2 anos ou nos próximos 2 anos."""
    dias_aleatorios = random.randint(-730, 730)
    return date.today() + timedelta(days=dias_aleatorios)


def criar_dados_em_massa(numero_de_funcionarios):
    """Cria uma grande quantidade de dados falsos para todas as tabelas."""
    conn = get_db_connection()
    cursor = conn.cursor()

    print(f"Iniciando a criação de {numero_de_funcionarios} funcionários e seus registros...")

    # Listas de amostra para dados mais realistas
    cargos = ["Motorista de Caminhão", "Assistente de Logística", "Motorista Carreteiro", "Gerente de Logística",
              "Analista de Logística"]
    tipos_cnh = ["N/A", "A", "B", "C", "D", "E", "AB", "AC", "AD", "AE"]
    nomes_treinamento = ["NR-35 Trabalho em Altura", "NR-33 Espaços Confinados", "Direção Defensiva",
                         "Primeiros Socorros", "Operador de Empilhadeira"]
    tipos_exame_aso = ["Admissional", "Periódico", "Demissional", "Mudança de Risco", "Retorno ao Trabalho"]
    resultados_aso = ["Apto", "Inapto"]

    # Listas de amostra para incidentes
    tipos_incidente = ["Queda de mesmo nível", "Corte", "Pancada contra", "Esforço excessivo",
                       "Exposição a produto químico"]
    locais_ocorrencia = ["Pátio", "Oficina", "Almoxarifado", "Escritório", "Doca de Carga"]
    causas_raiz = ["Falta de atenção", "Condição insegura no piso", "Falha de equipamento", "Uso incorreto de EPI",
                   "Falta de treinamento"]
    partes_corpo = ["Mão(s)", "Pé(s)", "Perna(s)", "Braço(s)", "Cabeça", "Olhos", "Costas"]

    # --- Criação de Funcionários ---
    for i in range(numero_de_funcionarios):
        nome = fake.name()
        matricula = str(fake.unique.random_number(digits=6))
        cargo = random.choice(cargos)
        cnh_tipo = random.choice(tipos_cnh)
        cnh_validade = gerar_data_aleatoria()

        try:
            cursor.execute(
                "INSERT INTO funcionarios (nome, matricula, cargo, cnh_tipo, cnh_validade) VALUES (?, ?, ?, ?, ?)",
                (nome, matricula, cargo, cnh_tipo, cnh_validade)
            )
            funcionario_id = cursor.lastrowid

            # --- Criação de Treinamentos para o funcionário ---
            num_treinamentos = random.randint(1, 4)
            for _ in range(num_treinamentos):
                nome_treinamento = random.choice(nomes_treinamento)
                data_realizacao = gerar_data_aleatoria()
                validade = data_realizacao + timedelta(days=random.randint(180, 730))
                cursor.execute(
                    "INSERT INTO treinamentos (funcionario_id, nome_treinamento, data_realizacao, validade) VALUES (?, ?, ?, ?)",
                    (funcionario_id, nome_treinamento, data_realizacao, validade)
                )

            # --- Criação de ASOs para o funcionário ---
            num_asos = random.randint(1, 3)
            for _ in range(num_asos):
                tipo_exame = random.choice(tipos_exame_aso)
                data_exame = gerar_data_aleatoria()
                resultado = random.choice(resultados_aso)
                validade_aso = data_exame + timedelta(days=365)
                cursor.execute(
                    "INSERT INTO asos (funcionario_id, tipo_exame, data_exame, resultado, validade_aso) VALUES (?, ?, ?, ?, ?)",
                    (funcionario_id, tipo_exame, data_exame, resultado, validade_aso)
                )

            # --- Criação de Incidentes (com probabilidade) ---
            if random.random() < 0.25:  # 25% de chance de ter um incidente
                dias_perdidos = 0
                # 20% de chance do incidente ser grave ou fatal
                if random.random() < 0.20:
                    gravidade = random.choice(["Grave", "Fatal"])
                    dias_perdidos = random.randint(15, 90)
                else:
                    gravidade = random.choice(["Leve", "Moderado", "Quase Acidente"])
                    if gravidade == "Leve":
                        dias_perdidos = random.randint(1, 5)
                    elif gravidade == "Moderado":
                        dias_perdidos = random.randint(5, 15)

                cursor.execute(
                    """INSERT INTO incidentes (funcionario_id, data_ocorrencia, gravidade, tipo_incidente,
                                               local_ocorrencia, causa_raiz, partes_corpo_atingidas, dias_perdidos)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        funcionario_id,
                        gerar_data_aleatoria(),
                        gravidade,
                        random.choice(tipos_incidente),
                        random.choice(locais_ocorrencia),
                        random.choice(causas_raiz),
                        random.choice(partes_corpo),
                        dias_perdidos
                    )
                )

        except sqlite3.IntegrityError:
            print(f"Matrícula {matricula} já existe, pulando funcionário.")
            continue

        # Exibe o progresso a cada 10 funcionários criados
        if (i + 1) % 10 == 0:
            print(f"{i + 1}/{numero_de_funcionarios} funcionários criados...")

    conn.commit()
    conn.close()
    print("\nCriação de dados concluída com sucesso!")


if __name__ == "__main__":
    # Garante que as tabelas existem antes de inserir dados
    # Isso é útil se você apagar o DB e rodar este script primeiro
    print("Verificando e inicializando o banco de dados...")
    init_db()

    try:
        num = int(input("Quantos funcionários de teste você deseja criar? "))
        if num > 0:
            criar_dados_em_massa(num)
        else:
            print("Por favor, insira um número positivo.")
    except ValueError:
        print("Entrada inválida. Por favor, insira um número inteiro.")
