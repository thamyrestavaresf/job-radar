from datetime import datetime, timedelta, timezone
import os

import pytest

from scrapers.inhire import InHireScraper, extrair_empresas_inhire


class Resposta:
    def __init__(self, payload, texto=""):
        self.payload = payload
        self.text = texto

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class SessaoFalsa:
    def __init__(self):
        self.headers = {}
        self.chamadas = []

    def get(self, url, headers=None, timeout=None):
        self.chamadas.append((url, headers))
        if "google.com" in url:
            return Resposta(None, 'https://nova.inhire.app/vagas/ https://outra.inhire.app/vagas/')
        if url.endswith("/lean"):
            return Resposta([{"displayName": "Analista Financeiro", "jobId": "abc"}])
        return Resposta({
            "displayName": "Analista Financeiro",
            "tenantName": "Nova Empresa",
            "location": "Recife\nPE\nBR",
            "workplaceType": "Remote",
            "publishedAt": "2026-08-20T10:00:00.000Z",
        })


def test_extrai_empresas_sem_lista_fixa():
    assert extrair_empresas_inhire(
        'https://Hubla.inhire.app/vagas/ e https://brq.inhire.app/vagas/'
    ) == ["brq", "hubla"]


def test_descoberta_consulta_busca_publica():
    scraper = InHireScraper(["analista financeiro"], session=SessaoFalsa())
    assert scraper.descobrir_empresas() == ["nova", "outra"]


def test_converte_resposta_publica_em_job():
    scraper = InHireScraper(["analista financeiro"], session=SessaoFalsa())
    vagas = scraper._buscar_empresa("nova")
    assert len(vagas) == 1
    assert vagas[0].site == "InHire"
    assert vagas[0].empresa == "Nova Empresa"
    assert vagas[0].local == "Recife PE BR"
    assert vagas[0].modalidade == "Remoto"
    assert vagas[0].link == "https://nova.inhire.app/vagas/abc"


def test_cache_expirado_dispara_nova_descoberta(monkeypatch):
    scraper = InHireScraper([], session=SessaoFalsa())
    monkeypatch.setattr("scrapers.inhire.obter_metadado", lambda _: (datetime.now(timezone.utc) - timedelta(hours=25)).isoformat())
    assert scraper._deve_descobrir()


@pytest.mark.skipif(
    os.getenv("INHIRE_TESTE_INTEGRACAO") != "1",
    reason="Teste externo: habilite apenas para consultar a API pública real do InHire.",
)
def test_integracao_publica_hubla():
    """Teste manual contra uma career page real, sem depender do browser."""
    vagas = InHireScraper(["especialista de controladoria"])._buscar_empresa("hubla")
    assert any(vaga.site == "InHire" for vaga in vagas)
