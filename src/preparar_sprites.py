
"""
PREPARAR_SPRITES.PY

Responsável pela preparação das imagens originais.

Conceitos de Computação Visual:
- Flood Fill
- Alpha Masking
- Bounding Box
- Cropping
- Scaling
- Nearest Neighbor
- Alinhamento espacial
"""

from pathlib import Path
from collections import deque
from PIL import Image


# ==========================================
# 1. CONFIGURAÇÕES
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent

ART_DIR = BASE_DIR / "art"
ORIGINAIS_DIR = ART_DIR / "originais"
SPRITES_DIR = ART_DIR / "sprites"

# Pastas das imagens originais
MAMETCHI_IN = ORIGINAIS_DIR / "mametchi"
ACTIONS_IN = ORIGINAIS_DIR / "actions"
MENU_IN = SPRITES_DIR / "menu"

# Pastas das imagens processadas
MAMETCHI_OUT = SPRITES_DIR / "mametchi"
ACTIONS_OUT = SPRITES_DIR / "actions"
MENU_OUT = SPRITES_DIR / "menu_processado"

# Configurações do processamento
THRESHOLD = 235
ALTURA_PADRAO = 200


# ==========================================
# 2. IDENTIFICAR PIXELS CLAROS
# ==========================================

def is_light_pixel(rgba):
    """
    Verifica se um pixel é suficientemente claro
    para ser considerado parte do fundo.
    """

    r, g, b, a = rgba

    return (
        a > 0
        and r >= THRESHOLD
        and g >= THRESHOLD
        and b >= THRESHOLD
    )


# ==========================================
# 3. REMOVER O FUNDO
# ==========================================

def remove_background_from_borders(image):
    """
    Remove os pixels claros ligados às bordas.

    Utiliza Flood Fill para preservar os detalhes
    brancos internos do Mametchi.
    """

    img = image.convert("RGBA")

    pixels = img.load()

    width, height = img.size

    # Guardar os pixels já visitados
    visited = set()

    # Fila de pixels a verificar
    queue = deque()

    # Adicionar as bordas horizontais
    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))

    # Adicionar as bordas verticais
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:

        x, y = queue.popleft()

        # Verificar os limites da imagem
        if not (0 <= x < width and 0 <= y < height):
            continue

        if (x, y) in visited:
            continue

        visited.add((x, y))

        pixel = pixels[x, y]

        # Atravessar pixels transparentes ou claros
        if pixel[3] == 0 or is_light_pixel(pixel):

            # Tornar o pixel transparente
            pixels[x, y] = (0, 0, 0, 0)

            # Verificar os quatro pixels vizinhos
            queue.append((x + 1, y))
            queue.append((x - 1, y))
            queue.append((x, y + 1))
            queue.append((x, y - 1))

    return img


# ==========================================
# 4. RECORTAR MARGENS TRANSPARENTES
# ==========================================

def crop_transparent(image):
    """
    Identifica a Bounding Box dos pixels visíveis
    através do canal Alpha.
    """

    bbox = image.getchannel("A").getbbox()

    if bbox is None:
        return image

    return image.crop(bbox)


# ==========================================
# 5. CRIAR DIRETÓRIOS
# ==========================================

def ensure_dir(path: Path):
    """
    Cria uma pasta caso ainda não exista.
    """

    path.mkdir(parents=True, exist_ok=True)


# ==========================================
# 6. PROCESSAR UMA IMAGEM
# ==========================================

def process_single_image(input_path: Path):
    """
    Abre, remove o fundo e recorta uma imagem.
    """

    with Image.open(input_path) as original:

        img = original.convert("RGBA")

    img = remove_background_from_borders(img)

    img = crop_transparent(img)

    return img


# ==========================================
# 7. NORMALIZAR OS SPRITES
# ==========================================

def normalize_to_canvas(images, out_dir: Path):
    """
    Uniformiza a altura visual dos sprites,
    mantendo as proporções originais.

    Todos os sprites ficam centrados
    horizontalmente e alinhados pela base.
    """

    ensure_dir(out_dir)

    imagens_normalizadas = []

    for name, img in images:

        img = img.convert("RGBA")

        # Identificar os pixels visíveis
        bbox = img.getchannel("A").getbbox()

        if bbox is None:
            print(f"Imagem vazia: {name}")
            continue

        # Remover margens transparentes
        img = img.crop(bbox)

        largura, altura = img.size

        # SCALING:
        # Calcular o fator de escala proporcional
        escala = ALTURA_PADRAO / altura

        nova_largura = max(
            1,
            round(largura * escala)
        )

        # NEAREST NEIGHBOR:
        # Preservar a aparência pixel art
        img = img.resize(
            (nova_largura, ALTURA_PADRAO),
            Image.Resampling.NEAREST
        )

        imagens_normalizadas.append((name, img))

    if not imagens_normalizadas:
        return

    # Encontrar a maior largura
    largura_canvas = max(
        img.width
        for _, img in imagens_normalizadas
    )

    altura_canvas = ALTURA_PADRAO

    # Criar uma tela uniforme para cada sprite
    for name, img in imagens_normalizadas:

        canvas = Image.new(
            "RGBA",
            (largura_canvas, altura_canvas),
            (0, 0, 0, 0)
        )

        # Alinhamento horizontal
        x = (largura_canvas - img.width) // 2

        # Alinhamento vertical pela base
        y = altura_canvas - img.height

        # Inserir o sprite na tela transparente
        canvas.alpha_composite(img, (x, y))

        # Guardar o sprite processado
        canvas.save(out_dir / name)

        print(
            f"{name}: "
            f"{canvas.width} x {canvas.height}"
        )


# ==========================================
# 8. PROCESSAR SPRITES DO MAMETCHI
# ==========================================

def process_folder_normalized(input_dir, out_dir):
    """
    Processa e normaliza todas as imagens PNG
    de uma determinada pasta.
    """

    if not input_dir.exists():
        print(f"Pasta não encontrada: {input_dir}")
        return

    files = sorted(input_dir.glob("*.png"))

    processed = []

    for path in files:

        img = process_single_image(path)

        processed.append((path.name, img))

    normalize_to_canvas(processed, out_dir)


# ==========================================
# 9. PROCESSAR AÇÕES E MENU
# ==========================================

def process_folder_simple(input_dir, out_dir):
    """
    Remove o fundo e recorta as imagens,
    sem uniformizar o tamanho.
    """

    if not input_dir.exists():
        return

    ensure_dir(out_dir)

    files = sorted(input_dir.glob("*.png"))

    for path in files:

        img = process_single_image(path)

        img.save(out_dir / path.name)

        print(f"Processado: {path.name}")


# ==========================================
# 10. PROGRAMA PRINCIPAL
# ==========================================

def main():

    print("\nA preparar sprites do Mametchi...\n")

    process_folder_normalized(
        MAMETCHI_IN,
        MAMETCHI_OUT
    )

    print("\nA preparar sprites das ações...\n")

    process_folder_simple(
        ACTIONS_IN,
        ACTIONS_OUT
    )

    print("\nA preparar sprites do menu...\n")

    process_folder_simple(
        MENU_IN,
        MENU_OUT
    )

    print("\nProcessamento concluído!")


if __name__ == "__main__":
    main()
