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
       classificacao TEXT NOT NULL
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


# Cadastro de cliente SEM listagem automática
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


# Cadastro de filme
def adicionar_filme():
   nome = input("Digite o nome do filme: ")
   classificacao = input("Digite a classificação do filme: ")
  
   conn = conectar()
   cursor = conn.cursor()
   cursor.execute("INSERT INTO filmes (nome, classificacao) VALUES (?, ?)", (nome, classificacao))
   conn.commit()
   conn.close()
   print("Filme cadastrado com sucesso!")


# Função para buscar filmes
def buscar_filme():
   nome = input("Digite o nome do filme que deseja encontrar: ")
  
   conn = conectar()
   cursor = conn.cursor()
   cursor.execute("SELECT filmes.id, filmes.nome, filmes.classificacao, locacoes.data_locacao, locacoes.data_devolucao FROM filmes LEFT JOIN locacoes ON filmes.id = locacoes.filme_id WHERE filmes.nome LIKE ?", ('%' + nome + '%',))
   filmes = cursor.fetchall()
   conn.close()
  
   if filmes:
       print("\nFilmes encontrados:")
       for filme in filmes:
           status = "Disponível" if filme[3] is None or filme[4] is not None else f"Alocado desde {filme[3]}"
           print(f"ID: {filme[0]}, Nome: {filme[1]}, Classificação: {filme[2]}, Status: {status}")
   else:
       print("Nenhum filme encontrado.")


# Função para alocar filme
def alocar_filme():
   cliente_id = input("Digite o ID do cliente que está alugando o filme: ")
   filme_id = input("Digite o ID do filme a ser alugado: ")
   data_locacao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  
   conn = conectar()
   cursor = conn.cursor()
   cursor.execute("INSERT INTO locacoes (cliente_id, filme_id, data_locacao) VALUES (?, ?, ?)", (cliente_id, filme_id, data_locacao))
   conn.commit()
   conn.close()
   print("Filme alocado com sucesso!")


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


menu()




