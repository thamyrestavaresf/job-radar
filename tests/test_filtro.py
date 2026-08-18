"""Testes automatizados da camada de filtro."""

import pytest

from core.job import Job, extrair_escopo_remoto
from core.perfis import PERFIL_BR, PERFIL_INTL


CASOS_ESCOPO = [
    ("uf-ambigua-al-maceio", "Remoto (Maceió, AL)", "", {"Brasil"}),
    ("uf-ambigua-ma-sao-luis", "Remoto (São Luís, MA)", "", {"Brasil"}),
    ("uf-ambigua-mt-cuiaba", "Remoto (Cuiabá, MT)", "", {"Brasil"}),
    ("uf-ambigua-ms-campo-grande", "Remoto (Campo Grande, MS)", "", {"Brasil"}),
    ("uf-ambigua-pa-belem", "Remoto (Belém, PA)", "", {"Brasil"}),
    ("uf-ambigua-sc-florianopolis", "Remoto (Florianópolis, SC)", "", {"Brasil"}),
    ("uf-ambigua-sem-capital-br-continua-eua", "Remote (Anytown, AL)", "", {"Estados Unidos"}),
    ("uf-nao-ambigua-resolve-direto", "Remoto (Recife, PE)", "", {"Brasil"}),
    ("hifen-sao-paulo-sem-parenteses", "São Paulo - SP", "Remoto", {"Brasil"}),
    ("hifen-fortaleza-sem-parenteses", "Fortaleza - CE", "Remoto", {"Brasil"}),
    ("hifen-uf-ambigua-sc-florianopolis", "Florianópolis - SC", "Remoto", {"Brasil"}),
    ("porto-alegre-com-uf-nao-vira-portugal", "Remoto (Porto Alegre, RS)", "", {"Brasil"}),
    ("porto-alegre-sem-uf-nao-vira-portugal", "Remoto (Porto Alegre)", "Remoto", {"Brasil"}),
    ("santiago-do-cacem-nao-vira-chile", "Remoto (Santiago do Cacém)", "Remoto", {"santiago do cacem"}),
    ("porto-sozinho-continua-portugal", "Remoto (Porto)", "Remoto", {"Portugal"}),
    ("santiago-sozinho-continua-chile", "Remoto (Santiago)", "Remoto", {"Chile"}),
    ("multimercado-brazil-barra-latam", "Remote - Brazil/LATAM", "", {"Brasil", "LATAM"}),
    ("multimercado-latam-mais-brazil", "Remote - LATAM + Brazil", "", {"Brasil", "LATAM"}),
    ("modalidade-remoto-sem-complemento-sem-escopo", "Remoto", "Remoto", set()),
    ("placeholder-nao-informado-sem-escopo", "Não informado", "Remoto", set()),
    ("placeholder-nao-informado-com-remoto-sem-escopo", "Não informado (Remoto)", "Remoto", set()),
    ("home-office-sem-escopo", "Home Office", "Remoto", set()),
    ("greater-buenos-aires", "Greater Buenos Aires", "Remoto", {"Argentina"}),
    ("madrid-provincia-duplicado", "Madrid, Madrid provincia", "Remoto", {"Espanha"}),
    ("cep-espanhol-na-frente", "08015, Barcelona, Barcelona provincia", "Remoto", {"Espanha"}),
    ("medellin-metropolitan-area", "Medellín Metropolitan Area", "Remoto", {"Colômbia"}),
    ("sigla-mexico-nl-monterrey", "Monterrey, N.L.", "Remoto", {"México"}),
    ("sigla-mexico-cdmx", "Cuauhtémoc, CDMX", "Remoto", {"México"}),
    ("regiao-br-barueri-mais-cidades", "Remoto (Barueri + 35 cidades)", "", set()),
    ("greater-seattle-area-continua-barrada", "Greater Seattle Area", "Remoto", {"seattle"}),
    ("anywhere-sem-restricao", "Remote (Anywhere)", "", set()),
    ("worldwide-sem-restricao", "Remote - Worldwide", "", set()),
    ("pais-nao-mapeado-fica-desconhecido", "Remote - Vietnam", "", {"vietnam"}),
    ("us-only-classico", "Remote — US only", "", {"Estados Unidos"}),
    ("brazil-based", "Remote, Brazil based", "", {"Brasil"}),
    ("pais-depois-da-cidade", "Remote - Florida, United States", "", {"Estados Unidos"}),
]


@pytest.mark.parametrize(
    "nome,local,modalidade,esperado",
    CASOS_ESCOPO,
    ids=[caso[0] for caso in CASOS_ESCOPO],
)
def test_extrair_escopo_remoto(nome, local, modalidade, esperado):
    assert extrair_escopo_remoto(local, modalidade) == esperado


CASOS_COMBINA_COM = [
    ("seattle-barrada-perfil-intl", "Senior Data Analyst", "Greater Seattle Area", "Remoto", PERFIL_INTL, False),
    ("spanish-speaking-sem-mercado-passa", "Spanish Speaking Data Analyst", "Remote", "Remoto", PERFIL_INTL, True),
    ("data-analyst-latam-passa", "Data Analyst LATAM", "Remote", "Remoto", PERFIL_INTL, True),
    ("sem-idioma-sem-mercado-barrada", "Senior Data Analyst", "Remote", "Remoto", PERFIL_INTL, False),
    ("mercado-confirmado-dispensa-idioma-no-titulo", "Senior Data Analyst", "Remote - Espanha", "Remoto", PERFIL_INTL, True),
    ("cidade-fora-da-lista-barrada", "Analista de Dados", "Nova York", "Presencial", PERFIL_BR, False),
    ("cargo-fora-do-escopo-barrado", "Vendedor Externo", "Recife, PE", "Presencial", PERFIL_BR, False),
    ("cargo-forte-cidade-aceita-passa", "Analista Financeiro Pleno", "São Paulo, SP", "Presencial", PERFIL_BR, True),
    ("cargo-ambiguo-sem-qualificador-barrado", "Business Analyst", "Recife, PE", "Presencial", PERFIL_BR, False),
    ("cargo-financeiro-cidade-aceita-passa", "Analista de FP&A", "Santos, SP", "Presencial", PERFIL_BR, True),
]


@pytest.mark.parametrize(
    "nome,titulo,local,modalidade,perfil,esperado",
    CASOS_COMBINA_COM,
    ids=[caso[0] for caso in CASOS_COMBINA_COM],
)
def test_combina_com(nome, titulo, local, modalidade, perfil, esperado):
    job = Job(
        titulo=titulo,
        empresa="Teste",
        local=local,
        link=f"https://teste.invalido/{nome}",
        site="Teste",
        modalidade=modalidade,
    )
    assert job.combina_com(perfil.regras) == esperado


CASOS_PUBLICACAO_ANTIGA = [
    ("caso-real-solides-7-meses", "há 7 meses", True),
    ("mes-singular", "há 1 mês", True),
    ("anos-plural", "há 2 anos", True),
    ("ano-singular", "há 1 ano", True),
    ("dias-nao-e-antiga", "há 3 dias", False),
    ("semanas-nao-e-antiga", "há 2 semanas", False),
    ("hoje-nao-e-antiga", "hoje", False),
    ("ontem-nao-e-antiga", "ontem", False),
    ("vazio-nao-e-antiga", "", False),
    ("absoluto-sem-ano-nao-e-antiga", "Publicada em 11/08", False),
]


@pytest.mark.parametrize(
    "nome,publicado_em,esperado",
    CASOS_PUBLICACAO_ANTIGA,
    ids=[caso[0] for caso in CASOS_PUBLICACAO_ANTIGA],
)
def test_publicacao_antiga(nome, publicado_em, esperado):
    job = Job(
        titulo="Analista Financeiro",
        empresa="Teste",
        local="São Paulo, SP",
        link=f"https://teste.invalido/{nome}",
        site="Teste",
        modalidade="Presencial",
        publicado_em=publicado_em,
    )
    assert job.publicacao_antiga == esperado
