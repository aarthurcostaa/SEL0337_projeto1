"""
SEL0337 - Projetos em Sistemas Embarcados
Pratica 3 / Checkpoint 1 - Programa 2
Arthur Alves da Costa - 13751207 
Raphael Franco de Oliveria - 13862393

Le no terminal um tempo em segundos, faz a contagem regressiva imprimindo
MM:SS sempre na MESMA linha e, ao final, acende um LED que permanece aceso.
"""

import time

import RPi.GPIO as GPIO

PINO_LED = 18          
LIMITE_MAXIMO = 5999   


def ler_tempo_do_usuario():
    # Rebece o valor de tempo do usuário e garante que é um valor válido
    while True:
        entrada = input("Digite o tempo da contagem regressiva, em segundos: ")

        try:
            # Type casting: a funcao input() sempre devolve str. Se o texto
            # nao representar um inteiro, int() levanta ValueError.
            segundos = int(entrada)
        except ValueError:
            print("Erro: o valor digitado deve ser um numero inteiro.\n")
            continue

        # Validações de faixa (o casting sozinho nao garante valor coerente).
        if segundos <= 0:
            print("Erro: o numero deve ser positivo (maior que zero).\n")
            continue

        if segundos > LIMITE_MAXIMO:
            print("Erro: use um valor de no maximo {} s (99:59).\n"
                  .format(LIMITE_MAXIMO))
            continue

        return segundos


def contagem_regressiva(segundos):
    # Recebe a quantidade de segundos já tratada e cria o contador no terminal
    instante_inicial = time.monotonic()

    for restante in range(segundos, -1, -1):
        # divmod devolve (quociente, resto) -> (minutos, segundos)
        minutos, segs = divmod(restante, 60)

        print("\rTempo restante: {:02d}:{:02d}".format(minutos, segs),
              end="", flush=True)

        if restante == 0:
            break

        proximo_instante = instante_inicial + (segundos - restante + 1)
        espera = proximo_instante - time.monotonic()
        if espera > 0:
            time.sleep(espera)

    print()  # encerra a linha da contagem


def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(PINO_LED, GPIO.OUT, initial=GPIO.LOW)  # LED comeca apagado

    try:
        segundos = ler_tempo_do_usuario()
        contagem_regressiva(segundos)

        GPIO.output(PINO_LED, GPIO.HIGH)
        print("Contagem finalizada! LED aceso.")

        # GPIO.cleanup() reconfigura os pinos como entrada e APAGARIA o LED.
        # Como o roteiro pede que ele permaneca aceso ao final, o script fica
        # aguardando o usuario antes de liberar as GPIOs.
        input("O LED permanece aceso. Pressione ENTER para encerrar...")

    except KeyboardInterrupt:
        print("\nInterrompido pelo teclado (CTRL+C).")

    finally:
        GPIO.cleanup()
        print("GPIOs liberadas")


if __name__ == "__main__":
    main()