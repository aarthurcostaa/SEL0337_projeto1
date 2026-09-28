"""
SEL0337 - Projetos em Sistemas Embarcados
Pratica 3 / Checkpoint 2 - Programa 1 (PWM)
Arthur Alves da Costa - 13751207
Raphael Franco de Oliveria - 13862393

Efeito de "fade" em um LED: o brilho sobe de apagado até o máximo,
desce de volta ate apagado e repete em loop ate o usuário pressionar CTRL+C.
O brilho e controlado pelo duty cycle de um sinal PWM gerado pela RPi.GPIO

Frequencia e periodo podem ser passados pela linha de comando:
    python pwm_fade.py                     # 100 Hz, ciclo de 2 s
    python pwm_fade.py --freq 50           # 50 Hz  
    python pwm_fade.py --freq 1000 --periodo 4
    python pwm_fade.py --linear            # desliga a correção gama
"""

import argparse
import time

import RPi.GPIO as GPIO

PINO_LED = 18          # GPIO18 (pino físico 12) -> resistor 330 ohm -> LED -> GND
FREQ_PADRAO = 100      # Hz
PERIODO_PADRAO = 2.0   # s 
PASSOS = 100           # resolução do gradiente em cada sentido
GAMMA = 2.2            # expoente da correção gama, para percepção de brilho


def brilho_para_duty(brilho, usar_gamma=True):
    """Converte brilho percebido (0.0 a 1.0) em duty cycle (0 a 100 %).

    O olho humano tem resposta aproximadamente logaritmica: com duty cycle
    linear o LED parece ficar quase no maximo logo na primeira metade da
    rampa e o degrade fica quebrado. Elevar o brilho a 2,2 (correção gama) gasta
    mais passos na regiao escura, e a variação passa a parecer uniforme.
    """
    if usar_gamma:
        return 100.0 * (brilho ** GAMMA)
    return 100.0 * brilho


def sequencia_triangular(passos):
    # Cria a sequência para gerar os níveis de brilho
    subida = list(range(0, passos + 1))
    descida = list(range(passos - 1, 0, -1))
    return subida + descida


def degrade_em_loop(pwm, periodo, usar_gamma):
    # Executa o degrade indefinidamente
    sequencia = sequencia_triangular(PASSOS)
    intervalo = periodo / len(sequencia)   # tempo em cada nivel de brilho

    while True:
        for indice in sequencia:
            brilho = indice / PASSOS
            duty = brilho_para_duty(brilho, usar_gamma)

            # Muda o duty cycle sem parar o PWM, a frequência é mantida
            pwm.ChangeDutyCycle(duty)

            # Atualiza a mesma linha do terminal
            barra = "#" * int(brilho * 20)
            print("\rDuty cycle: {:6.2f} %  [{:<20}]".format(duty, barra),
                  end="", flush=True)

            time.sleep(intervalo)


def ler_argumentos():
    # definição de argumentos diretamente pelo terminal
    parser = argparse.ArgumentParser(description="Degrade de LED com PWM")
    parser.add_argument("--freq", type=float, default=FREQ_PADRAO,
                        help="frequencia do PWM em Hz (padrao: 100)")
    parser.add_argument("--periodo", type=float, default=PERIODO_PADRAO,
                        help="duracao de um ciclo completo em s (padrao: 2)")
    parser.add_argument("--linear", action="store_true",
                        help="usa duty cycle linear, sem correcao gama")
    args = parser.parse_args()

    # Validacao das entradas
    if args.freq <= 0:
        parser.error("a frequencia deve ser positiva")
    if args.periodo <= 0:
        parser.error("o periodo deve ser positivo")
    return args


def main():
    args = ler_argumentos()

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(PINO_LED, GPIO.OUT, initial=GPIO.LOW)

    # Cria o objeto PWM no pino do LED e inicia com duty 0 % (apagado)
    # A RPi.GPIO gera PWM por software, por isso o osciloscopio mostra jitter nas bordas, 
    # principalmente em frequencias altas
    pwm = GPIO.PWM(PINO_LED, args.freq)
    pwm.start(0)

    print("PWM no GPIO{} a {:.0f} Hz, ciclo de {:.1f} s ({}).".format(
        PINO_LED, args.freq, args.periodo,
        "linear" if args.linear else "com correcao gama"))
    print("CTRL+C encerra.\n")

    try:
        degrade_em_loop(pwm, args.periodo, usar_gamma=not args.linear)

    except KeyboardInterrupt:
        print("\n\nInterrompido pelo teclado (CTRL+C).")

    finally:
        # Parar o PWM antes do cleanup evita erro da RPi.GPIO
        # ao destruir um objeto PWM de um pino que ja foi liberado
        pwm.stop()
        GPIO.cleanup()
        print("PWM parado e GPIOs liberadas.")


if __name__ == "__main__":
    main()
