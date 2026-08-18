"""Regras de negócio vigentes do JobRadar."""

import pytest

from core.job import Job
from core.perfis import PERFIL_BR, PERFIL_INTL


def _vaga(titulo, local, modalidade):
    return Job(
        titulo=titulo,
        empresa="Empresa Teste",
        local=local,
        link=f"https://exemplo.com/{abs(hash((titulo, local, modalidade)))}",
        site="Teste",
        modalidade=modalidade,
    )


# ------------------------------------------------------------------ BRASIL


@pytest.mark.parametrize("modalidade", ["Híbrido", "Presencial"])
@pytest.mark.parametrize("cidade", ["São Paulo", "Santos"])
def test_br_hibrido_e_presencial_so_em_sao_paulo_e_santos(cidade, modalidade):
    assert _vaga(
        "Analista Financeiro", f"{cidade} - SP", modalidade
    ).combina_com(PERFIL_BR.regras)


@pytest.mark.parametrize("modalidade", ["Híbrido", "Presencial"])
@pytest.mark.parametrize(
    "local",
    [
        "Recife - PE",
        "Campina Grande - PB",
        "João Pessoa - PB",
        "Natal - RN",
        "Caruaru - PE",
        "Manaus - AM",
        "Maceió - AL",
        "Aracaju - SE",
    ],
)
def test_br_hibrido_e_presencial_aceito_nas_demais_cidades_da_lista(
    local, modalidade
):
    """CIDADES em core/config.py inclui essas cidades além de SP/Santos —
    vaga presencial/híbrida nelas deve ser aceita."""
    assert _vaga(
        "Analista Financeiro", local, modalidade
    ).combina_com(PERFIL_BR.regras)


@pytest.mark.parametrize(
    "local",
    [
        "São Paulo",
        "São Paulo - SP",
        "São Paulo, SP",
        "SAO PAULO - SP",
        "Santos - SP",
        "Santos, SP",
    ],
)
def test_br_variacoes_de_escrita_das_cidades_aceitas(local):
    assert _vaga(
        "Analista Financeiro", local, "Híbrido"
    ).combina_com(PERFIL_BR.regras)


@pytest.mark.parametrize("modalidade", ["Híbrido", "Presencial"])
@pytest.mark.parametrize(
    "local",
    [
        "Rio de Janeiro - RJ",
        "Belo Horizonte - MG",
        "Salvador - BA",
        "Curitiba - PR",
    ],
)
def test_br_hibrido_e_presencial_fora_da_lista_de_cidades_e_rejeitado(
    local, modalidade
):
    """Cidades fora da lista CIDADES em core/config.py continuam
    rejeitadas para presencial/híbrido (só remoto passa para elas)."""
    assert not _vaga(
        "Analista Financeiro", local, modalidade
    ).combina_com(PERFIL_BR.regras)


@pytest.mark.parametrize(
    "local",
    [
        "Remoto",
        "Remoto (Recife, PE)",
        "Remoto (São Paulo, SP)",
        "Remote, Brazil",
        "Remoto (Manaus, AM)",
    ],
)
def test_br_remoto_e_aceito_de_qualquer_cidade(local):
    assert _vaga(
        "Analista Financeiro", local, "Remoto"
    ).combina_com(PERFIL_BR.regras)


@pytest.mark.parametrize("local", ["Remote - US only", "Remote - India"])
def test_br_remoto_de_mercado_nao_aceito_e_rejeitado(local):
    assert not _vaga(
        "Analista Financeiro", local, "Remoto"
    ).combina_com(PERFIL_BR.regras)


# ----------------------------------------------------------- INTERNACIONAL


@pytest.mark.parametrize(
    "local",
    [
        "Remote - Spain",
        "Remote - Mexico",
        "Remote - Portugal",
        "Remote - Latin America",
        "Remote - Colombia",
        "Buenos Aires, Argentina",
    ],
)
def test_intl_remoto_em_mercado_aceito_e_aceito(local):
    assert _vaga(
        "Financial Analyst", local, "Remoto"
    ).combina_com(PERFIL_INTL.regras)


@pytest.mark.parametrize("modalidade", ["Híbrido", "Presencial"])
@pytest.mark.parametrize("local", ["Madrid, Spain", "Lisboa, Portugal"])
def test_intl_hibrido_e_presencial_sempre_rejeitado(local, modalidade):
    assert not _vaga(
        "Financial Analyst", local, modalidade
    ).combina_com(PERFIL_INTL.regras)


@pytest.mark.parametrize("local", ["Remote - US only", "Remote - India"])
def test_intl_remoto_de_mercado_de_lingua_inglesa_e_rejeitado(local):
    assert not _vaga(
        "Financial Analyst", local, "Remoto"
    ).combina_com(PERFIL_INTL.regras)


def test_intl_remoto_sem_mercado_declarado_exige_idioma_no_titulo():
    assert _vaga(
        "Financial Analyst (Spanish speaker)", "Remote - Worldwide", "Remoto"
    ).combina_com(PERFIL_INTL.regras)
    assert not _vaga(
        "Financial Analyst", "Remote - Worldwide", "Remoto"
    ).combina_com(PERFIL_INTL.regras)


# ------------------------------------------------------------------- CARGO


@pytest.mark.parametrize(
    "titulo,esperado",
    [
        ("Analista Financeiro Pleno", True),
        ("Analista de Controladoria", True),
        ("Analista de FP&A", True),
        ("Analista de Contas a Receber", True),
        ("Vendedor Externo", False),
        ("Business Analyst", False),
        ("Analista de Power BI", False),
        ("Engenheiro de Dados", False),
    ],
)
def test_cargo_no_titulo(titulo, esperado):
    assert _vaga(
        titulo, "São Paulo - SP", "Presencial"
    ).combina_com(PERFIL_BR.regras) is esperado
