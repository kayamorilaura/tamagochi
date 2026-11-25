
"""
CONFIG.PY

Centraliza as configurações da aplicação.
Não contém lógica de execução.
"""

from pathlib import Path


# CAMINHOS DO PROJETO

BASE_DIR = Path(__file__).resolve().parent.parent

SPRITES_DIR = BASE_DIR / "art" / "sprites" / "mametchi"


# CONFIGURAÇÕES DA JANELA

WINDOW_NAME = "Tamagotchi"
CAMERA_INDEX = 0


# CONFIGURAÇÕES VISUAIS

ALTURA_DESEJADA = 200
MARGEM = 20

# Mostrar o retângulo da deteção facial
# True = mostrar | False = esconder
DEBUG_FACE = True


# CONFIGURAÇÕES DO MOVIMENTO

VELOCIDADE = 80          # Pixels por segundo
SWITCH_INTERVAL = 0.35   # Intervalo entre os passos
DURACAO_VIRAGEM = 0.5    # Duração da pose lateral


# COMPORTAMENTO COM O UTILIZADOR

SEGUIR_UTILIZADOR = True

DISTANCIA_TOLERANCIA = 40  # Distância para parar
DISTANCIA_RETORNO = 60     # Distância para voltar a seguir

DURACAO_FELICIDADE = 1.7   # Segundos de felicidade
TEMPO_PERDER_ROSTO = 0.8   # Tolerância a falhas de deteção

INTERVALO_PISCAR = 4.0
DURACAO_PISCAR = 0.2


# SPRITES DO MAMETCHI

FRAME_NAMES = [
    "mametchi_01.png",
    "mametchi_02.png"
]

SPRITE_ESQUERDA = "mametchi_03.png"
SPRITE_DIREITA = "mametchi_04.png"

SPRITE_IDLE = "mametchi_05.png"
SPRITE_FELIZ = "mametchi_08.png"
