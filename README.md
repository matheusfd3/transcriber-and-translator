# Transcriber and Translator
Este projeto captura o áudio que está sendo reproduzido pelo sistema em tempo real, transcreve e traduz para português.

## Requisitos
**OBS: Este script foi desenvolvido e testado em sistema Linux**
- Módulos e pacotes necessários
```bash
  pip install pyaudio
  pip install -U openai-whisper
  pip install translate
  pip install numpy
```
- Baixar e configurar PulseAudio para conseguir capturar audio do sistema caso esteja no Linux, para o Windows você vai precisar de outra ferramenta.
## Como usar
1. Clone o repositório em sua máquina local:
```bash
  git clone https://github.com/matheusfd3/transcriber-and-translator.git
```
2. Você vai precisar identificar o device id do PulseAudio:
```bash
  python3 script.py --list-devices
```
3. Execute o script:
```bash
  python3 script.py --device (device id)
```
4. Reproduza um vídeo ou áudio no seu computador.

## Contribuição
Contribuições são bem-vindas! Se você encontrou um bug ou tem alguma sugestão para melhorar o projeto, sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Autor
Este projeto foi desenvolvido por [matheusfd3](https://github.com/matheusfd3)

## Licença
Este projeto é distribuído sob a licença MIT.
