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
    parser.add_argument(
        "--model",
        default="base",
        help="Model to use",
        choices=["tiny", "base", "small", "medium", "large"]
    )
    parser.add_argument(
        "--non_english",
        action='store_true',
        help="Don't use the english model."
    )
    parser.add_argument(
        "--energy_threshold",
        default=600,
        help="Energy level for mic to detect.",
        type=int
    )
    parser.add_argument(
        "--record_timeout",
        default=2,
        help="How real time the recording is in seconds.",
        type=float
    )
    parser.add_argument(
        "--phrase_timeout",
        default=3,
        help="How much empty space between recordings before we "
             "consider it a new line in the transcription.",
        type=float
    )

    if 'linux' in platform:
        parser.add_argument(
            "--default_microphone",
            default='pulse',
            help="Default microphone name for SpeechRecognition. "
                 "Run this with 'list' to view available Microphones.",
            type=str
        )

    args = parser.parse_args()

    phrase_time = None
    data_queue = Queue()
    phrase_bytes = bytes()
    transcription = ['']
    translation = ['']

    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    recorder.dynamic_energy_threshold = False

    if 'linux' in platform:
        mic_name = args.default_microphone
        if not mic_name or mic_name == 'list':
            print("Available microphone devices are: ")
            for index, name in enumerate(sr.Microphone.list_microphone_names()):
                print(f"Microphone with name \"{name}\" found")
            return

        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            if mic_name in name:
                source = sr.Microphone(sample_rate=16000, device_index=index)
                break
    else:
        source = sr.Microphone(sample_rate=16000)

    model = args.model
    if args.model != "large" and not args.non_english:
        model = model + ".en"

    source_lang = 'en' if model.endswith('.en') else 'auto'
    audio_model = whisper.load_model(model)

    record_timeout = args.record_timeout
    phrase_timeout = args.phrase_timeout

    ui = UI()

    def background_loop():
        nonlocal phrase_time, phrase_bytes

        with source:
            recorder.adjust_for_ambient_noise(source)

        def record_callback(_, audio: sr.AudioData) -> None:
            data = audio.get_raw_data()
            data_queue.put(data)
            audio_np = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
            volume = np.sqrt(np.mean(audio_np ** 2))
            ui.update_volume_bar(volume * 2)

        recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

        print("Model loaded.\n")

        while True:
            try:
                now = datetime.now(timezone.utc)
                if not data_queue.empty():
                    phrase_complete = False
                    if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                        phrase_bytes = bytes()
                        phrase_complete = True

                    phrase_time = now

                    audio_data = b''.join(data_queue.queue)
                    data_queue.queue.clear()
                    phrase_bytes += audio_data

                    audio_np = np.frombuffer(phrase_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                    result = audio_model.transcribe(audio_np, fp16=torch.cuda.is_available())
                    text = result['text'].strip()

                    if phrase_complete:
                        transcription.append('\n- ' + text)
                        translation.append('\n- ' + GoogleTranslator(source=source_lang, target='pt').translate(text))
                    else:
                        transcription[-1] = '\n- ' + text
                        translation[-1] = '\n- ' + GoogleTranslator(source=source_lang, target='pt').translate(text)

                    ui.update_transcription('\n'.join(transcription))
                    ui.update_translation('\n'.join(translation))
                else:
                    sleep(0.25)
            except KeyboardInterrupt:
                break

    # Cria a thread da transcrição
    transcription_thread = threading.Thread(target=background_loop, daemon=True)
    transcription_thread.start()

    # Inicia a interface gráfica na thread principal
    ui.run()

if __name__ == "__main__":
    main()
