"""
HAND_DETECTION.PY

Responsável pela deteção e representação
dos pontos anatómicos da mão.

Conceitos para estudar:
- Landmarks
- Coordenadas normalizadas
- Conversão BGR para RGB
- Tracking temporal
- Transformação de coordenadas
"""

import time
import cv2
import mediapipe as mp

from config import (
    HAND_MODEL_PATH,
    MAX_HANDS,
    HAND_DETECTION_CONFIDENCE,
    HAND_TRACKING_CONFIDENCE
)


class HandDetector:

    def __init__(self):

        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=str(HAND_MODEL_PATH)
            ),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=MAX_HANDS,
            min_hand_detection_confidence=HAND_DETECTION_CONFIDENCE,
            min_tracking_confidence=HAND_TRACKING_CONFIDENCE
        )

        self.detector = (
            mp.tasks.vision.HandLandmarker
            .create_from_options(options)
        )

        self.ultimo_timestamp = -1


    # ======================================
    # DETEÇÃO DA MÃO
    # ======================================

    def detect(self, frame):

        rgb = cv2.cvtColor(
            frame, cv2.COLOR_BGR2RGB
        )

        imagem = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        timestamp = max(
            int(time.monotonic() * 1000),
            self.ultimo_timestamp + 1
        )

        self.ultimo_timestamp = timestamp

        resultado = self.detector.detect_for_video(
            imagem,
            timestamp
        )

        if resultado.hand_landmarks:
            return resultado.hand_landmarks[0]

        return None


    # ======================================
    # CONVERSÃO PARA PIXELS
    # ======================================

    def get_points(self, landmarks, frame):

        if landmarks is None:
            return []

        altura, largura = frame.shape[:2]

        return [
            (
                int(ponto.x * largura),
                int(ponto.y * altura)
            )
            for ponto in landmarks
        ]


    # ======================================
    # REPRESENTAÇÃO VISUAL
    # ======================================

    def draw(self, frame, landmarks):

        pontos = self.get_points(landmarks, frame)

        if not pontos:
            return frame

        ligacoes = [
            (0, 1), (1, 2), (2, 3), (3, 4),
            (0, 5), (5, 6), (6, 7), (7, 8),
            (5, 9), (9, 10), (10, 11), (11, 12),
            (9, 13), (13, 14), (14, 15), (15, 16),
            (13, 17), (17, 18), (18, 19), (19, 20),
            (0, 17)
        ]

        for inicio, fim in ligacoes:

            cv2.line(
                frame,
                pontos[inicio],
                pontos[fim],
                (180, 215, 180),
                2
            )

        for index, ponto in enumerate(pontos):

            cor = (
                (0, 215, 255)
                if index == 8
                else (100, 220, 100)
            )

            cv2.circle(frame, ponto, 5, cor, -1)

        return frame


    def close(self):

        self.detector.close()