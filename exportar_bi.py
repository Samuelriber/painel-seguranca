import sqlite3
import pandas as pd
import os
from datetime import datetime


def exportar_tabelas_para_csv():
    """Lê todas as tabelas do banco e as salva como ficheiros CSV."""

    # Nome do banco de dados
    db_file = 'controle_empresa.db'

    # Pasta onde os CSVs serão salvos
    output_folder = 'dados_bi'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    print(f"Conectando ao banco de dados: {db_file}")
    conn = sqlite3.connect(db_file)

    # Lista de todas as tabelas no banco de dados
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tabelas = [table[0] for table in cursor.fetchall()]

    print(f"Tabelas encontradas: {tabelas}")

    # Loop para exportar cada tabela
    for tabela in tabelas:
        try:
            print(f"Exportando a tabela '{tabela}'...")
            df = pd.read_sql_query(f"SELECT * FROM {tabela}", conn)

            # Caminho do arquivo de saída
            output_path = os.path.join(output_folder, f"{tabela}.csv")

            # Salva o DataFrame como CSV com codificação UTF-8
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f" -> Tabela '{tabela}' exportada com sucesso para '{output_path}'")
        except Exception as e:
            print(f"Erro ao exportar a tabela '{tabela}': {e}")

    conn.close()
    print(f"\nExportação concluída. {datetime.now()}")


if __name__ == "__main__":
    exportar_tabelas_para_csv()