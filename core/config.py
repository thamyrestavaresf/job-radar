import os

from dotenv import load_dotenv


load_dotenv()


# Cargos aceitos no perfil Brasil.
KEYWORDS_CARGO_FORTE = [
    "Analista Financeiro Pleno",
    "Analista BI",
    "Analista de BI",
    "Analista Financeiro",
    "Analista Financeiro Sênior",
    "Analista de Analytics",
    "Data Analyst",
    "Analista de Controladoria",
    "Analista de Planejamento Financeiro",
    "Analista de Inteligência de Negócios",
    "Analista de FP&A",
    "Analista de Contas a Receber",
    "Analista de Faturamento",
    "Analista de Billing",
    "Analista de Order to Cash",
    "Tesouraria",
    "FP&A",
    "Financial Planning & Analysis",
    "Analista de Planejamento e Dados",
]

# Não há cargos ambíguos nem filtros por ferramenta neste perfil.
KEYWORDS_CARGO_AMBIGUO = []
QUALIFICADORES_DADOS = []
FERRAMENTAS_TITULO = []
QUALIFICADORES_CARGO = []

KEYWORDS = KEYWORDS_CARGO_FORTE + KEYWORDS_CARGO_AMBIGUO

# A busca usa os próprios cargos acima, sem termos antigos de Dados/BI.
TERMOS_CARGO_EXTRA = []
TERMOS_CARGO = sorted(set(k.lower() for k in KEYWORDS) | set(TERMOS_CARGO_EXTRA))
TERMOS_FERRAMENTA = []
TERMOS_BUSCA = TERMOS_CARGO + TERMOS_FERRAMENTA
TERMOS_POR_CICLO = 10


# Vagas presenciais ou híbridas só são aceitas nestas cidades; vagas remotas
# também são aceitas quando atendem às regras de mercado abaixo.
CIDADES = [
    "Remoto",
    "Campina Grande",
    "João Pessoa",
    "Recife",
    "Natal",
    "Caruaru",
    "Manaus",
    "Maceió",
    "Aracaju",
    "São Paulo",
    "Santos",
]

CIDADES_EUROPA_IBERICA = [
    "Portugal",
    "Lisboa",
    "Porto",
    "Braga",
    "Espanha",
    "España",
    "Spain",
    "Madrid",
    "Barcelona",
    "Valencia",
]

ATIVAR_EIXO_IBERICO_BR = False


# Mercados pesquisados pelo scraper do LinkedIn no perfil Brasil.
LOCATIONS_LINKEDIN = ["Brasil"]
LOCATIONS_LINKEDIN_REMOTO_APENAS = [
    "Argentina",
    "Chile",
    "México",
    "Colômbia",
    "Espanha",
    "Portugal",
]
LOCATIONS_LINKEDIN_CIDADES_PRESENCIAL = [
    cidade for cidade in CIDADES if cidade != "Remoto"
]

MERCADOS_REMOTO_ACEITOS = [
    "Brasil",
    "LATAM",
    "Argentina",
    "Chile",
    "México",
    "Colômbia",
    "Portugal",
    "Espanha",
]


# Execução e notificações.
INTERVALO_MINUTOS = int(os.getenv("INTERVALO_MINUTOS", 180))
LIMIAR_DIGEST_IMEDIATO = 7
DIGEST_HORA_UTC = 9

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
INHIRE_DESCOBERTA_INTERVALO_HORAS = int(os.getenv("INHIRE_DESCOBERTA_INTERVALO_HORAS", 24))

# Descoberta é feita por busca pública e o catálogo fica em SQLite. Este
# intervalo evita consultar o buscador em cada ciclo, mas não impede que as
# empresas já conhecidas sejam verificadas a cada execução do JobRadar.
INHIRE_DESCOBERTA_INTERVALO_HORAS = int(os.getenv("INHIRE_DESCOBERTA_INTERVALO_HORAS", 24))


# Banco de dados ancorado na raiz do projeto.
_RAIZ_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.getenv("JOBRADAR_DB_PATH") or os.path.join(
    _RAIZ_PROJETO, "data", "jobs.db"
)
