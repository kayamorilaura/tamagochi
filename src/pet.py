
"""
PET.PY

Responsável pelo comportamento do Mametchi.

Conceitos para estudar:
- Programação orientada a objetos
- Atributos e métodos
- Máquina de estados
- Translação
- Delta Time
- Animação temporal
- Distância e tolerância
"""

import time

from config import (
    SPRITES_DIR,
    FRAME_NAMES,
    SPRITE_ESQUERDA,
    SPRITE_DIREITA,
    SPRITE_IDLE,
    SPRITE_FELIZ,
    ALTURA_DESEJADA,
    MARGEM,
    VELOCIDADE,
    SWITCH_INTERVAL,
    DURACAO_VIRAGEM,
    DISTANCIA_TOLERANCIA,
    DISTANCIA_RETORNO,
    DURACAO_FELICIDADE,
    TEMPO_PERDER_ROSTO,
    INTERVALO_PISCAR,
    DURACAO_PISCAR
)

from renderer import (
    load_sprite,
    resize_sprite,
    overlay_rgba
)


class Mametchi:

    def __init__(self):
        """
        Inicializa todos os atributos do personagem.

        Executado apenas uma vez, quando criamos
        um objeto Mametchi().
        """

        # POSIÇÃO E MOVIMENTO

        self.x = float(MARGEM)
        self.y = 0

        self.velocidade = VELOCIDADE

        # 1 = direita | -1 = esquerda
        self.direcao = 1


        # ESTADOS DO PERSONAGEM

        self.estado = "WANDERING"

        self.virar_ate = 0
        self.feliz_ate = 0

        self.chegou = False


        # TEMPORIZADORES

        agora = time.monotonic()

        self.tempo_anterior = agora
        self.last_switch = agora
        self.inicio_idle = agora

        self.current_index = 0


        # DETEÇÃO DO UTILIZADOR

        self.ultimo_rosto_x = None
        self.ultima_deteccao = 0


        # CARREGAMENTO DOS SPRITES

        self.carregar_sprites()

        self.sprite_atual = self.sprites_caminhada[0]


    # ======================================
    # CARREGAMENTO DAS IMAGENS
    # ======================================

    def carregar_sprites(self):
        """
        Carrega todas as imagens necessárias
        e redimensiona-as apenas uma vez.
        """

        def carregar(nome):

            sprite = load_sprite(SPRITES_DIR / nome)

            return resize_sprite(
                sprite,
                ALTURA_DESEJADA
            )

        # Sprites da caminhada
        self.sprites_caminhada = [
            carregar(nome)
            for nome in FRAME_NAMES
        ]

        # Sprites dos diferentes comportamentos
        self.sprite_esquerda = carregar(SPRITE_ESQUERDA)
        self.sprite_direita = carregar(SPRITE_DIREITA)

        self.sprite_idle = carregar(SPRITE_IDLE)
        self.sprite_feliz = carregar(SPRITE_FELIZ)

        # Maior largura entre todos os sprites
        # Garante limites horizontais consistentes
        todos = self.sprites_caminhada + [
            self.sprite_esquerda,
            self.sprite_direita,
            self.sprite_idle,
            self.sprite_feliz
        ]

        self.largura = max(
            sprite.shape[1]
            for sprite in todos
        )


    # ======================================
    # ANIMAÇÃO DAS PERNAS
    # ======================================

    def animar_caminhada(self, agora):
        """
        Alterna entre os dois frames da caminhada.
        """

        if agora - self.last_switch >= SWITCH_INTERVAL:

            self.current_index = (
                self.current_index + 1
            ) % len(self.sprites_caminhada)

            self.last_switch = agora

        self.sprite_atual = self.sprites_caminhada[
            self.current_index
        ]


    # ======================================
    # VIRAGEM
    # ======================================

    def virar(self, nova_direcao, agora):
        """
        Altera a direção do personagem
        e inicia uma pequena pausa.
        """

        self.direcao = nova_direcao

        self.virar_ate = agora + DURACAO_VIRAGEM

        self.estado = "TURNING"

        self.mostrar_viragem()


    def mostrar_viragem(self):
        """
        Escolhe a imagem lateral correspondente.
        """

        if self.direcao == -1:
            self.sprite_atual = self.sprite_esquerda
        else:
            self.sprite_atual = self.sprite_direita


    # ======================================
    # CAMINHADA AUTÓNOMA
    # ======================================

    def caminhar(self, dt, agora, limite_direito):
        """
        Caminha entre as extremidades do ecrã
        quando não existe um rosto detetado.
        """

        # Se ainda está a virar, não caminhar
        if agora < self.virar_ate:

            self.estado = "TURNING"
            self.mostrar_viragem()

            return

        self.estado = "WANDERING"

        # TRANSLAÇÃO HORIZONTAL
        # x = x + velocidade * direção * tempo
        self.x += self.velocidade * self.direcao * dt

        # Chegou à extremidade direita
        if self.direcao == 1 and self.x >= limite_direito:

            self.x = limite_direito

            self.virar(-1, agora)

        # Chegou à extremidade esquerda
        elif self.direcao == -1 and self.x <= MARGEM:

            self.x = MARGEM

            self.virar(1, agora)

        else:

            self.animar_caminhada(agora)


    # ======================================
    # ACOMPANHAR O UTILIZADOR
    # ======================================

    def seguir(self, rosto_x, dt, agora, limite_direito):
        """
        Caminha em direção ao centro do rosto.

        O Mametchi continua na parte inferior
        do ecrã. Apenas altera a coordenada X.
        """

        # Calcular a posição de destino para alinhar
        # o centro do personagem com o rosto
        destino = rosto_x - self.largura / 2

        # Garantir que o destino é acessível
        destino = max(MARGEM, destino)
        destino = min(limite_direito, destino)

        # Distância entre a posição atual e o destino
        distancia = destino - self.x

        # Usar duas tolerâncias diferentes evita
        # mudanças de estado demasiado frequentes
        tolerancia = (
            DISTANCIA_RETORNO
            if self.chegou
            else DISTANCIA_TOLERANCIA
        )

        # Já está suficientemente perto do utilizador
        if abs(distancia) <= tolerancia:

            # Cancelar qualquer viragem pendente
            self.virar_ate = 0

            self.descansar(agora)

            return

        # Ainda precisa caminhar
        self.chegou = False

        # Determinar a direção do movimento
        nova_direcao = 1 if distancia > 0 else -1

        # Se precisa mudar de direção, primeiro vira-se
        if nova_direcao != self.direcao:

            self.virar(nova_direcao, agora)

            return

        # Aguardar o fim da viragem
        if agora < self.virar_ate:

            self.estado = "TURNING"
            self.mostrar_viragem()

            return

        self.estado = "FOLLOWING"

        # Limitar o passo para não ultrapassar o destino
        passo = min(
            self.velocidade * dt,
            abs(distancia)
        )

        self.x += passo * self.direcao

        self.animar_caminhada(agora)


    # ======================================
    # FELICIDADE E DESCANSO
    # ======================================

    def descansar(self, agora):
        """
        Quando alcança o utilizador:
        1. Fica feliz.
        2. Permanece parado.
        3. Pisca os olhos ocasionalmente.
        """

        # Primeira vez que chegou ao destino
        if not self.chegou:

            self.chegou = True

            self.feliz_ate = agora + DURACAO_FELICIDADE

            self.inicio_idle = self.feliz_ate


        # Mostrar felicidade temporariamente
        if agora < self.feliz_ate:

            self.estado = "HAPPY"

            self.sprite_atual = self.sprite_feliz

        else:

            self.estado = "IDLE"

            # Calcular o tempo no ciclo de descanso
            ciclo = (
                agora - self.inicio_idle
            ) % INTERVALO_PISCAR

            # Mostrar os olhos fechados durante
            # uma pequena fração do tempo
            if ciclo >= INTERVALO_PISCAR - DURACAO_PISCAR:

                self.sprite_atual = self.sprite_idle

            else:

                self.sprite_atual = self.sprites_caminhada[0]


    # ======================================
    # ATUALIZAR O PERSONAGEM
    # ======================================

    def update(
    self,
    frame_w,
    frame_h,
    rosto_x=None,
    espaco_menu=0
):
        """
        Método principal do comportamento.

        Decide se o Mametchi deve:
        - Passear sozinho
        - Virar-se
        - Seguir o utilizador
        - Ficar feliz
        - Descansar

        Executado uma vez por frame da webcam.
        """

        agora = time.monotonic()

        # DELTA TIME
        # Tempo decorrido desde a última atualização

        dt = agora - self.tempo_anterior

        # Evitar saltos grandes caso o programa bloqueie
        dt = min(dt, 0.1)

        self.tempo_anterior = agora


        # LIMITES DO ECRÃ

        limite_direito = max(
            MARGEM,
            frame_w - self.largura - MARGEM
        )

        # Manter o personagem dentro dos limites
        self.x = max(MARGEM, self.x)
        self.x = min(limite_direito, self.x)


        # MEMÓRIA DA ÚLTIMA DETEÇÃO

        if rosto_x is not None:

            self.ultimo_rosto_x = rosto_x
            self.ultima_deteccao = agora

        elif agora - self.ultima_deteccao > TEMPO_PERDER_ROSTO:

            self.ultimo_rosto_x = None


        # DECIDIR O COMPORTAMENTO

        if self.ultimo_rosto_x is not None:

            self.seguir(
                self.ultimo_rosto_x,
                dt,
                agora,
                limite_direito
            )

        else:

            self.chegou = False

            self.caminhar(
                dt,
                agora,
                limite_direito
            )


        # Manter o personagem na parte inferior
        # Descontar o espaço ocupado pelo menu
        # para o Mametchi caminhar sempre acima dele.

        self.y = (
            frame_h
            - self.sprite_atual.shape[0]
            - MARGEM
            - espaco_menu
        )


    # ======================================
    # DESENHAR O PERSONAGEM
    # ======================================

    def draw(self, frame):
        """
        Solicita ao renderer que desenhe
        o sprite atual na posição do Mametchi.
        """

        # Centrar sprites de larguras diferentes
        largura_atual = self.sprite_atual.shape[1]

        offset = (self.largura - largura_atual) / 2

        return overlay_rgba(
            frame,
            self.sprite_atual,
            int(self.x + offset),
            int(self.y)
        )
