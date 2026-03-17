# 🛡️ Painel de Segurança do Trabalho

Sistema web para gestão de Segurança e Saúde Ocupacional, com dashboard interativo, controle de vencimentos e exportação de dados para ferramentas de BI.

Desenvolvido com **Python**, **Streamlit** e **SQLite**.

---

## 📋 Sobre o Projeto

O sistema centraliza o controle operacional de um departamento de Segurança do Trabalho, permitindo gerenciar funcionários, treinamentos obrigatórios (NRs), exames médicos (ASOs), CNHs e registros de incidentes — tudo com alertas automáticos de vencimento e visualização em dashboard.

**Problema que resolve:** substituir planilhas manuais e descentralizadas por uma aplicação única com alertas proativos, reduzindo o risco de multas por documentação vencida e melhorando a visibilidade para tomada de decisão.

---

## ⚙️ Funcionalidades

**Dashboard Interativo**
- KPIs de pendências: treinamentos, ASOs e CNHs vencidos ou próximos do vencimento (30 dias)
- Gráficos de incidentes por gravidade e tipo
- Filtro dinâmico por cargo/função
- Tabelas detalhadas em expander

**Módulos CRUD**
- Cadastro e edição de funcionários (nome, matrícula, cargo, CNH)
- Registro de treinamentos com controle de validade
- Registro de ASOs com tipo de exame e resultado (Apto/Inapto)
- Registro de incidentes com gravidade, causa raiz, partes do corpo atingidas e dias perdidos

**Importação e Exportação**
- Upload de planilhas Excel (.xlsx) para carga em massa de funcionários e ASOs, com detecção de duplicatas
- Exportação de todas as tabelas para CSV (`exportar_bi.py`) para consumo em Power BI ou outra ferramenta de BI

**Geração de Dados de Teste**
- Script `gerarador_de_dados.py` usando Faker para popular o banco com dados realistas em volume configurável

---

## 🛠️ Stack

| Camada | Tecnologia |
|--------|------------|
| Frontend | Streamlit |
| Backend | Python |
| Banco de Dados | SQLite |
| Manipulação de Dados | Pandas |
| Dados de Teste | Faker |
| Exportação BI | CSV (UTF-8) |

---

## 📁 Estrutura do Projeto

```
painel-seguranca/
├── app.py                  # Aplicação principal (Streamlit)
├── incidentes.py           # Módulo de registro de incidentes
├── app_uploader.py         # Ferramenta standalone de upload Excel
├── exportar_bi.py          # Script de exportação do banco → CSV
├── gerarador_de_dados.py   # Gerador de dados fictícios (Faker)
├── logo-avapex.png         # Logo exibida na sidebar
├── dados_bi/               # CSVs exportados para BI
│   ├── funcionarios.csv
│   ├── treinamentos.csv
│   ├── asos.csv
│   └── incidentes.csv
└── .gitignore
```

---

## 🚀 Como Executar

**Pré-requisitos:** Python 3.8+

```bash
# Clone o repositório
git clone https://github.com/Samuelriber/painel-seguranca.git
cd painel-seguranca

# Instale as dependências
pip install streamlit pandas faker openpyxl

# (Opcional) Gere dados de teste
python gerarador_de_dados.py

# Execute a aplicação
streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`.

---

## 📊 Exportação para BI

Para exportar os dados do banco SQLite para arquivos CSV consumíveis por Power BI:

```bash
python exportar_bi.py
```

Os arquivos são gerados na pasta `dados_bi/` com encoding UTF-8 (com BOM), prontos para importação direta.

---

## 📸 Screenshots

> *Em breve*

---

## 👤 Autor

**Samuel Ribeiro**
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/samuel-ribeiro-14b780213)
