import requests

from core.config import DISCORD_WEBHOOK_URL
from core.logger import get_logger

logger = get_logger()


def enviar_mensagem(texto: str) -> bool:
    """Envia uma mensagem para o canal do Discord configurado pelo Webhook."""
    if not DISCORD_WEBHOOK_URL:
        logger.warning(
            "Discord não configurado (DISCORD_WEBHOOK_URL ausente no ambiente). "
            "Pulando envio."
        )
        return False

    payload = {
        "content": texto,
    }

    try:
        resposta = requests.post(
            DISCORD_WEBHOOK_URL,
            json=payload,
            timeout=10,
        )
        resposta.raise_for_status()
        return True

    except requests.HTTPError as e:
        status = e.response.status_code if e.response is not None else None
        motivo = e.response.reason if e.response is not None else "sem detalhe"
        logger.error(
            f"Erro ao enviar mensagem no Discord: HTTP {status} ({motivo})"
        )
        return False

    except requests.RequestException as e:
        logger.error(
            f"Erro ao enviar mensagem no Discord: {type(e).__name__} "
            "(falha de conexão, sem resposta do servidor)"
        )
        return False


def _linha_relevancia(pontos: int) -> str:
    """Transforma a relevância de 0-10 em estrelas."""
    cheias = (pontos + 1) // 2
    return "⭐" * cheias + "☆" * (5 - cheias) + f" ({pontos}/10)"


def _linha_aviso_antiga(job) -> str:
    """Mostra aviso quando a vaga foi publicada há bastante tempo."""
    if not job.publicacao_antiga:
        return ""

    return f"⚠️ **Postada {job.publicado_em}** — pode já estar preenchida.\n"


def notificar_vaga(job) -> bool:
    """Envia uma nova vaga para o Discord."""

    linha_publicacao = (
        f"**Publicada:** {job.publicado_em}\n"
        if job.publicado_em
        else ""
    )

    linha_modalidade = (
        f"**Modalidade:** {job.modalidade}\n"
        if job.modalidade
        else ""
    )

    texto = (
        f"🚨 **Nova vaga encontrada!**\n\n"
        f"{_linha_aviso_antiga(job)}"
        f"**Relevância:** {_linha_relevancia(job.relevancia)}\n"
        f"**Motivo:** {job.motivo}\n"
        f"**Empresa:** {job.empresa}\n"
        f"**Cargo:** {job.titulo}\n"
        f"**Nível:** {job.senioridade}\n"
        f"**Local:** {job.local}\n"
        f"{linha_modalidade}"
        f"**Site:** {job.site}\n"
        f"{linha_publicacao}\n"
        f"Encontrada agora\n\n"
        f"**Link:**\n{job.link}"
    )

    return enviar_mensagem(texto)


def notificar_vaga_exploratoria(job) -> bool:
    """Envia vaga exploratória para o Discord."""

    linha_modalidade = (
        f"**Modalidade:** {job.modalidade}\n"
        if job.modalidade
        else ""
    )

    texto = (
        f"🧭 **Vaga exploratória (Portugal/Espanha)**\n\n"
        f"{_linha_aviso_antiga(job)}"
        f"**Relevância:** {_linha_relevancia(job.relevancia)}\n"
        f"**Motivo:** {job.motivo}\n"
        f"**Empresa:** {job.empresa}\n"
        f"**Cargo:** {job.titulo}\n"
        f"**Nível:** {job.senioridade}\n"
        f"**Local:** {job.local}\n"
        f"{linha_modalidade}"
        f"**Site:** {job.site}\n\n"
        f"Achada via busca por Portugal/Espanha — modalidade não "
        f"confirmada como remota, pode ser presencial ou híbrida. "
        f"Confirma no link.\n\n"
        f"**Link:**\n{job.link}"
    )

    return enviar_mensagem(texto)


_LIMITE_CHARS_DIGEST = 1900


def montar_digest(vagas: list[tuple], rotulo_perfil: str) -> list[str]:
    """Monta o digest diário em partes compatíveis com o Discord."""

    linhas = [
        f'{"🧭" if exploratoria else "•"} '
        f'{_linha_relevancia(relevancia or 0)} '
        f'[{titulo}]({link}) — {empresa}'
        for titulo, empresa, link, relevancia, exploratoria in vagas
    ]

    partes: list[list[str]] = []
    parte_atual: list[str] = []
    tamanho_atual = 0

    for linha in linhas:
        if parte_atual and tamanho_atual + len(linha) + 1 > _LIMITE_CHARS_DIGEST:
            partes.append(parte_atual)
            parte_atual = []
            tamanho_atual = 0

        parte_atual.append(linha)
        tamanho_atual += len(linha) + 1

    if parte_atual:
        partes.append(parte_atual)

    total_partes = len(partes)
    mensagens = []

    for i, parte in enumerate(partes, start=1):
        cabecalho = (
            f"📋 **Digest diário — {rotulo_perfil}** "
            f"({len(vagas)} vaga(s))"
        )

        if total_partes > 1:
            cabecalho += f" — parte {i}/{total_partes}"

        mensagens.append(
            cabecalho + "\n\n" + "\n".join(parte)
        )

    return mensagens


def enviar_digest(vagas: list[tuple], rotulo_perfil: str) -> bool:
    """Envia todas as partes do digest para o Discord."""

    if not vagas:
        return True

    return all(
        enviar_mensagem(mensagem)
        for mensagem in montar_digest(vagas, rotulo_perfil)
    )


def processar_feedback_pendente():
    """
    Mantido para compatibilidade com o restante do JobRadar.

    O feedback 👍/👎 era específico do Telegram e ainda será adaptado
    posteriormente para o Discord.
    """
    return
