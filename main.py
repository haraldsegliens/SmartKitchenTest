import json
import time
import threading

from word_pattern_match import JoinPatternConfig, SinglePatternConfig, FuzzyMatchingConfig, FuzzyMatchingAlgorithm, \
    OneOfPatternConfig, ClosestFuzzyPatternConfig, pattern_match

# Sampling frequency
freq = 44100

channels = 2

recording_file = "recording0.wav"


pattern_match_config = JoinPatternConfig(
    name="bojātu produktu dokuments",
    skip_adding_match=True,
    pattern_list=[
        SinglePatternConfig(
            name="dokumenta atslēgvārds",
            fuzzy_matching=FuzzyMatchingConfig(
                algorithm=FuzzyMatchingAlgorithm.LEVENSHTEIN_DISTANCE,
                max_distance=3
            ),
            iterate_words_from=2, iterate_words_to=3,
            string="bojāts produkts"
        ),
        ClosestFuzzyPatternConfig(
            name="produkta nosaukums",
            fuzzy_matching=FuzzyMatchingConfig(
                algorithm=FuzzyMatchingAlgorithm.LEVENSHTEIN_DISTANCE,
                insertion_weight=1,
                deletion_weight=5,
                substitution_weight=2
            ),
            iterate_words_from=1,
            iterate_words_to=3,
            string_list=[
                "liellopa karbonāde",
                "piens",
                "olīveļļa"
            ]
        ),
        OneOfPatternConfig(
            name="svars, skaitlis",
            pattern_list=[
                SinglePatternConfig(
                    regex_string="\\d+"
                ),
                SinglePatternConfig(
                    regex_string="\\d+,\\d+"
                ),
                SinglePatternConfig(
                    regex_string="\\d+\\.\\d+"
                ),
                ClosestFuzzyPatternConfig(
                    fuzzy_matching=FuzzyMatchingConfig(
                        algorithm=FuzzyMatchingAlgorithm.LEVENSHTEIN_DISTANCE,
                        max_distance=3,
                        insertion_weight=1,
                        deletion_weight=5,
                        substitution_weight=5
                    ),
                    save_original_text_instead = True,
                    iterate_words_from=1,
                    iterate_words_to=2,
                    string_list=[
                        "viens",
                        "divi",
                        "trīs",
                        "četri",
                        "pieci",
                        "seši",
                        "septiņi",
                        "astoņi",
                        "deviņi",
                        "desmit",
                        "simts"
                    ]
                )
            ]
        ),
        ClosestFuzzyPatternConfig(
            name="svars, mērvienība",
            fuzzy_matching=FuzzyMatchingConfig(
                algorithm=FuzzyMatchingAlgorithm.LEVENSHTEIN_DISTANCE,
                max_distance=3,
                insertion_weight=1,
                deletion_weight=5,
                substitution_weight=5
            ),
            iterate_words_from=1,
            iterate_words_to=2,
            string_list=[
                "kg",
                "g",
                "l",
                "kilograms",
                "grams",
                "litrs"
            ]
        ),
        ClosestFuzzyPatternConfig(
            name="atbildīgā persona",
            fuzzy_matching=FuzzyMatchingConfig(
                algorithm=FuzzyMatchingAlgorithm.LEVENSHTEIN_DISTANCE,
                max_distance=3,
                insertion_weight=1,
                deletion_weight=5,
                substitution_weight=5
            ),
            iterate_words_from=1,
            iterate_words_to=2,
            string_list=[
                "haralds",
                "juris"
            ]
        )
    ]
)


def transcribe_audio(audio_path, task="transcribe", return_timestamps=False):
    """Function to transcribe an audio file using our endpoint"""
    import gradio_client

    api_url = "sanchit-gandhi/whisper-jax"
    client = gradio_client.Client(api_url)

    text, runtime = client.predict(
        audio_path,
        task,
        return_timestamps,
        api_name="/predict_1",
    )

    return text


def main():
    recording = False

    def record():
        import pyaudio
        import wave

        p = pyaudio.PyAudio()

        chunk = 1
        sample_format = pyaudio.paInt16

        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=freq,
                        frames_per_buffer=chunk,
                        input=True)

        frames = []

        print("started recording!\n")
        while recording:
            data = stream.read(1024)
            frames.append(data)
        print("ended recording!\n")

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        p.terminate()

        # Save the recorded data as a WAV file
        wf = wave.open(recording_file, 'wb')
        wf.setnchannels(2)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(freq)
        wf.writeframes(b''.join(frames))
        wf.close()

    record_thread = threading.Thread(target=record)

    input('Nospied Enter lai sāktu balss ierakstīšanu!')
    recording = True
    record_thread.start()

    input('Nospied Enter lai pārtrauktu balss ierakstīšanu!')
    recording = False
    record_thread.join()

    start = time.time()
    output = transcribe_audio("recording0.wav")
    end = time.time()

    print(f"Execution time: {end - start} seconds")

    print(f"Teksts: {output}")

    print(json.dumps(pattern_match(pattern_match_config, output), indent=2, ensure_ascii=False))


# def main():
#     print(json.dumps(pattern_match(pattern_match_config, "Bojāts produkts lielop karbonādu 1,32 kg Haralds"), indent=2, ensure_ascii=False))
#     print(json.dumps(pattern_match(pattern_match_config, "Bojāts produkts lielop karbonādu 1,32 kg h"), indent=2, ensure_ascii=False))
#     print(json.dumps(pattern_match(pattern_match_config, "Bojāts produkts piens 2 litri haralds"), indent=2, ensure_ascii=False))
#     print(json.dumps(pattern_match(pattern_match_config, " Bojāts produkts lielopu karbonātu 1,32 kg Haralds."), indent=2, ensure_ascii=False))
#     print(json.dumps(pattern_match(pattern_match_config, "Bojāts produkts piens divi litri haralds."), indent=2, ensure_ascii=False))
#     print(json.dumps(pattern_match(pattern_match_config, "Bojāts produkts piens divsimt litri haralds."), indent=2, ensure_ascii=False))
#     print(json.dumps(pattern_match(pattern_match_config, "Bojāts produkts 500 l Haralds"), indent=2, ensure_ascii=False))
#     print(json.dumps(pattern_match(pattern_match_config, "Bojāts produkts 5,9 kg."), indent=2, ensure_ascii=False))
#     print(json.dumps(pattern_match(pattern_match_config, "Bojots produkts olija veļa 10 litru Haralds."), indent=2, ensure_ascii=False))
#"Bojāts produkts olīvēļa 5 litru harauti."

if __name__ == '__main__':
    main()
