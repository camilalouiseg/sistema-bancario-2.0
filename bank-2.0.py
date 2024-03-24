from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime
import textwrap
        
class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
        
    def realizar_transacao(self, conta, transacao):
            transacao.registrar(conta)

    def adicionar_conta(self, conta):
            self.contas.append(conta)

class PessoaFisica (Cliente):
    def __init__(self, nome, cpf, data_nascimento, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento

class Conta():
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod   #cria uma função que cria novas contas com base nessa classe
    def nova_conta (cls, cliente, numero):
        return cls(numero, cliente)
        
    @property   #é uma propriedade da classe Conta, portanto não pode ser alterada diretamente fora da classe
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
            print('\n Operação Falhou! Você não tem saldo suficiente.')
        
        elif valor > 0: 
            self._saldo -= valor
            print("\n Saque realizado com sucesso! ")
            return True

        else:
            print("\n Operação falhou! O valor informado é inválido. ")
        
        return False
    
    def depositar(self,valor):
        if valor > 0:
            self._saldo += valor
            print('\n Depósito realizado com sucesso!')
        else: 
            print('\n Operação falhou! O valor informado é inválido.')
            return False
        
        return True

class Conta_Corrente(Conta):

    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques
    
    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )

        excedeu_saques = numero_saques >= self.limite_saques
        excedeu_limite = valor > self.limite

        if excedeu_saques:
            print('Operação falhou! Número máximo de saques atingido!')

        elif excedeu_limite:
            print('Operação falhou!  O valor do saque excede o limite!')
        
        else:
            return super().sacar(valor)
        
        return False
    
    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
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
                #"data": datetime.now().strftime("%d-%m-%Y %H:%M:%s"),
            }
        )

class Transacao(ABC):

    @abstractproperty
    def valor(self):
        pass
    @abstractclassmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
       self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def menu() :
    menu = """\n
    ============ MENU ============

    [d] Depositar
    [s] Sacar
    [e] Extrato
    [nc] Nova Conta
    [lc] Listar Contas
    [nu] Novo Usuario
    [q] Sair
    => """
    return input(textwrap.dedent(menu))

def filtrar_clientes(cpf, clientes):

    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n Cliente não possui conta! ")
        return

    # FIXME: não permite cliente escolher a conta
    return cliente.contas[0]

def depositar(clientes):
    cpf = input('Digite seu CPF (somente números): ')
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente:
        print("\n Cliente não encontrado! ")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
        
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente:
        print("\n Cliente não encontrado! ")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)
        
def exibir_extrato(clientes):

    cpf = input('Digite seu CPF (somente números): ')
    cliente = filtrar_clientes(cpf, clientes)

    conta = recuperar_conta_cliente(cliente)
    if not cliente:
        print('Cliente não encontrado!')
        return
    
    print("=========   EXTRATO   =========")
    transacoes = conta.historico.transacoes

    extrato = ''
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:  R$ {transacao['valor']:.2f}"

    print(f'{extrato}\n')
    print(f"\nSaldo: R${conta.saldo:.2f}")
    print("===============================")

def criar_cliente(clientes):
    cpf = input('Digite o seu CPF(somente números): ')
    cliente = filtrar_clientes(cpf, clientes)

    if cliente:
        print('\n Já existe cliente com esse CPF! ')
        return
    else:           
        nome = input('Digite seu nome completo: ')
        data_nascimento = input('Digite sua data de nascimento (dd-mm-aaaa): ')
        endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")
        
        cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
        clientes.append(cliente)
        print('Cliente cadastrado com sucesso!')

def criar_conta(numero_conta, clientes, contas):
    cpf=input('Digite seu CPF(somente números): ')
    cliente = filtrar_clientes(cpf, clientes)
    
    if not cliente:
        print("\n Cliente não encontrado! ")
        return
    
    conta = Conta_Corrente.nova_conta(cliente = cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)
    print("\n=== Conta criada com sucesso! ===")

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))

def main():
    clientes=[]
    contas=[]

    while True :
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
            break

        else:
            print("Operação inválida")


main()