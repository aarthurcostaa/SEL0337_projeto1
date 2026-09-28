# SEL0337_projeto1
3 checkpoints referentes ao projeto 1 da disciplina SEL0337 - Projetos em Sistemas Embarcados

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


