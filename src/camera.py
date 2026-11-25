
"""
CAMERA.PY

Responsável pela captura das imagens da webcam.
"""

import cv2
from config import CAMERA_INDEX


class Camera:

    def __init__(self):
        """
        Construtor da classe.
        Executado quando criamos Camera().
        """

        self.capture = cv2.VideoCapture(CAMERA_INDEX)

        # Verificar se conseguimos abrir a webcam
        if not self.capture.isOpened():

            self.capture.release()

            raise RuntimeError(
                "Não foi possível abrir a webcam."
            )


    def read(self):
        """
        Captura uma imagem da webcam.

        Devolve:
        - Uma matriz de pixels, se funcionar.
        - None, se não conseguir capturar.
        """

        success, frame = self.capture.read()

        if not success:
            return None

        # Espelhar horizontalmente a imagem
        frame = cv2.flip(frame, 1)

        return frame


    def release(self):
        """
        Liberta os recursos da webcam.
        """

        self.capture.release()
