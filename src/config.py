
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


# ==========================================
# CONFIGURAÇÕES DO MENU
# ==========================================

MENU_DIR = BASE_DIR / "art" / "sprites" / "menu_processado"

# Altura da barra inferior
MENU_HEIGHT = 120

# Margem interna dos botões
MENU_PADDING = 10

# Tamanho máximo dos ícones
MENU_ICON_SIZE = 65

# Cores em formato BGR (OpenCV)
MENU_BACKGROUND = (235, 235, 235)
MENU_BUTTON_COLOR = (255, 255, 255)
MENU_SELECTED_COLOR = (180, 215, 180)
MENU_BORDER_COLOR = (30, 30, 30)

# Associar cada opção à respetiva imagem
MENU_ICONS = {
    "FEED": "Ícone pixelado de garfo e faca-3.png",
    "CLEAN": "Pato de borracha em pixel art.png",
    "PLAY": "Ícone Pixelado de Beisebol e Taco.png"
}

# ==========================================
# CONFIGURAÇÕES DAS NECESSIDADES
# ==========================================

# !!! ALTERAR PARA TRUE DURANTE A APRESENTAÇÃO !!!
MODO_DEMONSTRACAO = False

# Duração padrão configurável pelo utilizador
DURACAO_NECESSIDADES_HORAS = 14

# Duração acelerada para apresentar ao professor
DURACAO_DEMONSTRACAO_SEGUNDOS = 60

# Velocidade relativa de diminuição
TAXA_SACIEDADE = 1.0
TAXA_HIGIENE = 0.7
TAXA_FELICIDADE = 0.5

# ==========================================
# CONFIGURAÇÕES DOS LOGS
# ==========================================

INTERVALO_LOG_NECESSIDADES = 5