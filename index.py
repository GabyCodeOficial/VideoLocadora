import sqlite3
import re
from datetime import datetime

# Função para conectar ao banco de dados
def conectar():
    return sqlite3.connect("locadora.db")

# Criar tabelas
def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cpf TEXT UNIQUE NOT NULL,
        nome TEXT NOT NULL,
        telefone TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS filmes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        classificacao TEXT NOT NULL,
        genero TEXT NOT NULL,
        quantidade INTEGER NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS locacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id INTEGER NOT NULL,
        filme_id INTEGER NOT NULL,
        data_locacao TEXT NOT NULL,
        data_devolucao TEXT,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id),
        FOREIGN KEY (filme_id) REFERENCES filmes(id)
    );
    """)

    conn.commit()
    conn.close()

# Funções de validação
def validar_cpf(cpf):
    padrao = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")
    return bool(padrao.match(cpf))

def cpf_unico(cpf):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT cpf FROM clientes WHERE cpf = ?", (cpf,))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is None

def validar_telefone(telefone):
    padrao = re.compile(r"^\(?\d{2}\)?\s?\d{4,5}-?\d{4}$")  # Formato (XX) XXXXX-XXXX
    return bool(padrao.match(telefone))

# Cadastro de cliente
def adicionar_cliente():
    while True:
        cpf = input("Digite o CPF do cliente (XXX.XXX.XXX-XX) (ou 'V' para voltar): ")
        if cpf.upper() == 'V':
            return

        if not validar_cpf(cpf):
            print("CPF inválido! Use o formato XXX.XXX.XXX-XX.")
            continue

        if not cpf_unico(cpf):
            print("CPF já cadastrado! Tente novamente.")
            continue

        nome = input("Digite o nome do cliente: ")
        telefone = input("Digite o telefone do cliente (formato válido como (XX) XXXXX-XXXX): ")

        if not validar_telefone(telefone):
            print("Telefone inválido! Use um número real, no formato correto.")
            continue

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (cpf, nome, telefone) VALUES (?, ?, ?)", (cpf, nome, telefone))
        conn.commit()

        # Recupera o ID do cliente cadastrado
        cliente_id = cursor.lastrowid
        print("\nCliente cadastrado com sucesso!")
        print(f"ID: {cliente_id}")
        print(f"CPF: {cpf}")
        print(f"Nome: {nome}")
        print(f"Telefone: {telefone}")

        conn.close()
        break

# Função para listar todos os clientes cadastrados
def listar_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, cpf, nome, telefone FROM clientes")
    clientes = cursor.fetchall()
    conn.close()

    print(f"\nTotal de clientes cadastrados: {len(clientes)}")

    if clientes:
        print("\nLista de clientes cadastrados:")
        for cliente in clientes:
            print(f"ID: {cliente[0]}, CPF: {cliente[1]}, Nome: {cliente[2]}, Telefone: {cliente[3]}")
    else:
        print("Nenhum cliente cadastrado.")
    input("\nPressione Enter para voltar ao menu principal.")

# Função para buscar clientes
def buscar_cliente():
    while True:
        termo = input("Digite o nome ou CPF do cliente que deseja encontrar (ou 'V' para voltar): ")
        if termo.upper() == 'V':
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, cpf, nome, telefone FROM clientes WHERE cpf LIKE ? OR nome LIKE ?", ('%' + termo + '%', '%' + termo + '%'))
        clientes = cursor.fetchall()
        conn.close()

        if clientes:
            print("\nClientes encontrados:")
            for cliente in clientes:
                print(f"ID: {cliente[0]}, CPF: {cliente[1]}, Nome: {cliente[2]}, Telefone: {cliente[3]}")
        else:
            print("Nenhum cliente encontrado.")
        input("\nPressione Enter para voltar ao menu principal.")
        break

# Cadastro de filme com faixa etária e gênero obrigatórios e quantidade
def adicionar_filme():
    while True:
        nome = input("Digite o nome do filme (ou 'V' para voltar): ")
        if nome.upper() == 'V':
            return

        classificacao = input("Digite a classificação etária do filme (Ex: Livre, 10 anos, 12 anos, 14 anos, 16 anos, 18 anos): ")
        genero = input("Digite o gênero do filme (Ex: Ação, Comédia, Drama, Ficção Científica, Terror, etc.): ")
        quantidade = input("Digite a quantidade de exemplares disponíveis: ")

        if not nome.strip():
            print("O nome do filme é obrigatório! Tente novamente.")
            continue

        if not classificacao.strip():
            print("A classificação etária do filme é obrigatória! Tente novamente.")
            continue

        if not genero.strip():
            print("O gênero do filme é obrigatório! Tente novamente.")
            continue

        if not quantidade.strip() or not quantidade.isdigit() or int(quantidade) <= 0:
            print("A quantidade de exemplares deve ser um número inteiro maior que zero! Tente novamente.")
            continue

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO filmes (nome, classificacao, genero, quantidade) VALUES (?, ?, ?, ?)", (nome, classificacao, genero, int(quantidade)))
        conn.commit()

        filme_id = cursor.lastrowid
        print("\nFilme cadastrado com sucesso!")
        print(f"ID: {filme_id}")
        print(f"Nome: {nome}")
        print(f"Classificação: {classificacao}")
        print(f"Gênero: {genero}")
        print(f"Quantidade: {quantidade}")

        conn.close()
        break

# Função para buscar filmes
def buscar_filme():
    while True:
        nome = input("Digite o nome do filme que deseja encontrar (ou 'V' para voltar): ")
        if nome.upper() == 'V':
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, classificacao, genero, quantidade FROM filmes WHERE nome LIKE ?", ('%' + nome + '%',))
        filmes = cursor.fetchall()

        if filmes:
            print("\nFilmes encontrados:")
            for filme in filmes:
                filme_id = filme[0]
                cursor.execute("SELECT COUNT(*) FROM locacoes WHERE filme_id = ? AND data_devolucao IS NULL", (filme_id,))
                locacoes_pendentes = cursor.fetchone()[0]
                disponiveis = filme[4] - locacoes_pendentes
                status = "✅ Disponíveis" if disponiveis > 0 else "❌ Indisponível"
                print(f"ID: {filme[0]}, Nome: {filme[1]}, Classificação: {filme[2]}, Gênero: {filme[3]}, Existentes: {filme[4]}, {status} ({disponiveis})")
        else:
            print("Nenhum filme encontrado com o termo digitado.")
        input("\nPressione Enter para voltar ao menu principal.")
        break

# Função para devolver filme
def devolver_filme():
    while True:
        cliente_identificacao = input("Digite o CPF ou ID do cliente que está devolvendo o filme (ou 'V' para voltar): ")
        if cliente_identificacao.upper() == 'V':
            return

        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM clientes WHERE cpf = ? OR id = ?", (cliente_identificacao, cliente_identificacao))
        cliente = cursor.fetchone()

        if not cliente:
            print("Cliente não encontrado.")
            continue

        cliente_id = cliente[0]

        filme_id_devolucao = input("Digite o ID do filme a ser devolvido (ou 'V' para voltar): ")
        if filme_id_devolucao.upper() == 'V':
            return

        if not filme_id_devolucao.isdigit():
            print("ID do filme inválido. Digite apenas números.")
            continue

        cursor.execute("SELECT id, nome FROM filmes WHERE id = ?", (filme_id_devolucao,))
        filme = cursor.fetchone()

        if not filme:
            print("ID do filme não encontrado.")
            continue

        cursor.execute("SELECT id FROM locacoes WHERE cliente_id = ? AND filme_id = ? AND data_devolucao IS NULL", (cliente_id, filme_id_devolucao))
        locacao = cursor.fetchone()

        if not locacao:
            print(f"Nenhum exemplar do filme '{filme[1]}' alocado para este cliente.")
            continue

        locacao_id = locacao[0]
        data_devolucao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(f"\nConfirmar devolução do filme: {filme[1]}?")
        confirmacao = input("(S/N): ").upper()

        if confirmacao == 'S':
            cursor.execute("UPDATE locacoes SET data_devolucao = ? WHERE id = ?", (data_devolucao, locacao_id))
            conn.commit()
            print("Filme devolvido com sucesso!")
        else:
            print("Devolução cancelada.")

        conn.close()
        input("\nPressione Enter para voltar ao menu principal.")
        break

# Menu de Cadastros
def menu_cadastros():
    while True:
        print("\n===== Cadastros =====")
        print("1 - Cadastrar Cliente")
        print("2 - Cadastrar Filme")
        print("3 - Voltar ao Menu Principal")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            adicionar_cliente()
        elif opcao == "2":
            adicionar_filme()
        elif opcao == "3":
            break
        else:
            print("Opção inválida! Tente novamente.")

# Menu de Pesquisas
def menu_pesquisas():
    while True:
        print("\n===== Pesquisas =====")
        print("1 - Procurar Cliente")
        print("2 - Procurar Filme")
        print("3 - Voltar ao Menu Principal")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            buscar_cliente()
        elif opcao == "2":
            buscar_filme()
        elif opcao == "3":
            break
        else:
            print("Opção inválida! Tente novamente.")

# Menu de Relatórios
def menu_relatorios():
    while True:
        print("\n===== Relatórios =====")
        print("1 - Listar todos os clientes")
        print("2 - Voltar ao Menu Principal")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            listar_clientes()
        elif opcao == "2":
            break
        else:
            print("Opção inválida! Tente novamente.")

# Menu principal
def menu_principal():
    criar_tabelas()

    while True:
        print("\n===== Locadora de Filmes =====")
        print("1 - Locar Filme")
        print("2 - Cadastros")
        print("3 - Pesquisar")
        print("4 - Relatório")
        print("5 - Devolver Filme")
        print("6 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            alocar_filme()
        elif opcao == "2":
            menu_cadastros()
        elif opcao == "3":
            menu_pesquisas()
        elif opcao == "4":
            menu_relatorios()
        elif opcao == "5":
            devolver_filme()
        elif opcao == "6":
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida! Tente novamente.")

if __name__ == "__main__":
    menu_principal()
