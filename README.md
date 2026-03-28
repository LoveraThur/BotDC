Este é um Bot do discord, eu fiz pelo motivo de que eu queria entender como funciona a biblioteca Discord.py do Python.


## Ele tem algumas funcionalidades interessantes como:

    Mensagem de Boas-Vindas
    Cargo automático
    Preço do Bitcoin
    Tocar Música
    Parar Música
    Pular Música
    Desconectar da Call 

## Comandos disponíveis para uso neste bot:

    Boas-Vindas: Comando nativo, assim que alguem entra, caso o canal 
    esteja configurado ele da a mensagem de boas vindas e adiciona o cargo à 
    Pessoa
    .bitcoin: ao utilizar ".bitcoin" no PRINCIPAL_CHANNEL ele manda uma 
    mensagem ao chat destinado a bitcoin o valor atual da bitcoin, em tempo 
    real

    Comandos de Musica 

    /play: ao executar este comando "/play" com o nome de uma musica ou um 
    link do youtube ele executa a musica na call em que você está conectado. 
    Ele se conecta na call automaticamente apenas de você utilizar este comando
    /skip: Este comando pula a musica e começa tocar a próxima da fila. 
    caso nçao ouver outra na fila o bot irá se desconectar da call
    /pause: Pausa a musica em que está sendo tocada no momento atual
    resume: A musica em que estava pausada volta a tocar
    /disconnect: O bot se desconecta da call



### Está liberado o requirements.txt para caso você queira fazer um bot com o
 meu código(para instalar as bibliotecas necessárias). Unicas mudanças que 
 devem ser feitas são: 

     TOKEN do bot; 
     id de chats; 
    
é necessário estas mudanças por conta de que este bot funciona apenas no meu 
servidor.
