"""
SEL0337 - Projetos em Sistemas Embarcados
Pratica 3 / Checkpoint 3 - COmputação Paralela
Arthur Alves da Costa - 13751207
Raphael Franco de Oliveria - 13862393

Monitor de proximidade concorrente. Quatro tarefas rodam ao mesmo tempo,
cada uma em sua propria thread, sobre a mesma montagem do Checkpoint 2
acrescida do botão do Checkpoint 1:

  1) Thread sensor   - dispara o HC-SR04 e mede a distância continuamente,
                       gravando o resultado em um estado compartilhado.
  2) Thread barra    - lâ o estado compartilhado e acende de 0 a 5 LEDs,
                       conforme a proximidade do objeto.
  3) Thread blink    - pisca o LED de alerta em uma de duas frequências,
                       alternadas pelo botão.
  4) Timer (callback)- apos N segundos de monitoramento, dispara uma função de
                       callback que imprime o relatório da sessão e encerra o
                       programa.

O acesso ao estado compartilhado e protegido por um MUTEX (threading.Lock),
pois a thread do sensor escreve enquanto a thread da barra e o callback lêem.

LIGAÇÃO:
    HC-SR04 VCC  -> 5 V;  GND -> GND
    HC-SR04 Trig -> GPIO8
    HC-SR04 Echo -> divisor 1 kohm / 2 kohm -> GPIO25
    Barra de LEDs: GPIO14, GPIO15, GPIO18, GPIO23, GPIO24
    LED de alerta: GPIO18 (12)
    Botao: GPIO25 (22) -> botao -> GND (pull-up interno)
    Todos os LEDs com resistor de 330 ohm em serie.

Integrantes: <Nome 1> (NUSP xxxxxxxx) / <Nome 2> (NUSP yyyyyyyy)
"""

import argparse
import threading
import time

import RPi.GPIO as GPIO

# --------------------------------------------------------------------------
# Configuracao
# --------------------------------------------------------------------------
PINO_TRIGGER = 8
PINO_ECHO = 24
PINOS_BARRA = (5, 6, 13, 19, 26)
PINO_ALERTA = 18
PINO_BOTAO = 25

DIST_MIN = 0.05          # m - mais perto que isso: barra cheia
DIST_MAX = 0.50          # m - mais longe que isso: barra vazia
DIST_ALERTA = 0.15       # m - abaixo disso o alerta pisca rapido sozinho

FREQUENCIAS = (1.0, 5.0)  # Hz - alternadas pelo botao
VELOCIDADE_SOM = 343.0    # m/s a 20 graus C
TIMEOUT_ECHO = 0.04       # s - ~6,8 m ida e volta, além disso, leitura perdida

PERIODO_SENSOR = 0.06     # s entre disparos do HC-SR04
PERIODO_BARRA = 0.10      # s entre atualizações da barra de LEDs
DEBOUNCE_BOTAO = 200      # ms

NUM_LEDS = len(PINOS_BARRA)


# Estado compartilhado, protegido por mutex

class EstadoCompartilhado(object):
    """Dados acessados por mais de uma thread.

    Sem sincroniza~ço, a thread da barra poderia ler a distẫncia no meio de
    uma atualização feita pela thread do sensor, e as estatísticas (contador e
    minimo) poderiam se perder em uma condição de corrida (ler-modificar-
    escrever interrompido no meio). O mutex garante exclusao mutua: apenas uma
    thread por vez entra na região crítica.

    Todo o programa usa um único lock, o que elimina por construção a
    possibilidade de deadlock (deadlock exige duas ou mais threads esperando
    locks diferentes em ordens opostas).
    """

    def __init__(self):
        self._mutex = threading.Lock()
        self._distancia = None      # ultima leitura valida, em metros
        self._leituras_ok = 0
        self._leituras_perdidas = 0
        self._distancia_minima = None

    def registrar_leitura(self, distancia):
        with self._mutex:                     
            if distancia is None:
                self._leituras_perdidas += 1
                return
            self._distancia = distancia
            self._leituras_ok += 1
            if (self._distancia_minima is None
                    or distancia < self._distancia_minima):
                self._distancia_minima = distancia

    def distancia_atual(self):
        with self._mutex:                     
            return self._distancia

    def resumo(self):
        with self._mutex:
            return (self._leituras_ok, self._leituras_perdidas,
                    self._distancia_minima)


# Acesso ao hardware

def medir_distancia():
    """Dispara o HC-SR04 e devolve a distancia em metros (None se falhar).

    Esta função é bloqueante, ela fica em espera ocupada (polling) aguardando
    as bordas do pino Echo.
    """
    # Pulso de disparo de 10 us no Trig.
    GPIO.output(PINO_TRIGGER, GPIO.LOW)
    time.sleep(0.000002)
    GPIO.output(PINO_TRIGGER, GPIO.HIGH)
    time.sleep(0.000010)
    GPIO.output(PINO_TRIGGER, GPIO.LOW)

    # Espera a subida do Echo (inicio do pulso), com timeout.
    limite = time.monotonic() + TIMEOUT_ECHO
    while GPIO.input(PINO_ECHO) == GPIO.LOW:
        if time.monotonic() > limite:
            return None
    inicio = time.monotonic()

    # Espera a descida do Echo (fim do pulso), com timeout.
    limite = inicio + TIMEOUT_ECHO
    while GPIO.input(PINO_ECHO) == GPIO.HIGH:
        if time.monotonic() > limite:
            return None
    fim = time.monotonic()

    # O pulso dura o tempo de ida e volta do som: divide-se por 2.
    return (fim - inicio) * VELOCIDADE_SOM / 2.0


def leds_para_distancia(distancia):
    """Numero de LEDs acesos (0 a 5) para uma distancia em metros."""
    if distancia is None or distancia >= DIST_MAX:
        return 0
    if distancia <= DIST_MIN:
        return NUM_LEDS
    proximidade = (DIST_MAX - distancia) / (DIST_MAX - DIST_MIN)
    return min(NUM_LEDS, int(proximidade * NUM_LEDS) + 1)


def acender_barra(quantidade):
    for indice, pino in enumerate(PINOS_BARRA):
        GPIO.output(pino, GPIO.HIGH if indice < quantidade else GPIO.LOW)


def tarefa_sensor(estado, parada):
    """Thread 1: mede a distância continuamente até o evento de parada."""
    while not parada.is_set():
        estado.registrar_leitura(medir_distancia())
        # wait() dorme de forma interrompível: se o evento for setado, a
        # thread acorda na hora em vez de esperar o timeout inteiro.
        parada.wait(PERIODO_SENSOR)


def tarefa_barra(estado, parada):
    """Thread 2: reflete a distância na barra de 5 LEDs e no terminal."""
    ultimo = None
    while not parada.is_set():
        distancia = estado.distancia_atual()
        quantidade = leds_para_distancia(distancia)

        if quantidade != ultimo:          # so escreve na GPIO quando muda
            acender_barra(quantidade)
            ultimo = quantidade

        texto = "--- cm" if distancia is None else "{:6.1f} cm".format(distancia * 100)
        print("\rDistancia: {}   Barra: [{}{}]".format(
            texto, "#" * quantidade, "-" * (NUM_LEDS - quantidade)),
            end="", flush=True)

        parada.wait(PERIODO_BARRA)


def tarefa_blink(estado, parada, controle):
    """Thread 3: pisca o LED de alerta na frequência selecionada.

    A frequência muda de duas formas: pelo botão (callback de evento) e
    automaticamente, quando o objeto entra na zona de alerta. A espera usa
    controle.wait(), então a troca de frequência tem efeito imediato, sem
    precisar terminar o semiciclo em andamento e sem polling.
    """
    while not parada.is_set():
        distancia = estado.distancia_atual()

        if distancia is not None and distancia <= DIST_ALERTA:
            frequencia = FREQUENCIAS[1]          
        else:
            frequencia = FREQUENCIAS[indice_frequencia[0]]

        meio_periodo = 1.0 / (2.0 * frequencia)

        GPIO.output(PINO_ALERTA, GPIO.HIGH)
        controle.wait(meio_periodo)
        controle.clear()
        if parada.is_set():
            break

        GPIO.output(PINO_ALERTA, GPIO.LOW)
        controle.wait(meio_periodo)
        controle.clear()

    GPIO.output(PINO_ALERTA, GPIO.LOW)


indice_frequencia = [0]


def criar_callback_botao(controle):
    """Devolve o callback de borda do botao (executado pela thread da RPi.GPIO)."""
    def ao_pressionar(canal):
        indice_frequencia[0] = (indice_frequencia[0] + 1) % len(FREQUENCIAS)
        # Acorda a thread do blink imediatamente para aplicar a nova frequencia.
        controle.set()
        print("\nBotao: frequencia do alerta -> {:.1f} Hz".format(
            FREQUENCIAS[indice_frequencia[0]]))
    return ao_pressionar


def criar_callback_fim(estado, parada, controle, duracao):
    """Devolve a funcao de callback chamada pelo Timer ao fim da contagem."""
    def fim_do_monitoramento():
        ok, perdidas, minima = estado.resumo()
        print("\n\n=== Fim do monitoramento ({:.0f} s) ===".format(duracao))
        print("Leituras validas ....: {}".format(ok))
        print("Leituras perdidas ...: {}".format(perdidas))
        if minima is None:
            print("Menor distancia .....: nenhuma leitura valida")
        else:
            print("Menor distancia .....: {:.1f} cm".format(minima * 100))
        parada.set()      # avisa todas as threads que devem terminar
        controle.set()    # acorda a thread do blink na hora
    return fim_do_monitoramento


# Configuracao de hardware e programa principal

def configurar_gpio(callback_botao):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(PINO_TRIGGER, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(PINO_ECHO, GPIO.IN)
    GPIO.setup(PINO_ALERTA, GPIO.OUT, initial=GPIO.LOW)
    for pino in PINOS_BARRA:
        GPIO.setup(pino, GPIO.OUT, initial=GPIO.LOW)

    GPIO.setup(PINO_BOTAO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(PINO_BOTAO, GPIO.FALLING,
                          callback=callback_botao,
                          bouncetime=DEBOUNCE_BOTAO)


def main():
    parser = argparse.ArgumentParser(description="Monitor de proximidade concorrente")
    parser.add_argument("--duracao", type=float, default=60.0,
                        help="tempo de monitoramento em segundos (padrao: 60)")
    args = parser.parse_args()
    if args.duracao <= 0:
        parser.error("a duracao deve ser positiva")

    estado = EstadoCompartilhado()
    parada = threading.Event()    # sinaliza "todos devem encerrar"
    controle = threading.Event()  # acorda a thread do blink

    configurar_gpio(criar_callback_botao(controle))

    threads = [
        threading.Thread(target=tarefa_sensor, args=(estado, parada),
                         name="Sensor", daemon=True),
        threading.Thread(target=tarefa_barra, args=(estado, parada),
                         name="Barra", daemon=True),
        threading.Thread(target=tarefa_blink, args=(estado, parada, controle),
                         name="Blink", daemon=True),
    ]

    # O Timer e uma thread que dorme e depois executa a função de callback.
    # Enquanto ele conta, o programa não fica preso verificando o relógio.
    temporizador = threading.Timer(
        args.duracao, criar_callback_fim(estado, parada, controle, args.duracao))
    temporizador.name = "Timer"

    print("Monitorando por {:.0f} s.".format(args.duracao))
    print("Botao no GPIO{} alterna o alerta entre {:.0f} Hz e {:.0f} Hz.".format(
        PINO_BOTAO, FREQUENCIAS[0], FREQUENCIAS[1]))
    print("CTRL+C encerra antes do tempo.\n")

    try:
        for thread in threads:
            thread.start()
        temporizador.start()

        # join() com timeout mantem a thread principal responsiva ao CTRL+C
        # (um join() sem timeout bloquearia a entrega do KeyboardInterrupt).
        while not parada.is_set():
            parada.wait(0.2)

    except KeyboardInterrupt:
        print("\n\nInterrompido pelo teclado (CTRL+C).")
        parada.set()
        controle.set()

    finally:
        temporizador.cancel()          # desarma o timer, se ainda estiver contando
        parada.set()
        controle.set()
        for thread in threads:         # espera as threads terminarem de verdade
            thread.join(timeout=2.0)
        GPIO.remove_event_detect(PINO_BOTAO)
        GPIO.cleanup()                 # todas as GPIOs voltam a ser entradas
        print("Threads encerradas e GPIOs liberadas.")


if __name__ == "__main__":
    main()