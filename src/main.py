
"""
MAIN.PY

Responsável pela coordenação dos módulos
do Tamagotchi Interativo.
"""

import cv2

from config import (
    WINDOW_NAME,
    DEBUG_FACE,
    DEBUG_HAND,
    SEGUIR_UTILIZADOR
)

# VISAO COMPUTACIONAL
from vision.camera import Camera
from vision.face_detection import FaceDetector
from vision.hand_detection import HandDetector
from vision.gestures import GestureRecognizer

# PERSONAGEM
from pet.pet import Mametchi

# INTERFACE
from interface.renderer import draw_label
from interface.menu import Menu

# LOGS
from utils.log import log_gesto


def main():

    # ======================================
    # INICIALIZAR OS COMPONENTES
    # ======================================

    mametchi = Mametchi()

    detector = FaceDetector()
    hand_detector = HandDetector()
    gesture_recognizer = GestureRecognizer()

    menu = Menu()
    camera = Camera()

    ultimo_gesto = "NONE"

    try:

        while True:

            # ======================================
            # 1. CAPTURAR A WEBCAM
            # ======================================

            frame = camera.read()

            if frame is None:
                break

            frame_h, frame_w = frame.shape[:2]


            # ======================================
            # 2. DETETAR O ROSTO DO UTILIZADOR
            # ======================================

            rosto = detector.detect(frame)

            centro = detector.get_center(rosto)

            rosto_x = (
                centro[0]
                if centro is not None and SEGUIR_UTILIZADOR
                else None
            )


            # ======================================
            # 3. DETETAR A MAO DO UTILIZADOR
            # ======================================

            mao = hand_detector.detect(frame)

            pontos = hand_detector.get_points(
                mao,
                frame
            )


            # ======================================
            # 4. RECONHECER OS GESTOS
            # ======================================

            gesto = gesture_recognizer.reconhecer(
                pontos
            )

            # Registar apenas quando o gesto muda

            if gesto != ultimo_gesto:

                log_gesto(gesto)

                ultimo_gesto = gesto
            # ======================================
            # CONTROLO DO MENU POR GESTOS
            # ======================================

            if gesto == "FIST":

                menu.abrir()

            elif gesto == "OPEN_HAND":

                menu.fechar()


            # ======================================
            # 5. ATUALIZAR O MAMETCHI
            # ======================================

            mametchi.update(
                frame_w,
                frame_h,
                rosto_x,
                espaco_menu=menu.altura_ocupada()
            )


            # ======================================
            # 6. MOSTRAR AS DETECOES
            # ======================================

            if DEBUG_FACE:

                detector.draw(frame, rosto)

            if DEBUG_HAND:

                hand_detector.draw(frame, mao)


            # ======================================
            # 7. DESENHAR A INTERFACE
            # ======================================

            frame = mametchi.draw(frame)

            frame = menu.draw(frame)

            draw_label(
                frame,
                f"Mametchi: {mametchi.estado}"
            )


            # ======================================
            # 8. APRESENTAR A IMAGEM FINAL
            # ======================================

            cv2.imshow(WINDOW_NAME, frame)


            # ======================================
            # 9. INTERACOES TEMPORARIAS POR TECLADO
            # ======================================

            key = cv2.waitKey(1) & 0xFF

            # Encerrar a aplicacao
            if key == ord("q"):

                break

            # Abrir ou fechar o menu
            elif key == ord("m"):

                menu.toggle()

            # Selecionar FEED
            elif key == ord("1"):

                menu.selecionar("FEED")

            # Selecionar CLEAN
            elif key == ord("2"):

                menu.selecionar("CLEAN")

            # Selecionar PLAY
            elif key == ord("3"):

                menu.selecionar("PLAY")


    finally:

        # Libertar os recursos da aplicacao

        hand_detector.close()

        camera.release()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
