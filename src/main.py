
"""
MAIN.PY

Tamagotchi Interativo

Responsável apenas pela coordenação
dos diferentes módulos da aplicação.
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


def main():

    # Inicializar os componentes
    mametchi = Mametchi()
    detector = FaceDetector()
    camera = Camera()

    try:

        while True:

            # 1. Capturar a imagem da webcam
            frame = camera.read()

            if frame is None:
                break

            frame_h, frame_w = frame.shape[:2]


            # 2. Detetar o rosto do utilizador
            rosto = detector.detect(frame)

            centro = detector.get_center(rosto)

            rosto_x = (
                centro[0]
                if centro is not None and SEGUIR_UTILIZADOR
                else None
            )


            # 3. Atualizar o comportamento do Mametchi
            mametchi.update(
                frame_w,
                frame_h,
                rosto_x
            )


            # 4. Desenhar a deteção facial (debug)
            if DEBUG_FACE:

                detector.draw(frame, rosto)


            # 5. Desenhar o Mametchi
            frame = mametchi.draw(frame)


            # 6. Apresentar o estado atual
            draw_label(
                frame,
                f"Mametchi: {mametchi.estado}"
            )


            # 7. Apresentar a imagem final
            cv2.imshow(WINDOW_NAME, frame)


            # 8. Pressionar Q para sair
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:

        # Libertar os recursos mesmo que ocorra um erro
        camera.release()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
