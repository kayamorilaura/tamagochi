"""
GESTURES.PY

Responsável pela interpretação geométrica
dos gestos da mão.

Conceitos para estudar:
- Vetores
- Produto escalar
- Norma de um vetor
- Ângulos entre articulações
- Classificação de gestos
"""

import numpy as np


class GestureRecognizer:

    def calcular_angulo(self, a, b, c):

        a = np.array(a, dtype=float)
        b = np.array(b, dtype=float)
        c = np.array(c, dtype=float)

        # Construir os vetores
        ba = a - b
        bc = c - b

        # Calcular as normas
        norma = np.linalg.norm(ba) * np.linalg.norm(bc)

        if norma == 0:
            return 0

        # Produto escalar
        coseno = np.dot(ba, bc) / norma

        # Evitar erros de precisão numérica
        coseno = np.clip(coseno, -1.0, 1.0)

        # Converter radianos para graus
        return np.degrees(np.arccos(coseno))

    def dedo_estendido(self, pontos, mcp, pip, tip):

        angulo = self.calcular_angulo(
            pontos[mcp],
            pontos[pip],
            pontos[tip]
        )

        return angulo >= 160

        # ======================================
    # RECONHECIMENTO DE GESTOS
    # ======================================

    def reconhecer(self, pontos):

        if pontos is None or len(pontos) != 21:
            return "NONE"

        indicador = self.dedo_estendido(
            pontos, 5, 6, 8
        )

        medio = self.dedo_estendido(
            pontos, 9, 10, 12
        )

        anelar = self.dedo_estendido(
            pontos, 13, 14, 16
        )

        mindinho = self.dedo_estendido(
            pontos, 17, 18, 20
        )

        dedos = [
            indicador,
            medio,
            anelar,
            mindinho
        ]

        # Punho fechado
        if not any(dedos):
            return "FIST"

        # Mão aberta
        if all(dedos):
            return "OPEN_HAND"

        # Apenas o indicador estendido
        if dedos == [True, False, False, False]:
            return "POINTING"

        # Gesto não reconhecido
        return "UNKNOWN"