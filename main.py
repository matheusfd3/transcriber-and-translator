'''
Python 3.12.10
'''

from datetime import datetime, timedelta, timezone
from queue import Queue
from sys import platform
from time import sleep

import argparse
import threading
import numpy as np
import speech_recognition as sr
import torch
import whisper
from deep_translator import GoogleTranslator

from ui import UI

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="tiny", choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--non_english", action='store_true', help="Don't use the English-only model.")
    parser.add_argument("--energy_threshold", default=300, type=int)
    parser.add_argument("--record_timeout", default=1, type=float)
    parser.add_argument("--phrase_timeout", default=3, type=float)

    if 'linux' in platform:
        parser.add_argument("--default_microphone", default='pulse', type=str)

    args = parser.parse_args()

    phrase_time = None
    data_queue = Queue()
    buffer_audio = bytes()
    transcription = ['']
    translation = ['']

    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    recorder.dynamic_energy_threshold = False

    # Seleção do microfone
    if 'linux' in platform:
        mic_name = args.default_microphone
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            if mic_name in name:
                source = sr.Microphone(sample_rate=16000, device_index=index)
                break
    else:
        source = sr.Microphone(sample_rate=16000)

    # Carregamento do modelo Whisper
    model_name = args.model + ('' if args.model == 'large' or args.non_english else '.en')
    audio_model = whisper.load_model(model_name)
    source_lang = 'en' if model_name.endswith('.en') else 'auto'

    ui = UI()

    def background_loop():
        nonlocal phrase_time, buffer_audio

        with source:
            recorder.adjust_for_ambient_noise(source)

        def record_callback(_, audio: sr.AudioData) -> None:
            data = audio.get_raw_data()
            data_queue.put(data)

            # Volume RMS para feedback visual
            audio_np = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
            volume = np.sqrt(np.mean(audio_np ** 2))
            ui.update_volume_bar(volume * 2)

        recorder.listen_in_background(source, record_callback, phrase_time_limit=args.record_timeout)
        print("Model loaded. Listening...\n")

        while True:
            try:
                now = datetime.now(timezone.utc)
                
                if not data_queue.empty():
                    # Verifica se houve pausa longa (frase finalizada)
                    phrase_complete = False
                    if phrase_time and now - phrase_time > timedelta(seconds=args.phrase_timeout):
                        phrase_complete = True
                        buffer_audio = bytes()

                    phrase_time = now

                    # Junta novo áudio ao buffer
                    while not data_queue.empty():
                        buffer_audio += data_queue.get()

                    # Transcrição
                    audio_np = np.frombuffer(buffer_audio, dtype=np.int16).astype(np.float32) / 32768.0
                    result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
                    text = result['text'].strip()

                    if phrase_complete:
                        transcription.append('\n- ' + text)
                        translated = GoogleTranslator(source=source_lang, target='pt').translate(text)
                        translation.append('\n- ' + translated)
                    else:
                        transcription[-1] = '\n- ' + text
                        translated = GoogleTranslator(source=source_lang, target='pt').translate(text)
                        translation[-1] = '\n- ' + translated

                    ui.update_transcription('\n'.join(transcription))
                    ui.update_translation('\n'.join(translation))
                else:
                    sleep(0.25)

            except KeyboardInterrupt:
                print("Interrompido pelo usuário.")
                break

    # Cria a thread da transcrição
    transcription_thread = threading.Thread(target=background_loop, daemon=True)
    transcription_thread.start()

    # Inicia a interface gráfica na thread principal
    ui.run()

if __name__ == "__main__":
    main()
