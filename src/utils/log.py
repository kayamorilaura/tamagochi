"""
LOG.PY

Responsável pelo registo centralizado
dos eventos da aplicação.
"""

import logging


# CONFIGURAÇÃO DO LOGGER

logging.basicConfig(
    level=logging.WARNING,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

logger = logging.getLogger("Tamagotchi")
# Ativar DEBUG apenas para a nossa aplicação
logger.setLevel(logging.DEBUG)


# NECESSIDADES DO PERSONAGEM

def log_necessidades(saciedade, higiene, felicidade):

    logger.debug(
        f"Saciedade: {saciedade:.2f}% | "
        f"Higiene: {higiene:.2f}% | "
        f"Felicidade: {felicidade:.2f}%"
    )

# ======================================
# RECONHECIMENTO DE GESTOS
# ======================================

def log_gesto(gesto):

    logger.debug(f"Gesto reconhecido: {gesto}")