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
