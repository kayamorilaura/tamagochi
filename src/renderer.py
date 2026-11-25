
"""
RENDERER.PY

Responsável pelo processamento e desenho das imagens.

Conceitos para estudar:
- Matrizes de pixels
- RGB, BGR e RGBA
- Nearest Neighbor
- Clipping
- Alpha Blending
"""

from pathlib import Path
import cv2
import numpy as np
from PIL import Image


def load_sprite(path: Path) -> np.ndarray:
    """
    Abre uma imagem PNG e transforma-a
    numa matriz NumPy com quatro canais RGBA.
    """

    with Image.open(path) as img:
        return np.array(img.convert("RGBA"))


def resize_sprite(sprite, altura_desejada):
    """
    Redimensiona uma imagem mantendo as proporções.

    INTER_NEAREST:
    Interpolação por vizinho mais próximo.
    Preserva a aparência da pixel art.
    """

    altura, largura = sprite.shape[:2]

    # Fator de escala
    scale = altura_desejada / altura

    nova_largura = max(1, int(largura * scale))

    return cv2.resize(
        sprite,
        (nova_largura, altura_desejada),
        interpolation=cv2.INTER_NEAREST
    )


def overlay_rgba(
    background_bgr: np.ndarray,
    sprite_rgba: np.ndarray,
    x: int,
    y: int
):
    """
    Sobrepõe um sprite transparente à webcam.

    background_bgr: imagem da webcam
    sprite_rgba: imagem do personagem
    x: posição horizontal
    y: posição vertical
    """

    # Dimensões das duas imagens
    bg_h, bg_w = background_bgr.shape[:2]
    sp_h, sp_w = sprite_rgba.shape[:2]

    # CLIPPING:
    # Limitar o desenho à região visível da webcam

    x1 = max(x, 0)
    y1 = max(y, 0)

    x2 = min(x + sp_w, bg_w)
    y2 = min(y + sp_h, bg_h)

    # Se não existe sobreposição, não desenhar
    if x1 >= x2 or y1 >= y2:
        return background_bgr

    # Coordenadas correspondentes no sprite
    sprite_x1 = x1 - x
    sprite_y1 = y1 - y

    sprite_x2 = sprite_x1 + (x2 - x1)
    sprite_y2 = sprite_y1 + (y2 - y1)

    # Recortar a região visível do sprite
    sprite_crop = sprite_rgba[
        sprite_y1:sprite_y2,
        sprite_x1:sprite_x2
    ]

    # Separar o canal Alpha
    # Normalizar os valores de 0-255 para 0-1
    alpha = sprite_crop[:, :, 3:4] / 255.0

    # Separar os canais de cor
    sprite_rgb = sprite_crop[:, :, :3]

    # Converter RGB para BGR
    sprite_bgr = sprite_rgb[:, :, ::-1]

    # Converter para float antes dos cálculos
    bg_crop = background_bgr[
        y1:y2, x1:x2
    ].astype(np.float32)

    sp_crop = sprite_bgr.astype(np.float32)

    # ALPHA BLENDING - ESTUDAR!
    #
    # alpha = 0 -> completamente transparente
    # alpha = 1 -> completamente opaco
    #
    # Resultado = alpha * sprite
    #           + (1 - alpha) * fundo

    blended = (
        alpha * sp_crop + (1 - alpha) * bg_crop
    ).astype(np.uint8)

    # Inserir o resultado na imagem da webcam
    background_bgr[y1:y2, x1:x2] = blended

    return background_bgr


def draw_label(frame, text):
    """
    Desenha uma caixa de texto informativa.
    """

    # Calcular automaticamente a largura do texto
    (width, height), baseline = cv2.getTextSize(
        text,
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        1
    )

    # Fundo da caixa
    cv2.rectangle(
        frame,
        (10, 10),
        (width + 30, height + baseline + 30),
        (30, 30, 30),
        -1
    )

    # Texto
    cv2.putText(
        frame,
        text,
        (20, height + 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        1,
        cv2.LINE_AA
    )
