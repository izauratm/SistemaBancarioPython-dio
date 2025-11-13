import textwrap
from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente, saldo=0, agencia="0001"):
        self._saldo = saldo
        self._numero = numero
        self._agencia = agencia
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n ❎ Operação falhou! Saldo insuficiente.")

        elif valor > 0:
            self._saldo -= valor
            print("\n ✅ Saque realizado com sucesso!")
            return True
        else:
            print("\n ❎ Operação falhou! O valor informado é inválido.")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n ✅ Depósito realizado com sucesso!")
            return True
        else:
            print("\n ❎ Operação falhou! O valor informado é inválido.")
            return False


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=1000, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    @property
    def limite(self):
        return self._limite
    
    @property
    def limite_saques(self):
        return self._limite_saques

    def sacar(self, valor):
        saques_hoje = [
            transacao for transacao in self.historico.transacoes
            if transacao["tipo"] == Saque.__name__ and datetime.strptime(transacao["data"].split(' ')[0], "%d-%m-%Y").date() == datetime.now().date()
        ]
        
        numero_saques = len(saques_hoje)

        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n ❎ Operação falhou! O valor do saque excede o limite.")
            return False
        
        elif excedeu_saques:
            print("\n ❎ Operação falhou! Número máximo de saques diários excedido.")
            return False
        
        return super().sacar(valor)

    def depositar(self, valor):
        return super().depositar(valor)

    def __str__(self):
        return f"""\
            {"Agência:":<10} {self.agencia}
            {"C/C:":<10} {self.numero}
            {"Titular:":<10} {self.cliente.nome}
            {"Limite:":<10} R$ {self.limite:.2f}
            {"Saques/Dia:":<10} {self.limite_saques}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )
    
    def gerar_extrato(self, conta):
        nome = conta.cliente.nome
        print("\n==================🏦 EXTRATO DB 🏦==================")
        print(f"* Titular: {nome}")
        print("----------------------------------------------------")
        
        if isinstance(conta, ContaCorrente):
            saques_dia_count = len([t for t in self._transacoes if t['tipo'] == Saque.__name__ and datetime.strptime(t['data'].split(' ')[0], '%d-%m-%Y').date() == datetime.now().date()])
            
            print(f"* Limite da conta:\t\tR$ {conta.limite:.2f}")
            print(f"* Saques diários restantes:\t{conta.limite_saques - saques_dia_count}")
            print("-" * 52)

        extrato_str = ""
        if not self._transacoes:
            extrato_str = "Não foram realizadas movimentações."
        else:
            for transacao in self._transacoes:
                extrato_str += f"{transacao['data']} | {transacao['tipo']}: R$ {transacao['valor']:.2f}\n"

        print(extrato_str)
        print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
        print("====================================================")


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @classmethod
    @abstractmethod
    def registrar(cls, conta, valor):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    @classmethod
    def registrar(cls, conta, valor):
        saque = cls(valor)
        sucesso_transacao = conta.sacar(saque.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(saque)
            return True
        return False


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    @classmethod
    def registrar(cls, conta, valor):
        deposito = cls(valor)
        sucesso_transacao = conta.depositar(deposito.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(deposito)
            return True
        return False

# ----------------------------------------------------------------------
# FUNÇÕES DE EXECUÇÃO (MAIN)
# ----------------------------------------------------------------------

def menu():
    menu = """\n
    ===================🏦 MENU DB 🏦====================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf, clientes):
    cpf_formatado = "".join(filter(str.isdigit, cpf)) 
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf_formatado]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n❎ Cliente não possui conta!")
        return None
    return cliente.contas[0]

def _realizar_operacao_bancaria(clientes, TipoTransacao, nome_operacao):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n ❎ Cliente não encontrado!")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    while True:
        try:
            valor = float(input(f"Informe o valor do {nome_operacao}: "))
            if valor <= 0:
                 print("\n*❎ Valor deve ser positivo.")
                 continue
            break
        except ValueError:
            print("\n ❎ Entrada inválida. Informe um número para o valor.")
            continue

    TipoTransacao.registrar(conta, valor)


def depositar(clientes):
    _realizar_operacao_bancaria(clientes, Deposito, "depósito")


def sacar(clientes):
    _realizar_operacao_bancaria(clientes, Saque, "saque")


def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n❎ Cliente não encontrado!")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    conta.historico.gerar_extrato(conta)

def criar_cliente(clientes):
    while True:
        cpf_input = input("-Informe o CPF (somente 11 números): ")
        cpf_limpo = "".join(filter(str.isdigit, cpf_input))
        
        if len(cpf_limpo) != 11:
            print("\n❎ Operação falhou! CPF deve conter exatamente 11 dígitos.")
            continue
        break

    if filtrar_cliente(cpf_limpo, clientes):
        print("\n❎ Já existe cliente com esse CPF!")
        return
    
    while True:
        nome = input("-Informe o nome completo: ")
        if not nome.strip():
            print("\n❎ Nome não pode ser vazio.")
            continue
        break

    while True:
        data_nascimento = input("-Informe a data de nascimento (DD/MM/AAAA): ")
        try:
            datetime.strptime(data_nascimento, "%d/%m/%Y")
            break
        except ValueError:
            print("\n ❎ Formato de data inválido. Use DD/MM/AAAA.")
            continue
            
    while True:
        endereco = input("-Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")
        if not endereco.strip():
            print("\n ❎ Endereço não pode ser vazio.")
            continue
        break

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf_limpo, endereco=endereco)

    clientes.append(cliente)

    print("\n ✅ Cliente criado com sucesso!")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)
    
    if not cliente:
        print("\n ❎ Cliente não encontrado, fluxo de criação de conta encerrado!")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.adicionar_conta(conta)
    print("\n ✅ Conta criada com sucesso!")
    
    conta.historico.gerar_extrato(conta)


def listar_contas(contas):
    if not contas:
        print("\n Não há contas cadastradas.")
        return
        
    for conta in contas:
        print("=" * 52)
        print(textwrap.dedent(str(conta)))
    print("=" * 52)


def main():
    clientes = []
    contas = []
    while True:
        opcao = menu()
        
        if opcao == "d":
            depositar(clientes)
        
        elif opcao == "s":
            sacar(clientes)
        
        elif opcao == "e":
            exibir_extrato(clientes)
        
        elif opcao == "nu":
            criar_cliente(clientes)
        
        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)
        
        elif opcao == "lc":
            listar_contas(contas)
        
        elif opcao == "q":
            print("\n👋 Obrigado(a) por usar os serviços bancários DB. Até mais!")
            break
        
        else:
            print("\n❎ Operação inválida, por favor selecione novamente a operação desejada.")

main()