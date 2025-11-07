import textwrap

# --- Funções do Menu ---
def menu():
    """Exibe o menu de opções e captura a escolha do usuário."""
    menu = """\n
    *********** MENU ***********
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nu]\tNovo Usuário
    [nc]\tNova Conta
    [lc]\tListar Contas
    [q]\tSair
    ****************************
    => """
    return input(textwrap.dedent(menu))

# --- Funções das Operações Bancárias ---
def depositar(saldo, valor, extrato, /):

    if valor > 0:
        saldo += valor
        extrato += f"Depósito:\tR$ {valor:.2f}\n"
        print("\n✅ Depósito realizado com sucesso!")
    else:
        print("\n❌ Operação falhou! O valor informado é inválido.")

    return saldo, extrato

def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques):

    excedeu_saldo = valor > saldo
    excedeu_limite = valor > limite
    excedeu_saques = numero_saques >= limite_saques

    if excedeu_saldo:
        print("\n❌ Operação falhou! Você não tem saldo suficiente.")

    elif excedeu_limite:
        print("\n❌ Operação falhou! O valor do saque excede o limite.")

    elif excedeu_saques:
        print("\n❌ Operação falhou! Número máximo de saques por dia excedido!")

    elif valor > 0:
        saldo -= valor
        extrato += f"Saque:\t\tR$ {valor:.2f}\n"
        numero_saques += 1
        print("\n✅ Saque realizado com sucesso!")

    else:
        print("\n❌ Operação falhou! O valor informado é inválido.")

    return saldo, extrato

def visualizar_extrato(saldo, /, *, extrato):

    print("\n================ EXTRATO ================")
    print("Não foram realizadas movimentações." if not extrato else extrato)
    print(f"\nSaldo:\t\tR$ {saldo:.2f}")
    print("==========================================")

# --- Funções de Cadastro ---
def filtrar_usuario(cpf, usuarios):

    usuarios_filtrados = [usuario for usuario in usuarios if usuario["cpf"] == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def cadastrar_usuario(usuarios):
    
    cpf = input("Informe o CPF (somente números): ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print("\n❌ Já existe usuário com este CPF!")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/estado): ")

    usuarios.append({
        "nome": nome,
        "data_nascimento": data_nascimento,
        "cpf": cpf,
        "endereco": endereco,
    })

    print("\n✅ Usuário cadastrado com sucesso!")

def cadastrar_conta(agencia, proximo_numero_conta, usuarios):
    
    cpf = input("Informe o CPF do usuário: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print("\n✅ Conta criada com sucesso!")
        return {
            "agencia": agencia,
            "numero_conta": proximo_numero_conta,
            "usuario": usuario, # Vincula o objeto usuário
        }
    
    print("\n❌ Usuário não encontrado, fluxo de criação de conta encerrado!")
    return None

def listar_contas(contas):
    if not contas:
        print("\n⚠️ Nenhuma conta cadastrada.")
        return

    print("\n============== LISTA DE CONTAS ==============")
    for conta in contas:
        linha = f"""\
            Agência:\t{conta['agencia']}
            C/C:\t\t{conta['numero_conta']}
            Titular:\t{conta['usuario']['nome']}
            CPF:\t\t{conta['usuario']['cpf']}
        """
        print("=" * 43)
        print(textwrap.dedent(linha))
    print("=============================================")

# --- Função Principal ---
def main():
    LIMITE_SAQUES = 3
    AGENCIA = "0001"

    saldo = 0
    limite = 500
    extrato = ""
    numero_saques = 0
    
    usuarios = []  # Lista de dicionários para armazenar usuários
    contas = []    # Lista de dicionários para armazenar contas
    proximo_numero_conta = 1

    while True:
        opcao = menu()

        if opcao == "d":
            valor = float(input("Informe o valor do depósito: "))
            saldo, extrato = depositar(saldo, valor, extrato) # Argumentos posicionais

        elif opcao == "s":
            valor = float(input("Informe o valor do saque: "))
            # Argumentos nomeados (keyword only)
            saldo, extrato = sacar(
                saldo=saldo,
                valor=valor,
                extrato=extrato,
                limite=limite,
                numero_saques=numero_saques,
                limite_saques=LIMITE_SAQUES
            )
            # Se o saque foi bem-sucedido (saldo foi alterado), incrementa o contador
            if "Saque" in extrato.splitlines()[-1] and valor > 0 and saldo != saldo + valor:
                numero_saques += 1
            
        elif opcao == "e":
            # Argumentos: saldo por posição, extrato por nome
            visualizar_extrato(saldo, extrato=extrato)

        elif opcao == "nu":
            cadastrar_usuario(usuarios)
        
        elif opcao == "nc":
            conta = cadastrar_conta(AGENCIA, proximo_numero_conta, usuarios)
            if conta:
                contas.append(conta)
                proximo_numero_conta += 1 # Incrementa o número para a próxima conta
        
        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print("\n❌ Operação inválida, por favor selecione novamente a operação desejada.")

# Execução do programa
main()