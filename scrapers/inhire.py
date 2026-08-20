"""Fonte InHire baseada na API pública das career pages.

O endpoint administrativo ``/jobs/paginated/lean`` documentado pelo InHire
exige credenciais. Já as páginas públicas usam ``/job-posts/public/pages``
com ``X-Tenant``; esta é a superfície pública usada aqui.
"""

import re
import unicodedata
from datetime import datetime, timedelta, timezone
from urllib.parse import quote_plus

import requests

from core.config import INHIRE_DESCOBERTA_INTERVALO_HORAS
from core.job import Job
from core.logger import get_logger
from database.database import (
    definir_metadado,
    listar_empresas_inhire,
    obter_metadado,
    salvar_empresas_inhire,
)
from scrapers.base import BaseScraper

logger = get_logger()

API_URL = "https://api.inhire.app/job-posts/public/pages"
_PADRAO_EMPRESA = re.compile(
    r"https?://([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)\.inhire\.app/vagas/?",
    re.IGNORECASE,
)
_MODALIDADES = {
    "remote": "Remoto", "remoto": "Remoto",
    "hybrid": "Híbrido", "hibrido": "Híbrido", "híbrido": "Híbrido",
    "on site": "Presencial", "onsite": "Presencial", "presencial": "Presencial",
}


def extrair_empresas_inhire(texto: str) -> list[str]:
    """Extrai e normaliza subdomínios InHire de uma página de busca pública."""
    return sorted({slug.lower() for slug in _PADRAO_EMPRESA.findall(texto)})


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    return "".join(char for char in texto if not unicodedata.combining(char))


class InHireScraper(BaseScraper):
    """Descobre career pages indexadas e lê vagas pela API pública do InHire."""

    def __init__(self, termos_busca: list[str], session=None):
        self.termos_busca = termos_busca
        self.session = session or requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (compatible; JobRadar/1.0)",
            "X-Inhire-Client": "web-inhire",
        })

    def buscar_vagas(self) -> list[Job]:
        empresas = listar_empresas_inhire()
        if self._deve_descobrir():
            try:
                novas = self.descobrir_empresas()
                salvar_empresas_inhire(novas)
                definir_metadado("inhire_descoberta_ultima", datetime.now(timezone.utc).isoformat())
                empresas = sorted(set(empresas) | set(novas))
                logger.info(f"[InHire] Descoberta pública encontrou {len(novas)} empresa(s).")
            except requests.RequestException as erro:
                # Uma indisponibilidade do buscador não apaga nem bloqueia o
                # catálogo já persistido; as fontes restantes seguem no main.
                logger.warning(f"[InHire] Falha na descoberta; usando cache: {erro}")

        vagas: list[Job] = []
        for empresa in empresas:
            try:
                vagas.extend(self._buscar_empresa(empresa))
            except requests.RequestException as erro:
                logger.warning(f"[InHire] Falha em {empresa}: {erro}")
            except (KeyError, TypeError, ValueError) as erro:
                logger.warning(f"[InHire] Resposta inválida em {empresa}: {erro}")

        logger.info(f"[InHire] {len(vagas)} vaga(s) encontrada(s) em {len(empresas)} empresa(s).")
        return vagas

    def _deve_descobrir(self) -> bool:
        ultima = obter_metadado("inhire_descoberta_ultima")
        if not ultima:
            return True
        try:
            return datetime.now(timezone.utc) - datetime.fromisoformat(ultima) >= timedelta(
                hours=INHIRE_DESCOBERTA_INTERVALO_HORAS
            )
        except ValueError:
            return True

    def descobrir_empresas(self) -> list[str]:
        """Usa resultados indexados de busca; não há catálogo público InHire."""
        consulta = quote_plus('site:inhire.app/vagas/ -www.inhire.app')
        # Dois índices públicos evitam transformar uma mudança/bloqueio de
        # um buscador em indisponibilidade total da descoberta. O resultado
        # ainda passa pelo mesmo regex e pelo cache SQLite.
        ultimo_erro = None
        for url in (
            f"https://www.google.com/search?q={consulta}&num=100",
            f"https://www.bing.com/search?q={consulta}&count=100",
        ):
            try:
                resposta = self.session.get(url, timeout=30)
                resposta.raise_for_status()
            except requests.RequestException as erro:
                ultimo_erro = erro
                continue
            empresas = extrair_empresas_inhire(resposta.text)
            if empresas:
                return empresas
        if ultimo_erro:
            raise ultimo_erro
        return []

    def _titulo_relevante(self, titulo: str) -> bool:
        titulo_norm = _normalizar(titulo)
        return any(_normalizar(termo) in titulo_norm for termo in self.termos_busca)

    def _buscar_empresa(self, slug: str) -> list[Job]:
        headers = {"X-Tenant": slug}
        lista = self.session.get(f"{API_URL}/lean", headers=headers, timeout=30)
        lista.raise_for_status()
        vagas: list[Job] = []

        for resumo in lista.json():
            titulo = (resumo.get("displayName") or "").strip()
            job_id = resumo.get("jobId")
            # A API enxuta não traz local/modalidade. Reduz chamadas sem
            # mudar o filtro: títulos sem nenhum termo monitorado jamais
            # passam pela regra de cargo deste perfil.
            if not job_id or not titulo or not self._titulo_relevante(titulo):
                continue

            detalhe = self.session.get(f"{API_URL}/{job_id}", headers=headers, timeout=30)
            detalhe.raise_for_status()
            dados = detalhe.json()
            vagas.append(Job(
                titulo=(dados.get("displayName") or titulo).strip(),
                empresa=(dados.get("tenantName") or slug).strip(),
                local=" ".join((dados.get("location") or "Não informado").split()),
                link=f"https://{slug}.inhire.app/vagas/{job_id}",
                site="InHire",
                publicado_em=dados.get("publishedAt") or dados.get("lastPublishedAt") or "",
                modalidade=_MODALIDADES.get(_normalizar(dados.get("workplaceType") or ""), ""),
            ))
        return vagas
