from airflow.decorators import dag, task
from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook
from datetime import datetime
from faker import Faker
import random

@dag(
    schedule='@daily',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['etl', 'sqlserver', 'faker', 'demo']
)
def inserir_dados_fakes_sqlserver():

    @task()
    def inserir_dados():
        print("🕑 Iniciando task inserir_dados")
        hook = MsSqlHook(mssql_conn_id="mssql_local")
        print("✅ MsSqlHook criado")
        conn = hook.get_conn()
        print("✅ Conexão obtida")
        cursor = conn.cursor()
        print("✅ Cursor aberto")
        fake = Faker('pt_BR')

        # 1) CRIAR TABELAS SE NÃO EXISTIREM (já com updated_at)
        print("🕑 Verificando/criando tabelas")
        tabelas = [
            ('lojas', f"""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'lojas')
                BEGIN
                  CREATE TABLE dbo.lojas (
                    id_loja INT IDENTITY(1,1) PRIMARY KEY,
                    nome_loja VARCHAR(80),
                    cidade VARCHAR(60),
                    estado CHAR(2),
                    updated_at DATETIME2(3) NOT NULL CONSTRAINT DF_lojas_updated_at DEFAULT SYSUTCDATETIME()
                  )
                END
            """),
            ('clientes', f"""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'clientes')
                BEGIN
                  CREATE TABLE dbo.clientes (
                    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
                    nome VARCHAR(100),
                    email VARCHAR(100),
                    telefone VARCHAR(30),
                    data_cadastro DATE,
                    updated_at DATETIME2(3) NOT NULL CONSTRAINT DF_clientes_updated_at DEFAULT SYSUTCDATETIME()
                  )
                END
            """),
            ('pedidos', f"""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'pedidos')
                BEGIN
                  CREATE TABLE dbo.pedidos (
                    id_pedido INT IDENTITY(1,1) PRIMARY KEY,
                    id_cliente INT,
                    id_loja INT,
                    data_pedido DATE,
                    valor_total DECIMAL(10,2),
                    status VARCHAR(20),
                    updated_at DATETIME2(3) NOT NULL CONSTRAINT DF_pedidos_updated_at DEFAULT SYSUTCDATETIME(),
                    FOREIGN KEY (id_cliente) REFERENCES dbo.clientes(id_cliente),
                    FOREIGN KEY (id_loja) REFERENCES dbo.lojas(id_loja)
                  )
                END
            """),
        ]

        for name, ddl in tabelas:
            print(f"   🕑 Tabela `{name}`")
            cursor.execute(ddl)
            print(f"   ✅ Tabela `{name}` OK")
        conn.commit()
        print("✅ Commit após criação de tabelas")

        # 1.1) SE JÁ EXISTIREM sem updated_at, adiciona a coluna
        print("🕑 Garantindo coluna updated_at nas tabelas existentes")
        for name, pk in [('lojas', 'id_loja'), ('clientes', 'id_cliente'), ('pedidos', 'id_pedido')]:
            print(f"   🕑 Checando coluna updated_at em `{name}`")
            cursor.execute(f"""
                IF NOT EXISTS (
                  SELECT 1
                  FROM sys.columns
                  WHERE object_id = OBJECT_ID('dbo.{name}')
                    AND name = 'updated_at'
                )
                BEGIN
                  ALTER TABLE dbo.{name}
                  ADD updated_at DATETIME2(3) NOT NULL CONSTRAINT DF_{name}_updated_at DEFAULT SYSUTCDATETIME();
                END
            """)
            print(f"   ✅ Coluna updated_at OK em `{name}`")
        conn.commit()
        print("✅ Commit após garantir coluna updated_at")

        # 1.2) CRIAR TRIGGERS (se não existirem) para atualizar updated_at em UPDATE
        print("🕑 Garantindo triggers de atualização de updated_at")
        triggers = [
            ('lojas', 'id_loja'),
            ('clientes', 'id_cliente'),
            ('pedidos', 'id_pedido'),
        ]
        for name, pk in triggers:
            trg = f"trg_{name}_set_updated_at"
            print(f"   🕑 Trigger `{trg}`")
            cursor.execute(f"""
                IF NOT EXISTS (
                  SELECT 1 FROM sys.triggers WHERE name = '{trg}'
                )
                BEGIN
                  EXEC('CREATE TRIGGER dbo.{trg} ON dbo.{name}
                    AFTER UPDATE
                    AS
                    BEGIN
                      SET NOCOUNT ON;
                      UPDATE t
                        SET updated_at = SYSUTCDATETIME()
                      FROM dbo.{name} t
                      INNER JOIN inserted i ON t.{pk} = i.{pk};
                    END');
                END
            """)
            print(f"   ✅ Trigger `{trg}` OK")
        conn.commit()
        print("✅ Commit após criação/verificação de triggers")

        # 2) INSERIR LOJAS
        N_LOJAS = 2
        print(f"🕑 Gerando e inserindo {N_LOJAS} lojas")
        lojas = [(fake.company(), fake.city(), fake.estado_sigla()) for _ in range(N_LOJAS)]
        cursor.executemany(
            "INSERT INTO dbo.lojas (nome_loja, cidade, estado) VALUES (%s, %s, %s)",
            lojas
        )
        conn.commit()
        print(f"✅ Lojas inseridas e committed: {lojas}")

        # 3) INSERIR CLIENTES
        N_CLIENTES = 10
        print(f"🕑 Gerando e inserindo {N_CLIENTES} clientes")
        clientes = [
            (fake.name(), fake.email(), fake.phone_number(), fake.date_between(start_date='-5y', end_date='today'))
            for _ in range(N_CLIENTES)
        ]
        cursor.executemany(
            "INSERT INTO dbo.clientes (nome, email, telefone, data_cadastro) VALUES (%s, %s, %s, %s)",
            clientes
        )
        conn.commit()
        print(f"✅ Clientes inseridos e committed: {clientes}")

        # 4) BUSCAR IDS PARA FK
        print("🕑 Buscando IDs de lojas e clientes para pedidos")
        cursor.execute("SELECT id_loja FROM dbo.lojas")
        ids_loja = [row[0] for row in cursor.fetchall()]
        print("   IDs de loja:", ids_loja)

        cursor.execute("SELECT id_cliente FROM dbo.clientes")
        ids_cliente = [row[0] for row in cursor.fetchall()]
        print("   IDs de cliente:", ids_cliente)

        # 5) INSERIR PEDIDOS
        N_PEDIDOS = 20
        print(f"🕑 Gerando e inserindo {N_PEDIDOS} pedidos")
        status_pedidos = ['pago', 'cancelado', 'pendente']
        pedidos = []
        for _ in range(N_PEDIDOS):
            pedidos.append((
                random.choice(ids_cliente),
                random.choice(ids_loja),
                fake.date_between(start_date='-4y', end_date='today'),
                round(random.uniform(50, 1500), 2),
                random.choices(status_pedidos, weights=[0.8,0.1,0.1])[0]
            ))
        cursor.executemany(
            "INSERT INTO dbo.pedidos (id_cliente, id_loja, data_pedido, valor_total, status) VALUES (%s, %s, %s, %s, %s)",
            pedidos
        )
        conn.commit()
        print(f"✅ Pedidos inseridos e committed: {pedidos}")

        # 6) Finalização
        cursor.close()
        conn.close()
        print("🏁 Task inserir_dados finalizada com sucesso")

    inserir_dados()

inserir_dados_fakes_sqlserver = inserir_dados_fakes_sqlserver()
