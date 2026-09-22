"""
SEL0337 - Projetos em Sistemas Embarcados
Pratica 3 / Checkpoint 1 - Programa 1
Arthur Alves da Costa - 13751207 
Raphael Franco de Oliveria - 13862393

Acende um LED enquanto o botao estiver pressionado e apaga quando ele for
solto, usando (add_event_detect) da biblioteca RPi.GPIO.
O pino do botao e configurado com resistor de PULL-UP interno e o programa
executa o cleanup das GPIOs ao ser interrompido pelo teclado (CTRL+C).
"""

import time
import RPi.GPIO as GPIO

PINO_LED = 18       # GPIO18             
PINO_BOTAO = 23     #GPIO23
TEMPO_DEBOUNCE = 50  # ms ignorados apos cada borda


def tratar_evento_botao(canal):
    # verifica se o botão está pressionado ou não e acende o LED conforme o resultado
    botao_pressionado = (GPIO.input(canal) == GPIO.LOW)

    GPIO.output(PINO_LED, GPIO.HIGH if botao_pressionado else GPIO.LOW)

    if botao_pressionado:
        print("Botao pressionado -> LED aceso")
    else:
        print("Botao solto       -> LED apagado")


def configurar_gpio():

    GPIO.setmode(GPIO.BCM)        # numeração pelos nomes GPIO
    GPIO.setwarnings(False)       # silencia avisos de pino ja em uso

    # Saida: comeca em nivel baixo (LED apagado), estado inicial seguro
    GPIO.setup(PINO_LED, GPIO.OUT, initial=GPIO.LOW)

    # Entrada com pull-up interno
    GPIO.setup(PINO_BOTAO, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    GPIO.add_event_detect(
        PINO_BOTAO,
        GPIO.BOTH,
        callback=tratar_evento_botao,
        bouncetime=TEMPO_DEBOUNCE,
    )


def main():
    configurar_gpio()

    print("Pressione o botao para acender o LED")
    print("CTRL+C encerra o programa e libera as GPIOs\n")
    tratar_evento_botao(PINO_BOTAO) # certeza que o LED iniciará desligado 

    try:
        while True:
            time.sleep(0.5)

    except KeyboardInterrupt:
        # Trata a interrupcao por teclado (CTRL+C)
        print("\nInterrompido pelo teclado (CTRL+C)")

    finally:
        # Limpeza das portas
        GPIO.remove_event_detect(PINO_BOTAO)
        GPIO.cleanup()
        print("GPIOs liberadas")


if __name__ == "__main__":
    main()
