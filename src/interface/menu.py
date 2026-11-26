
"""
MENU.PY

Responsável pela interface interativa do Tamagotchi.

Conceitos para estudar:
- Coordenadas espaciais
- Divisão de regiões da imagem
- Sobreposição de elementos gráficos
- Deteção de colisão entre ponto e retângulo
- Estados de interface
"""

import cv2

from config import (
    MENU_DIR,
    MENU_HEIGHT,
    MENU_PADDING,
    MENU_ICON_SIZE,
    MENU_BACKGROUND,
    MENU_BUTTON_COLOR,
    MENU_SELECTED_COLOR,
    MENU_BORDER_COLOR,
    MENU_ICONS
)

from interface.renderer import load_sprite, overlay_rgba


class Menu:

    def __init__(self):
        """
        Inicializa os atributos do menu.
        """

        # O menu começa fechado
        self.visivel = False

        # Lista das opções disponíveis
        self.opcoes = list(MENU_ICONS.keys())

        # Nenhuma opção selecionada inicialmente
        self.selecionado = None

        # Guardar as regiões dos botões
        self.botoes = {}

        # Guardar os sprites dos ícones
        self.icones = {}

        self.carregar_icones()


    # ======================================
    # CARREGAMENTO DOS ÍCONES
    # ======================================

    def carregar_icones(self):
        """
        Carrega e redimensiona as imagens
        do menu apenas uma vez.
        """

        for opcao, nome in MENU_ICONS.items():

            caminho = MENU_DIR / nome

            if not caminho.exists():

                print(f"Icone nao encontrado: {caminho}")

                continue

            sprite = load_sprite(caminho)

            altura, largura = sprite.shape[:2]

            # Ajustar o maior lado ao tamanho máximo,
            # preservando as proporções da imagem.
            escala = MENU_ICON_SIZE / max(altura, largura)

            nova_largura = max(1, round(largura * escala))
            nova_altura = max(1, round(altura * escala))

            sprite = cv2.resize(
                sprite,
                (nova_largura, nova_altura),
                interpolation=cv2.INTER_NEAREST
            )

            self.icones[opcao] = sprite


    # ======================================
    # VISIBILIDADE DO MENU
    # ======================================

    def toggle(self):
        """
        Alterna entre aberto e fechado.
        """

        self.visivel = not self.visivel

        if not self.visivel:
            self.selecionado = None
            self.botoes.clear()


    def altura_ocupada(self):
        """
        Devolve a altura ocupada pelo menu.

        Permite ao Mametchi saber quanto espaço
        está disponível para caminhar.
        """

        if self.visivel:
            return MENU_HEIGHT

        return 0


    # ======================================
    # SELEÇÃO DE OPÇÕES
    # ======================================

    def selecionar(self, opcao):
        """
        Guarda a opção selecionada.
        """

        if self.visivel and opcao in self.opcoes:

            self.selecionado = opcao

            print(f"Opcao selecionada: {opcao}")


    def detectar_botao(self, x, y):
        """
        Verifica se um ponto (x, y) está
        dentro de algum dos botões.

        Futuramente, x e y serão as coordenadas
        da ponta do dedo indicador.
        """

        if not self.visivel:
            return None

        for opcao, limites in self.botoes.items():

            x1, y1, x2, y2 = limites

            if x1 <= x <= x2 and y1 <= y <= y2:

                return opcao

        return None


    # ======================================
    # DESENHAR O MENU
    # ======================================

    def draw(self, frame):
        """
        Desenha todos os elementos do menu
        sobre a imagem da webcam.
        """

        if not self.visivel:
            return frame

        frame_h, frame_w = frame.shape[:2]

        # Coordenada vertical onde começa o menu
        menu_y = frame_h - MENU_HEIGHT

        # Desenhar o fundo da barra inferior
        cv2.rectangle(
            frame,
            (0, menu_y),
            (frame_w - 1, frame_h - 1),
            MENU_BACKGROUND,
            -1
        )

        # Dividir horizontalmente em três regiões
        largura_regiao = frame_w // len(self.opcoes)

        self.botoes.clear()

        for index, opcao in enumerate(self.opcoes):

            # Limites de cada botão
            x1 = index * largura_regiao + MENU_PADDING
            x2 = (index + 1) * largura_regiao - MENU_PADDING

            y1 = menu_y + MENU_PADDING
            y2 = frame_h - MENU_PADDING

            # Guardar as coordenadas para futuras interações
            self.botoes[opcao] = (x1, y1, x2, y2)

            # Escolher a cor dependendo da seleção
            cor = (
                MENU_SELECTED_COLOR
                if self.selecionado == opcao
                else MENU_BUTTON_COLOR
            )

            # Fundo do botão
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                cor,
                -1
            )

            # Contorno do botão
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                MENU_BORDER_COLOR,
                2
            )

            # ==============================
            # DESENHAR O ÍCONE
            # ==============================

            sprite = self.icones.get(opcao)

            if sprite is not None:

                icon_h, icon_w = sprite.shape[:2]

                # Centrar horizontalmente o ícone
                icon_x = (x1 + x2 - icon_w) // 2

                icon_y = y1 + 5

                frame = overlay_rgba(
                    frame,
                    sprite,
                    icon_x,
                    icon_y
                )

            # ==============================
            # DESENHAR O TEXTO
            # ==============================

            fonte = cv2.FONT_HERSHEY_SIMPLEX

            (text_w, text_h), _ = cv2.getTextSize(
                opcao,
                fonte,
                0.5,
                1
            )

            # Centrar o texto no botão
            text_x = (x1 + x2 - text_w) // 2
            text_y = y2 - 8

            cv2.putText(
                frame,
                opcao,
                (text_x, text_y),
                fonte,
                0.5,
                MENU_BORDER_COLOR,
                1,
                cv2.LINE_AA
            )

        return frame
