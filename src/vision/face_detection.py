
"""
FACE_DETECTION.PY

Responsável pela deteção facial.

Conceitos para estudar:
- Grayscale
- Haar Cascade
- Bounding Box
- Centro do retângulo
"""

import cv2


class FaceDetector:

    def __init__(self):
        """
        Carregar o classificador facial pré-treinado
        disponibilizado pelo OpenCV.
        """

        caminho = (
            cv2.data.haarcascades
            + "haarcascade_frontalface_default.xml"
        )

        self.classifier = cv2.CascadeClassifier(caminho)

        if self.classifier.empty():
            raise RuntimeError(
                "Não foi possível carregar o classificador facial."
            )


    def detect(self, frame):
        """
        Deteta rostos presentes numa imagem.

        Devolve o maior rosto detetado
        ou None caso não encontre nenhum.
        """

        # Converter a imagem BGR para escala de cinzentos
        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # Detetar possíveis rostos
        faces = self.classifier.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60)
        )

        # Nenhum rosto encontrado
        if len(faces) == 0:
            return None

        # Se existirem vários rostos,
        # selecionar aquele com maior área
        face = max(
            faces,
            key=lambda f: f[2] * f[3]
        )

        x, y, w, h = map(int, face)

        return x, y, w, h


    def get_center(self, face):
        """
        Calcula o centro do retângulo facial.
        """

        if face is None:
            return None

        x, y, w, h = face

        center_x = x + w // 2
        center_y = y + h // 2

        return center_x, center_y


    def draw(self, frame, face):
        """
        Desenha a deteção facial para testes.
        Não altera a lógica do Mametchi.
        """

        if face is None:
            return

        x, y, w, h = face

        # Retângulo verde à volta do rosto
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        # Marcar o centro do rosto
        center = self.get_center(face)

        cv2.circle(
            frame,
            center,
            5,
            (0, 0, 255),
            -1
        )
