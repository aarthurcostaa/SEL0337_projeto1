# SEL0337_projeto1
Projeto 1 -  SEL0337 - Projetos em Sistemas Embarcados

Arthur Alves da Costa - 13751207

Raphael Franco de Oliveira - 13862393

# Checkpoint 1 
O primeiro checkpoint consiste em dois programas: blink_led.py e countdown.py

# blink_led.py
Consiste em acionar um LED baseando-se no estado de um botão: 
- Botão pressionado -> LED aceso
- Botão solto -> LED apagado 

Para isso foram utilizadas as bibliotecas time e RPi.GPIO. No código temos 3 funções: 
1) tratar_evento_botao: Recebe o pino no qual o botão está conectado, trata o efeito bounce, indica no terminal se o botão está pressionado ou não
   e altera o estado do pino do LED de acordo com o que foi informado acima. 
2) configurar_gpio: Configura os pinos de entrada e saída e detecta o evento do botão ter sido pressionado.
3) main: Chama a função de configuração das portas,  printa na tela as instruções ao usuário, trata as interrupções via teclado e libera as portas após
   o final encerramento do programa.

# countdown.py
Consiste em receber uma quantidade de segundos do usuário, tratar esse dado para certificar que é um formato válido e após a validação inicia uma contagem regressiva
de acordo com o que foi informado pelo terminal. Ao final da contagem o LED é aceso.

As funções utilizadas são: 
1) ler_tempo_do_usuario: Realiza a verificação da entrada fornecida pelo usuário usando Type casting (garante que o valor recebido é inteiro), depois verifica se o
   número é positivo e menor do que o limite estabelecido (99:59)
2) contagem_regressiva: Recebe a quantidade de segundos já validada, realiza a conversão e vai atualizando o contador a cada segundo (end="" + flush=True para não
   gerar várias linhas no print).
3) main: chama as funções anteriores e admistra a liberação das portas após a interrupção do usuário.


# Checkpoint 2
O segundo checkpoint consiste em dois programas: pwm_fade.py e distance_sensor.py

# pwm_fade.py
Este programa controla o brilho de um led por meio da aplicação de um sinal PWM com duty cicle variável para gerar um efeito de gradiente no led. O sinal PWM recebe uma correção gama para suavizar a transição devido à percepção de brilho do olho humano. 

As funções utilizadas são: 
1) brilho_para_duty: recebe o valor de brilho entre 0 e 1 e retorna o sinal corrigido por gama.
2) sequencia_triangular: gera a sequência de números que irá modular o sinal PWM e gerar efetivamente o efeito de gradiente.
3) degrade_em_loop: aplica a sequência de números da rampa no sinal de PWM
4) ler_argumentos: coleta possíveis argumentos passados pelo usuário via terminal.
5) main: organiza todas as funções acima de maneira que o usuário seja notificado em cada etapa e se algum erro aconteceu.

Para ilustrar o funcionamento, seguem abaixo repectivamente: uma foto da montagem do circuito, a leitura do sinal PWM via osciloscópio e o circuito enquanto o código é executado.

1) Montagem do circuito
<img width="960" height="1280" alt="pwm" src="https://github.com/user-attachments/assets/1c5287ea-16c0-479a-a110-f7adc699a250" />

2) Leitura do PWM pelo osciloscópio

https://github.com/user-attachments/assets/8a5af3e6-1a15-4d77-9f76-82c7d6c4cdf7

3) Circuito com o código sendo executado

https://github.com/user-attachments/assets/37f91a6a-f43d-4e78-a797-dd2cc1cbf637

# distance_sensor.py
Este código faz o controle da leitura do sensor, calculo da distância e gerenciamento dos LEDs de indicação. 

As funções utilizadas são:
1) leds_para_distancia: recebe a distância lida pelo sensor e retorna quantos leds deverão ser acesos.
2) padrão_da_barra: recebe a quantidade de leds que devem ligar e retorna o vetor correspondente para ligá-los.
3) main: edita as mensagens no terminal de indicação ao usuário, processa interrupções via teclado e limpa as portas que estão sendo utilizadas.

Para ilustrar o funcionamento do código, seguem abaixo, respectivamente: A montagem do circuito e a sua devida demonstração.

1) Montagem do circuito:

<img width="960" height="1280" alt="distance" src="https://github.com/user-attachments/assets/b4a5b153-2472-4ee4-9f60-ac1d020b876b" />


2) Demonstração de funcionamento:

   

https://github.com/user-attachments/assets/a178d16a-d6b9-4a52-8a2c-18d3abd130a2


# Checkpoint 3
O terceiro checkpoint consiste em um programa: parallel_monitor.py

# parallel_monitor.py
Este programa reúne os dois checkpoints anteriores em uma única aplicação concorrente, um monitor de proximidade. 
O sensor ultrassônico mede a distância continuamente, a barra de cinco LEDs indica o quão perto o objeto está,
um LED de alerta pisca em uma de duas frequências selecionadas pelo botão e, ao fim de um tempo pré-determinado, 
uma função de callback imprime o relatório da sessão e encerra o programa.

As quatro tarefas rodam ao mesmo tempo, cada uma em sua própria thread:

| Tarefa | Papel |
|---|---|
| Thread Sensor | dispara o HC-SR04 e grava a distância no estado compartilhado |
| Thread Barra | lê o estado e acende de 0 a 5 LEDs conforme a proximidade |
| Thread Blink | pisca o LED de alerta na frequência selecionada |
| `threading.Timer` | conta o tempo da sessão e executa o callback final |

Existe ainda uma quinta thread que não é criada explicitamente,
a thread interna da biblioteca RPi.GPIO, gerada pelo `add_event_detect`, 
responsável por executar o callback do botão quando a borda é detectada.

A necessidade da concorrência fica clara na função de medição, a leitura do HC-SR04 é bloqueante, 
pois fica em espera ocupada aguardando as bordas do pino Echo por até 40 ms. Em um programa sequencial, 
essa espera travaria o blink do LED e a resposta ao botão. Isolando-a em uma thread própria, as demais 
tarefas continuam rodando normalmente.

As funções e classes utilizadas são:

1) EstadoCompartilhado (classe): encapsula os dados acessados por mais de uma thread, a última distância válida, o contador de leituras e a menor distância da sessão. Todos os acessos são protegidos por um mutex (`threading.Lock`), já que a thread do sensor escreve enquanto a thread da barra e o callback final leem. Possui três métodos: `registrar_leitura` (grava uma nova medição ou contabiliza uma leitura perdida), `distancia_atual` (devolve a última leitura válida) e `resumo` (devolve as estatísticas da sessão para o relatório final).

2) medir_distancia: dispara um pulso de 10 µs no pino Trig e mede a largura do pulso devolvido no pino Echo, convertendo-a em distância pela velocidade do som dividida por dois (ida e volta). As duas esperas por borda têm timeout de 40 ms, equivalente a cerca de 6,8 m, bem além do alcance do sensor: se ele estourar, a função devolve `None` e a leitura é contabilizada como perdida, preservando a última distância válida para que a barra não oscile.

3) leds_para_distancia: recebe a distância em metros e devolve quantos LEDs devem acender. O intervalo entre 50 cm e 5 cm é dividido em cinco faixas iguais; acima do limite superior nenhum LED acende, abaixo do inferior todos acendem.

4) acender_barra: recebe a quantidade de LEDs e escreve o padrão correspondente nos cinco pinos da barra.

5) tarefa_sensor: corpo da primeira thread. Mede a distância repetidamente e registra o resultado no estado compartilhado, respeitando o intervalo de 60 ms entre disparos recomendado pelo datasheet para que o eco residual se dissipe. A espera usa `Event.wait()` em vez de `sleep()`, de modo que a thread acorda imediatamente quando o evento de parada é sinalizado.

6) tarefa_barra: corpo da segunda thread. Lê o estado compartilhado, atualiza os LEDs apenas quando o número muda e imprime a distância e a barra sempre na mesma linha do terminal.

7) tarefa_blink: corpo da terceira thread. Pisca o LED de alerta na frequência selecionada, que muda de duas formas: pelo botão e automaticamente, quando o objeto entra na zona de alerta (15 cm). A espera de cada semiciclo usa `Event.wait()`, então a troca de frequência tem efeito imediato, sem precisar terminar o semiciclo em andamento e sem polling.

8) criar_callback_botao: devolve a função executada pela thread interna da RPi.GPIO quando o botão é pressionado. Ela alterna o índice da frequência e acorda a thread do blink para que a mudança seja aplicada na hora.

9) criar_callback_fim: devolve a função de callback que o `threading.Timer` executa ao fim da contagem. Ela lê as estatísticas do estado compartilhado, imprime o relatório da sessão (leituras válidas, leituras perdidas e menor distância registrada) e sinaliza o evento de parada para todas as threads.

10) configurar_gpio: configura o modo BCM, as direções de todos os pinos, o pull-up interno do botão e a detecção de evento na borda de descida com debounce de 200 ms.

11) main: lê a duração do monitoramento passada por argumento de linha de comando, cria o estado compartilhado e os eventos de sincronização, inicia as três threads e o temporizador, trata a interrupção por teclado e garante o encerramento ordenado, cancela o timer, sinaliza a parada, aguarda as threads com `join()` e só então libera as GPIOs com `GPIO.cleanup()`.

Para ilustrar o funcionamento, seguem abaixo, respectivamente: a montagem do circuito e a demonstração do programa em execução.

1) Montagem do circuito:

<img width="1200" height="1600" alt="WhatsApp Image 2026-10-05 at 09 12 07" src="https://github.com/user-attachments/assets/d6dd3a7b-4023-4e94-9e50-1dc557b6bc0b" />

2) Demonstração de funcionamento:



https://github.com/user-attachments/assets/e73d39d0-4555-46ba-ba27-ecbe7f42e27f





# Conceitos envolvidos

Um programa é apenas um arquivo executável, ao ser carregado e executado, torna-se um processo, com espaço de memória próprio e 
isolado por hardware pela MMU. Uma thread é uma unidade de execução dentro de um processo, e todas as threads de um mesmo processo 
compartilham o espaço de memória, tendo apenas pilha e registradores próprios.

Justamente por compartilharem memória, duas threads podem interferir uma na outra: uma sequência ler-modificar-escrever pode ser
interrompida no meio pela preempção do escalonador, levando a resultados incorretos. O mutex (`threading.Lock`) garante exclusão 
mútua, permitindo que apenas uma thread por vez entre na região crítica. O semáforo se diferencia por permitir um número limitado,
maior que um, de acessos simultâneos, desnecessário nesta aplicação.

Deadlock, ocorre quando duas ou mais threads se bloqueiam mutuamente, cada uma segurando o recurso que a outra espera. A aplicação
o evita por construção, utilizando um único lock em todo o programa: sem dois locks, não existem ordens de aquisição conflitantes. 
As demais estratégias seriam adquirir os locks sempre na mesma ordem hierárquica e utilizar timeouts.


O kernel do Linux alterna as threads por preempção, distribuindo fatias de tempo de forma circular segundo o 
algoritmo round-robin. Como o Linux não é um sistema operacional de tempo real, não há garantia determinística de prazo, obtendo-se
no máximo um comportamento soft real time. Os processos foram inspecionados no terminal com `ps aux | grep python`, `pgrep -fl python` 
e `top -p <PID>`, e a afinidade de núcleo foi verificada com `taskset -cp <PID>`, comando que permite dedicar um dos quatro núcleos do 
BCM2837 a um processo específico.

O uso de threads foi a escolha adequada por dois motivos. Primeiro, pela natureza da carga: todas as tarefas são limitadas por 
entrada/saída e temporização, esperar o pulso do Echo, dormir entre 
as piscadas do LED, aguardar o timer, e não por processamento. Durante essas esperas o GIL é liberado, de modo que as threads 
efetivamente se intercalam e o paralelismo real entre múltiplos núcleos não traria ganho. Segundo, pelo compartilhamento de memória,
a distância medida precisa ser vista imediatamente pelas demais tarefas, o que com threads se resolve com uma variável protegida por mutex. 
Com `multiprocessing.Process`, cada tarefa teria memória isolada e seria necessário recorrer a mecanismos de comunicação entre processos 
(`Queue`, `Pipe` ou `Value`), além do custo maior de criação e do risco de dois processos inicializarem a mesma GPIO de forma conflitante. 
Processos seriam preferíveis caso alguma tarefa fosse limitada por CPU, processamento de imagem ou filtragem pesada dos dados do sensor, 
por exemplo, situação em que o GIL impediria o ganho com threads e o paralelismo real entre os quatro núcleos compensaria o isolamento 
de memória.


