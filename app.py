import json
from typing import Annotated

import aiofiles
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from flaskwebgui import FlaskUI
from starlette.responses import FileResponse

from form_storage import FormStorage, Form, MatchAttribute
from word_pattern_match import JoinPatternConfig, SinglePatternConfig, FuzzyMatchingConfig, FuzzyMatchingAlgorithm, \
    OneOfPatternConfig, ClosestFuzzyPatternConfig, pattern_match

pattern_match_config = OneOfPatternConfig(
    name="viss",
    skip_adding_match=True,
    pattern_list=[
        JoinPatternConfig(
            name="bojātu produktu veidlapa",
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
        ),
        JoinPatternConfig(
            name="atlikumu uzskaites veidlapa",
            skip_adding_match=True,
            pattern_list=[
                SinglePatternConfig(
                    name="dokumenta atslēgvārds",
                    fuzzy_matching=FuzzyMatchingConfig(
                        algorithm=FuzzyMatchingAlgorithm.LEVENSHTEIN_DISTANCE,
                        max_distance=3
                    ),
                    iterate_words_from=2, iterate_words_to=3,
                    string="atlikumu uzskaite"
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
                )
            ]
        )
    ]
)

form_storage = FormStorage(
    forms=[
        Form(
            name="Bojāti produkti",
            form_keyword_attribute=MatchAttribute(key="dokumenta atslēgvārds", value="bojāts produkts"),
            form_columns=[
                "produkta nosaukums",
                "svars, skaitlis",
                "svars, mērvienība",
                "atbildīgā persona"
            ],
            datetime_field="laiks"
        ),
        Form(
            name="Atlikumu uzskaite",
            form_keyword_attribute=MatchAttribute(key="dokumenta atslēgvārds", value="atlikumu uzskaite"),
            form_columns=[
                "produkta nosaukums",
                "svars, skaitlis",
                "svars, mērvienība"
            ],
            datetime_field="laiks"
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


app = FastAPI()


@app.get("/")
async def read_index_html():
    return FileResponse('html/index.html')


@app.get("/forms")
async def read_forms_html():
    return FileResponse('html/forms.html')


@app.get("/data/forms")
async def read_forms_list():
    return [form.name for form in form_storage.forms]


@app.get("/data/forms/{form_index}")
async def read_forms_data(form_index: int):
    if form_index >= len(form_storage.forms):
        raise HTTPException(status_code=400, detail="Form with index " + str(form_index) + " not found!")

    form = form_storage.forms[form_index]
    return {
        "columns": form.get_form_columns(),
        "records": json.loads(form.data_frame.to_json(orient="records"))
    }


@app.post("/process-recording")
async def process_recording(file: UploadFile = File(...)):
    async with aiofiles.open("test.wav", 'wb') as out_file:
        while content := await file.read(1024):  # async read chunk
            await out_file.write(content)  # async write chunk

    output = transcribe_audio("test.wav")

    pattern_match_response = pattern_match(pattern_match_config, output)

    if pattern_match_response is not None:
        form_storage.input_pattern_matches(pattern_match_response)

    response = {
        "text": output,
        "matches": pattern_match_response
    }
    print(response)
    return response


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=3000)

#if __name__ == "__main__":
#    FlaskUI(app=app, server="fastapi", fullscreen=False, width=1000, height=1000).run()
