from pathlib import Path
from collections import deque
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
ART_DIR = BASE_DIR / "art"
ORIGINAIS_DIR = ART_DIR / "originais"
SPRITES_DIR = ART_DIR / "sprites"

MAMETCHI_IN = ORIGINAIS_DIR / "mametchi"
ACTIONS_IN = ORIGINAIS_DIR / "actions"
MENU_IN = SPRITES_DIR / "menu"   # já tens estes ficheiros aqui

MAMETCHI_OUT = SPRITES_DIR / "mametchi"
ACTIONS_OUT = SPRITES_DIR / "actions"
MENU_OUT = SPRITES_DIR / "menu_processado"

THRESHOLD = 235  # considera fundo "muito claro"


def is_light_pixel(rgba):
    r, g, b, a = rgba
    return a > 0 and r >= THRESHOLD and g >= THRESHOLD and b >= THRESHOLD


def remove_background_from_borders(image: Image.Image) -> Image.Image:
    """
    Remove apenas o fundo claro ligado às bordas.
    Assim preservamos detalhes claros internos que não façam parte do fundo.
    """
    img = image.convert("RGBA")
    pixels = img.load()
    width, height = img.size

    visited = [[False for _ in range(height)] for _ in range(width)]
    q = deque()

    # adicionar pixeis das bordas
    for x in range(width):
        q.append((x, 0))
        q.append((x, height - 1))
    for y in range(height):
        q.append((0, y))
        q.append((width - 1, y))

    while q:
        x, y = q.popleft()

        if x < 0 or y < 0 or x >= width or y >= height:
            continue
        if visited[x][y]:
            continue

        visited[x][y] = True
        px = pixels[x, y]

        if is_light_pixel(px):
            pixels[x, y] = (255, 255, 255, 0)

            q.append((x + 1, y))
            q.append((x - 1, y))
            q.append((x, y + 1))
            q.append((x, y - 1))

    return img


def crop_transparent(image: Image.Image) -> Image.Image:
    bbox = image.getbbox()
    if bbox is None:
        return image
    return image.crop(bbox)


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def process_single_image(input_path: Path) -> Image.Image:
    img = Image.open(input_path).convert("RGBA")
    img = remove_background_from_borders(img)
    img = crop_transparent(img)
    return img


def normalize_to_canvas(images: list[tuple[str, Image.Image]], out_dir: Path):
    """
    Coloca todas as imagens na mesma tela, alinhadas ao centro inferior,
    para evitar 'saltos' durante a animação.
    """
    ensure_dir(out_dir)

    max_w = max(img.width for _, img in images)
    max_h = max(img.height for _, img in images)

    for name, img in images:
        canvas = Image.new("RGBA", (max_w, max_h), (255, 255, 255, 0))

        x = (max_w - img.width) // 2
        y = max_h - img.height  # alinhamento na base

        canvas.alpha_composite(img, (x, y))
        canvas.save(out_dir / name)


def process_folder_normalized(input_dir: Path, out_dir: Path):
    files = sorted([p for p in input_dir.iterdir() if p.suffix.lower() == ".png"])
    processed = []

    for path in files:
        img = process_single_image(path)
        processed.append((path.name, img))

    if processed:
        normalize_to_canvas(processed, out_dir)


def process_folder_simple(input_dir: Path, out_dir: Path):
    ensure_dir(out_dir)
    files = sorted([p for p in input_dir.iterdir() if p.suffix.lower() == ".png"])

    for path in files:
        img = process_single_image(path)
        img.save(out_dir / path.name)


def main():
    print("A preparar sprites...")

    process_folder_normalized(MAMETCHI_IN, MAMETCHI_OUT)
    process_folder_simple(ACTIONS_IN, ACTIONS_OUT)

    # os ícones do menu já estão em art/sprites/menu
    # aqui criamos uma versão limpa/processada noutra pasta
    if MENU_IN.exists():
        process_folder_simple(MENU_IN, MENU_OUT)

    print("Concluído!")
    print(f"Mametchi processado em: {MAMETCHI_OUT}")
    print(f"Ações processadas em:   {ACTIONS_OUT}")
    print(f"Menu processado em:     {MENU_OUT}")


if __name__ == "__main__":
    main()