import argparse
import pyaudio
import whisper
from translate import Translator
import wave
import numpy
import os

# Constantes
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
THRESHOLD = 900
SILENCE_DURATION = 0.6

def list_audio_devices(audio):
    """Lista dispositivos de áudio disponíveis."""
    info = audio.get_host_api_info_by_index(0)
    number_devices = info.get('deviceCount')
    for i in range(number_devices):
        device = audio.get_device_info_by_host_api_device_index(0, i)
        if device.get('maxInputChannels') > 0:
            print(f"Input Device id {i} - {device.get('name')}")

def capture_audio(stream, output_filename):
    """Captura áudio do stream até que haja silêncio prolongado."""
    frames = []
    silent_chunks = 0
    recording = False

    while True:
        data = stream.read(CHUNK)
        if is_silent(data):
            if recording:
                silent_chunks += 1
                if silent_chunks > (RATE / CHUNK * SILENCE_DURATION):
                    break
            continue
        else:
            silent_chunks = 0
            recording = True

        if recording:
            frames.append(data)
    
    save_audio(output_filename, frames)

def is_silent(data):
    """Verifica se o som está abaixo do limiar de silêncio."""
    audio_data = numpy.frombuffer(data, dtype=numpy.int16)
    return numpy.abs(audio_data).mean() < THRESHOLD

def save_audio(filename, frames):
    """Salva os frames de áudio capturados em um arquivo WAV."""
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

def transcribe_audio(model, filename):
    """Transcreve o áudio do arquivo usando o modelo Whisper."""
    result = model.transcribe(filename)
    return result["text"]

def translate_text(translator, text):
    """Traduz o texto usando o tradutor fornecido."""
    return translator.translate(text)

def main(device_index, output_filename):
    """Função principal para gravar, transcrever e traduzir áudio."""
    audio = pyaudio.PyAudio()
    try:
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            input_device_index=device_index,
                            frames_per_buffer=CHUNK)
        
        model = whisper.load_model("tiny")
        translator = Translator(to_lang="pt-br")
        
        print("Gravando, transcrevendo e traduzindo...")
        while True:
            capture_audio(stream, output_filename)
            transcription = transcribe_audio(model, output_filename)
            print("\n- " + transcription.strip())
            translated = translate_text(translator, transcription)
            print("- " + translated.strip())
    except KeyboardInterrupt:
        print("Encerrando...")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        print("Fechando recursos...")
        stream.stop_stream()
        stream.close()
        audio.terminate()
        if os.path.exists(output_filename):
            os.remove(output_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gravador e transcritor de áudio.")
    parser.add_argument("--list-devices", action="store_true", help="Lista os dispositivos de entrada de áudio e sai")
    parser.add_argument("--device", type=int, help="ID do dispositivo de entrada de áudio")
    parser.add_argument("--output", type=str, default="output.wav", help="Nome do arquivo de saída")
    args = parser.parse_args()

    audio = pyaudio.PyAudio()

    if args.list_devices:
        print("Lista de dispositivos de entrada de áudio:")
        list_audio_devices(audio)
        audio.terminate()
    elif args.device is not None:
        main(args.device, args.output)
    else:
        print("Você deve fornecer o ID do dispositivo de entrada com --device ou listar dispositivos com --list-devices")
