"""
SEL0337 - Projetos em Sistemas Embarcados
Pratica 3 / Checkpoint 2 - Programa 2(Sensor de distância)
Arthur Alves da Costa - 13751207
Raphael Franco de Oliveria - 13862393


Indicador de proximidade: um sensor ultrassonico HC-SR04 mede a distancia até
um objeto e uma barra de 5 LEDs mostra o quão perto ele está. Quanto mais
perto, mais LEDs acendem.

    distancia >= 50 cm         -> nenhum LED
    entre 50 cm e 5 cm         -> 1 a 5 LEDs, em 5 faixas iguais de 9 cm
    distancia <= 5 cm          -> 5 LEDs

Usa a biblioteca gpiozero (DistanceSensor + LEDBoard), complementando o
programa de PWM, que usa RPi.GPIO

LIGACAO (numeracao BCM, pino fisico entre parenteses):
    HC-SR04 VCC  -> 5 V         (2)
    HC-SR04 GND  -> GND         (6)
    HC-SR04 Trig -> GPIO8       (14)   
    HC-SR04 Echo -> DIVISOR DE TENSAO -> GPIO25 (22)
    LEDs: GPIO14, GPIO15, GPIO18, GPIO23, GPIO24
          cada um: GPIO -> resistor 220 ohm -> anodo; catodo -> GND
"""

import time

from gpiozero import DistanceSensor, LEDBoard

PINO_TRIGGER = 8
PINO_ECHO = 25
PINOS_LEDS = (14, 15, 18, 23, 24)  

DIST_MIN = 0.05       # m  : a partir daqui (mais perto) todos os LEDs acesos
DIST_MAX = 0.50       # m  : a partir daqui (mais longe) nenhum LED aceso
ALCANCE_SENSOR = 1.0  # m  : distancia maxima reportada pelo DistanceSensor
PERIODO_LEITURA = 0.1 # s  : intervalo entre atualizacoes da barra

NUM_LEDS = len(PINOS_LEDS)


def leds_para_distancia(distancia):
    """Converte a distancia em metros no numero de LEDs a acender (0 a 5).

    O intervalo [DIST_MIN, DIST_MAX] e dividido em NUM_LEDS faixas iguais.
    A fração de proximidade vale 0 no limite distante e 1 no limite próximo;
    cada faixa ultrapassada acende mais um LED.
    """
    if distancia >= DIST_MAX:
        return 0
    if distancia <= DIST_MIN:
        return NUM_LEDS

    proximidade = (DIST_MAX - distancia) / (DIST_MAX - DIST_MIN)
    return min(NUM_LEDS, int(proximidade * NUM_LEDS) + 1)


def padrao_da_barra(quantidade):
    # Tupla (1, 1, 0, 0, 0) com os `quantidade` primeiros LEDs ligados
    return tuple(1 if i < quantidade else 0 for i in range(NUM_LEDS))


def main():
    # O DistanceSensor dispara o Trig e mede o pulso de Echo em uma thread
    # propria, e já entrega uma média movel das últimas leituras (queue_len),
    # o que reduz o ruido e evita LEDs piscando na fronteira das faixas.
    sensor = DistanceSensor(echo=PINO_ECHO, trigger=PINO_TRIGGER,
                            max_distance=ALCANCE_SENSOR)

    # LEDBoard agrupa os 5 LEDs; atribuir uma tupla a .value liga/desliga
    # todos de uma vez
    barra = LEDBoard(*PINOS_LEDS)

    print("Aproxime um objeto do sensor. CTRL+C encerra.\n")

    ultimo = None
    try:
        while True:
            distancia = sensor.distance          # em metros
            quantidade = leds_para_distancia(distancia)

            # So escreve nas GPIOs quando o numero de LEDs muda.
            if quantidade != ultimo:
                barra.value = padrao_da_barra(quantidade)
                ultimo = quantidade

            indicador = "#" * quantidade + "-" * (NUM_LEDS - quantidade)
            print("\rDistancia: {:6.1f} cm   LEDs: [{}] {}/{}".format(
                distancia * 100, indicador, quantidade, NUM_LEDS),
                end="", flush=True)

            time.sleep(PERIODO_LEITURA)

    except KeyboardInterrupt:
        print("\n\nInterrompido pelo teclado (CTRL+C).")

    finally:
        # Apaga os LEDs e libera os pinos (equivalente ao GPIO.cleanup()).
        barra.off()
        barra.close()
        sensor.close()
        print("LEDs apagados e GPIOs liberadas.")


if __name__ == "__main__":
    main()
