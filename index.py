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
    cpf = input("Digite o CPF do cliente (XXX.XXX.XXX-XX): ")

    if not validar_cpf(cpf):
        print("CPF inválido! Use o formato XXX.XXX.XXX-XX.")
        return

    if not cpf_unico(cpf):
        print("CPF já cadastrado! Tente novamente.")
        return

    nome = input("Digite o nome do cliente: ")
    telefone = input("Digite o telefone do cliente (formato válido como (XX) XXXXX-XXXX): ")

    if not validar_telefone(telefone):
        print("Telefone inválido! Use um número real, no formato correto.")
        return

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (cpf, nome, telefone) VALUES (?, ?, ?)", (cpf, nome, telefone))
    conn.commit()
    conn.close()

    print("\nCliente cadastrado com sucesso!")

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

# Função para buscar clientes
def buscar_cliente():
    termo = input("Digite o nome ou CPF do cliente que deseja encontrar: ")

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

# Cadastro de filme com faixa etária e gênero obrigatórios e quantidade
def adicionar_filme():
    nome = input("Digite o nome do filme: ")
    classificacao = input("Digite a classificação etária do filme (Ex: Livre, 10 anos, 12 anos, 14 anos, 16 anos, 18 anos): ")
    genero = input("Digite o gênero do filme (Ex: Ação, Comédia, Drama, Ficção Científica, Terror, etc.): ")
    quantidade = input("Digite a quantidade de exemplares disponíveis: ")

    if not nome.strip():
        print("O nome do filme é obrigatório! Tente novamente.")
        return

    if not classificacao.strip():
        print("A classificação etária do filme é obrigatória! Tente novamente.")
        return

    if not genero.strip():
        print("O gênero do filme é obrigatório! Tente novamente.")
        return

    if not quantidade.strip() or not quantidade.isdigit() or int(quantidade) <= 0:
        print("A quantidade de exemplares deve ser um número inteiro maior que zero! Tente novamente.")
        return

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO filmes (nome, classificacao, genero, quantidade) VALUES (?, ?, ?, ?)", (nome, classificacao, genero, int(quantidade)))
    conn.commit()
    conn.close()
    print("Filme cadastrado com sucesso!")

# Função para buscar filmes
def buscar_filme():
    nome = input("Digite o nome do filme que deseja encontrar: ")

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
        print("Nenhum filme encontrado.")

    conn.close()

# Função para alocar filme
def alocar_filme():
    cliente_id = input("Digite o ID do cliente que está alugando o filme: ")
    nome_filme = input("Digite o nome do filme a ser alugado: ")

    conn = conectar()
    cursor = conn.cursor()

    # Busca o filme pelo nome
    cursor.execute("SELECT id, nome, quantidade FROM filmes WHERE nome LIKE ?", ('%' + nome_filme + '%',))
    filmes_encontrados = cursor.fetchall()

    if not filmes_encontrados:
        print("Nenhum filme encontrado com esse nome.")
        conn.close()
        return
    elif len(filmes_encontrados) > 1:
        print("Múltiplos filmes encontrados com esse nome. Por favor, seja mais específico:")
        for filme in filmes_encontrados:
            # Conta quantos exemplares deste filme estão atualmente alugados
            cursor.execute("SELECT COUNT(*) FROM locacoes WHERE filme_id = ? AND data_devolucao IS NULL", (filme[0],))
            locacoes_pendentes = cursor.fetchone()[0]
            disponiveis = filme[2] - locacoes_pendentes
            status = "✅ Disponíveis" if disponiveis > 0 else "❌ Indisponível"
            print(f"ID: {filme[0]}, Nome: {filme[1]}, Existentes: {filme[2]}, {status} ({disponiveis})")
        conn.close()
        return
    else:
        filme = filmes_encontrados[0]
        filme_id = filme[0]
        data_locacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Conta quantos exemplares deste filme estão atualmente alugados
        cursor.execute("SELECT COUNT(*) FROM locacoes WHERE filme_id = ? AND data_devolucao IS NULL", (filme_id,))
        locacoes_pendentes = cursor.fetchone()[0]
        disponiveis = filme[2] - locacoes_pendentes

        if disponiveis > 0:
            cursor.execute("INSERT INTO locacoes (cliente_id, filme_id, data_locacao) VALUES (?, ?, ?)", (cliente_id, filme_id, data_locacao))
            conn.commit()
            print(f"Filme '{filme[1]}' alocado com sucesso. Exemplares disponíveis restantes: {disponiveis - 1}")
        else:
            print(f"❌ Indisponível! Não há exemplares disponíveis do filme '{filme[1]}' no momento.")

    conn.close()

# Função para devolver filme
def devolver_filme():
    locacao_id = input("Digite o ID da locação a ser devolvida: ")
    data_devolucao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE locacoes SET data_devolucao = ? WHERE id = ?", (data_devolucao, locacao_id))
    conn.commit()
    conn.close()
    print("Filme devolvido com sucesso!")

# Menu atualizado
def menu():
    criar_tabelas()

    while True:
        print("\n===== Locadora de Filmes =====")
        print("1 - Cadastrar Cliente")
        print("2 - Listar Todos os Clientes")
        print("3 - Procurar Cliente")
        print("4 - Cadastrar Filme")
        print("5 - Procurar Filme")
        print("6 - Alocar Filme")
        print("7 - Devolver Filme")
        print("8 - Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            adicionar_cliente()
        elif opcao == "2":
            listar_clientes()
        elif opcao == "3":
            buscar_cliente()
        elif opcao == "4":
            adicionar_filme()
        elif opcao == "5":
            buscar_filme()
        elif opcao == "6":
            alocar_filme()
        elif opcao == "7":
            devolver_filme()
        elif opcao == "8":
            print("Saindo do sistema...")
            break
        else:
            print("Opção inválida! Tente novamente.")

if __name__ == "__main__":
    menu()