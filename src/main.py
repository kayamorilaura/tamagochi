
"""
MAIN.PY

Responsável pela coordenação dos módulos
do Tamagotchi Interativo.
"""

import cv2

from config import (
    WINDOW_NAME,
    DEBUG_FACE,
    SEGUIR_UTILIZADOR
)

from camera import Camera
from pet import Mametchi
from face_detection import FaceDetector
from renderer import draw_label
from menu import Menu


def main():

    # Inicializar os componentes da aplicação
    mametchi = Mametchi()
    detector = FaceDetector()
    menu = Menu()
    camera = Camera()

    try:

        while True:

            # 1. CAPTURAR A WEBCAM

            frame = camera.read()

            if frame is None:
                break

            frame_h, frame_w = frame.shape[:2]


            # 2. DETETAR O UTILIZADOR

            rosto = detector.detect(frame)

            centro = detector.get_center(rosto)

            rosto_x = (
                centro[0]
                if centro is not None and SEGUIR_UTILIZADOR
                else None
            )


            # 3. ATUALIZAR O MAMETCHI

            mametchi.update(
                frame_w,
                frame_h,
                rosto_x,
                espaco_menu=menu.altura_ocupada()
            )


            # 4. MOSTRAR A DETEÇÃO FACIAL

            if DEBUG_FACE:
                detector.draw(frame, rosto)


            # 5. DESENHAR A INTERFACE

            frame = mametchi.draw(frame)

            frame = menu.draw(frame)

            draw_label(
                frame,
                f"Mametchi: {mametchi.estado}"
            )


            # 6. APRESENTAR A IMAGEM FINAL

            cv2.imshow(WINDOW_NAME, frame)


            # 7. INTERAÇÕES TEMPORÁRIAS POR TECLADO

            key = cv2.waitKey(1) & 0xFF

            # Encerrar a aplicação
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

        camera.release()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
