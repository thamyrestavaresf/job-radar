"""Configuração do perfil internacional do JobRadar."""

from core.config import (
    CIDADES_EUROPA_IBERICA,
    DB_PATH,
)


# Cargos financeiros aceitos no perfil internacional, em português, inglês
# e espanhol. Os cargos de Dados/IA que não estão na lista foram removidos.
KEYWORDS_INTL = [
    # Português
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
    # Inglês
    "Financial Analyst",
    "Senior Financial Analyst",
    "Financial Planning Analyst",
    "FP&A Analyst",
    "Financial Controller",
    "Controllership Analyst",
    "Accounts Receivable Analyst",
    "Billing Analyst",
    "Order to Cash Analyst",
    "Treasury Analyst",
    # Espanhol
    "Analista Financiero",
    "Analista Financiera",
    "Analista de Control de Gestión",
    "Analista de Control de Gestion",
    "Analista de Planificación Financiera",
    "Analista de Planificacion Financiera",
    "Analista de Planeación Financiera",
    "Analista de Planeacion Financiera",
    "Analista de FP&A",
    "Analista de Cuentas por Cobrar",
    "Analista de Facturación",
    "Analista de Facturacion",
    "Analista de Billing",
    "Analista de Order to Cash",
    "Analista de Tesorería",
    "Analista de Tesoreria",
    "Tesorería",
    "Tesoreria",
    "Planificación Financiera",
    "Planificacion Financiera",
    "Planeación Financiera",
    "Planeacion Financiera",
]

# Cada cargo também é usado como termo de busca. Os resultados ainda passam
# pelos filtros de vaga remota, país/mercado e idioma abaixo.
TERMOS_BUSCA_INTL = sorted({cargo.lower() for cargo in KEYWORDS_INTL})
TERMOS_POR_CICLO_INTL = 10


# Países em que o LinkedIn pesquisará vagas remotas.
LOCATIONS_INTL = [
    "Spain",
    "Portugal",
    "Mexico",
    "Colombia",
    "Argentina",
    "Chile",
]

# O perfil internacional aceita somente vagas remotas.
CIDADES_INTL = ["Remote", "Remoto"]

# A vaga remota pode estar vinculada a qualquer um destes mercados.
MERCADOS_REMOTO_ACEITOS_INTL = [
    "Portugal",
    "Espanha",
    "México",
    "Colômbia",
    "Argentina",
    "Chile",
    "Peru",
    "Uruguai",
    "Paraguai",
    "Bolívia",
    "Equador",
    "Venezuela",
    "Costa Rica",
    "Panamá",
    "Guatemala",
    "Honduras",
    "El Salvador",
    "Nicarágua",
    "República Dominicana",
    "Porto Rico",
    "Cuba",
    "Angola",
    "Moçambique",
    "Cabo Verde",
    "LATAM",
]

# Quando uma vaga remota não declara país, ela precisa sinalizar um destes
# idiomas ou mercados no título para continuar no perfil internacional.
IDIOMAS_EXIGIDOS_INTL = [
    "spanish",
    "espanol",
    "español",
    "portuguese",
    "português",
    "portugues",
    "latam",
    "latin america",
    "america latina",
    "hispanohablante",
    "lusofono",
    "lusófono",
]

# Vagas presenciais/híbridas na Ibéria permanecem desativadas.
ATIVAR_EIXO_IBERICO = False

# Domínios do Indeed pesquisados pelo scraper internacional.
DOMINIOS_INDEED_INTL = {
    "Espanha": "es.indeed.com",
    "Portugal": "pt.indeed.com",
    "México": "mx.indeed.com",
    "Colômbia": "co.indeed.com",
    "Argentina": "ar.indeed.com",
    "Chile": "cl.indeed.com",
}
