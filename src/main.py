from pathlib import Path
import time
import cv2
import numpy as np
from PIL import Image  # Abrir e converter imagens


# ==========================================
# CONFIGURAÇÕES GLOBAIS
# ==========================================

# Localização da pasta principal do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Localização dos sprites já processados
SPRITES_DIR = BASE_DIR / "art" / "sprites" / "mametchi"

# Imagens utilizadas na animação de caminhada
FRAME_NAMES = ["mametchi_01.png", "mametchi_02.png"]

WINDOW_NAME = "Tamagotchi"

# Configurações do personagem
ALTURA_DESEJADA = 200
VELOCIDADE = 80          # Pixels por segundo
MARGEM = 20              # Distância das extremidades
SWITCH_INTERVAL = 0.35   # Tempo entre sprites da caminhada
DURACAO_VIRAGEM = 0.5    # Tempo que permanece a olhar para o lado


# ==========================================
# 1. CARREGAMENTO DE SPRITES
# ==========================================

def load_sprite(path: Path) -> np.ndarray:
    """
    Recebe o caminho de uma imagem PNG.

    Image.open: abre a imagem.
    convert("RGBA"): garante quatro canais de informação.
    np.array: transforma a imagem numa matriz NumPy.

    Devolve uma matriz com dimensões:
    (altura, largura, 4 canais).
    """

    img = Image.open(path).convert("RGBA")

    return np.array(img)


# ==========================================
# 2. REDIMENSIONAMENTO DE SPRITES
# ==========================================

def resize_sprite(sprite, altura_desejada):
    """
    Redimensiona o sprite mantendo as proporções
    e preservando a estética pixel art.
    """

    # Obter as dimensões originais
    altura, largura = sprite.shape[:2]

    # Calcular o fator de escala
    scale = altura_desejada / altura

    # Calcular a nova largura proporcionalmente
    nova_largura = max(1, int(largura * scale))

    # INTER_NEAREST evita suavizar os pixels
    return cv2.resize(
        sprite,
        (nova_largura, altura_desejada),
        interpolation=cv2.INTER_NEAREST
    )


# ==========================================
# 3. SOBREPOSIÇÃO E TRANSPARÊNCIA
# ==========================================

def overlay_rgba(
    background_bgr: np.ndarray,
    sprite_rgba: np.ndarray,
    x: int,
    y: int
):
    """
    Desenha um sprite RGBA sobre uma imagem BGR.

    x: posição horizontal do sprite.
    y: posição vertical do sprite.
    """

    # Dimensões da webcam
    bg_h, bg_w = background_bgr.shape[:2]

    # Dimensões do sprite
    sp_h, sp_w = sprite_rgba.shape[:2]

    # Verificar se o sprite está fora da imagem
    if x >= bg_w or y >= bg_h:
        return background_bgr

    # CLIPPING:
    # Limitar a região de desenho à área visível
    x1 = max(x, 0)
    y1 = max(y, 0)

    x2 = min(x + sp_w, bg_w)
    y2 = min(y + sp_h, bg_h)

    # Verificar se existe uma região de sobreposição
    if x1 >= x2 or y1 >= y2:
        return background_bgr

    # Calcular as coordenadas correspondentes
    # dentro da imagem do sprite
    sprite_x1 = x1 - x
    sprite_y1 = y1 - y

    sprite_x2 = sprite_x1 + (x2 - x1)
    sprite_y2 = sprite_y1 + (y2 - y1)

    # Recortar a região visível do sprite
    sprite_crop = sprite_rgba[
        sprite_y1:sprite_y2,
        sprite_x1:sprite_x2
    ]

    # Separar o canal Alpha e normalizar de 0-255 para 0-1
    alpha = sprite_crop[:, :, 3:4] / 255.0

    # Obter os três canais de cor
    sprite_rgb = sprite_crop[:, :, :3]

    # Converter RGB para BGR, utilizado pelo OpenCV
    sprite_bgr = sprite_rgb[:, :, ::-1]

    # Converter para números decimais antes dos cálculos
    bg_crop = background_bgr[y1:y2, x1:x2].astype(np.float32)
    sp_crop = sprite_bgr.astype(np.float32)

    # ALPHA BLENDING - ESTUDAR!
    #
    # alpha = 0: mostra apenas a webcam
    # alpha = 1: mostra apenas o sprite
    #
    # Resultado = alpha * sprite + (1 - alpha) * fundo

    blended = (
        alpha * sp_crop + (1 - alpha) * bg_crop
    ).astype(np.uint8)

    # Colocar a região processada na imagem da webcam
    background_bgr[y1:y2, x1:x2] = blended

    return background_bgr


# ==========================================
# 4. INTERFACE - TEXTO
# ==========================================

def draw_label(frame, text):
    """
    Desenha uma caixa de texto sobre a webcam.
    """

    cv2.rectangle(
        frame,
        (10, 10),
        (220, 45),
        (30, 30, 30),
        -1
    )

    cv2.putText(
        frame,
        text,
        (20, 33),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )


# ==========================================
# 5. PROGRAMA PRINCIPAL
# ==========================================

def main():

    # --------------------------------------
    # A. CARREGAR OS SPRITES
    # --------------------------------------

    # Carregar os dois sprites da caminhada
    sprites = [
        resize_sprite(
            load_sprite(SPRITES_DIR / name),
            ALTURA_DESEJADA
        )
        for name in FRAME_NAMES
    ]

    # Carregar o sprite que olha para a esquerda
    olhar_esquerda = resize_sprite(
        load_sprite(SPRITES_DIR / "mametchi_03.png"),
        ALTURA_DESEJADA
    )

    # Carregar o sprite que olha para a direita
    olhar_direita = resize_sprite(
        load_sprite(SPRITES_DIR / "mametchi_04.png"),
        ALTURA_DESEJADA
    )

    # --------------------------------------
    # B. INICIALIZAR A WEBCAM
    # --------------------------------------

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Não foi possível abrir a webcam.")
        camera.release()
        return

    # --------------------------------------
    # C. INICIALIZAR A ANIMAÇÃO
    # --------------------------------------

    current_index = 0

    # Controlar o tempo entre as trocas de sprite
    last_switch = time.monotonic()

    # --------------------------------------
    # D. INICIALIZAR O MOVIMENTO
    # --------------------------------------

    # Posição horizontal inicial
    x = float(MARGEM)

    # Direção do movimento:
    #  1 = direita
    # -1 = esquerda
    direcao = 1

    # Controlar o tempo entre frames da webcam
    tempo_anterior = time.monotonic()

    # Momento até ao qual permanece a virar
    virar_ate = 0

    # Utilizar a maior largura entre os sprites
    # para manter limites consistentes durante a viragem
    sprite_w = max(
        sprite.shape[1]
        for sprite in sprites + [olhar_esquerda, olhar_direita]
    )

    # ======================================
    # E. CICLO PRINCIPAL
    # ======================================

    while True:

        # 1. Capturar uma imagem da webcam
        success, frame = camera.read()

        if not success:
            break

        # 2. Espelhar horizontalmente a imagem
        frame = cv2.flip(frame, 1)

        # 3. Obter as dimensões da webcam
        frame_h, frame_w = frame.shape[:2]

        # ----------------------------------
        # 4. CALCULAR O TEMPO DECORRIDO
        # ----------------------------------

        agora = time.monotonic()

        # Delta Time: tempo entre dois frames
        dt = agora - tempo_anterior

        tempo_anterior = agora

        # ----------------------------------
        # 5. CALCULAR OS LIMITES DO ECRÃ
        # ----------------------------------

        limite_esquerdo = MARGEM

        limite_direito = max(
            MARGEM,
            frame_w - sprite_w - MARGEM
        )

        # ----------------------------------
        # 6. ATUALIZAR A POSIÇÃO
        # ----------------------------------

        # Só pode caminhar quando não está a virar
        if agora >= virar_ate:

            # TRANSLAÇÃO HORIZONTAL - ESTUDAR!
            # Posição = posição anterior + velocidade * direção * tempo
            x += VELOCIDADE * direcao * dt

            # Chegou à extremidade direita
            if direcao == 1 and x >= limite_direito:

                x = limite_direito

                # Passa a caminhar para a esquerda
                direcao = -1

                # Para temporariamente para olhar
                virar_ate = agora + DURACAO_VIRAGEM

            # Chegou à extremidade esquerda
            elif direcao == -1 and x <= limite_esquerdo:

                x = limite_esquerdo

                # Passa a caminhar para a direita
                direcao = 1

                # Para temporariamente para olhar
                virar_ate = agora + DURACAO_VIRAGEM

        # ----------------------------------
        # 7. ESCOLHER A IMAGEM DO MAMETCHI
        # ----------------------------------

        if agora < virar_ate:

            # ESTADO: VIRAGEM

            if direcao == -1:
                sprite = olhar_esquerda
            else:
                sprite = olhar_direita

        else:

            # ESTADO: CAMINHADA

            # Alternar as imagens das perninhas
            if agora - last_switch >= SWITCH_INTERVAL:

                current_index = (
                    current_index + 1
                ) % len(sprites)

                last_switch = agora

            sprite = sprites[current_index]

        # ----------------------------------
        # 8. CALCULAR A POSIÇÃO VERTICAL
        # ----------------------------------

        sprite_h = sprite.shape[0]

        # Manter o personagem na parte inferior
        y = frame_h - sprite_h - MARGEM

        # ----------------------------------
        # 9. DESENHAR O MAMETCHI
        # ----------------------------------

        # A posição interna x é decimal.
        # Para desenhar pixels, convertemos para inteiro.
        frame = overlay_rgba(
            frame,
            sprite,
            int(x),
            y
        )

        # Desenhar o texto informativo
        draw_label(frame, "Mametchi online <3")

        # Apresentar o resultado
        cv2.imshow(WINDOW_NAME, frame)

        # ----------------------------------
        # 10. VERIFICAR O TECLADO
        # ----------------------------------

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    # ======================================
    # F. ENCERRAMENTO DA APLICAÇÃO
    # ======================================

    camera.release()
    cv2.destroyAllWindows()


# Ponto de entrada do programa
if __name__ == "__main__":
    main()
