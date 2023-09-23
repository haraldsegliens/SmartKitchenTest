from form_storage import FormStorage, Form, MatchAttribute
from word_pattern_match import JoinPatternConfig, SinglePatternConfig, FuzzyMatchingConfig, \
    OneOfPatternConfig, ClosestFuzzyPatternConfig, ColognePhoneticsConfig, LevenshteinDistanceConfig

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
                    fuzzy_matching=ColognePhoneticsConfig(
                        fuzzy_match_config_for_phonetics=LevenshteinDistanceConfig()
                    ),
                    iterate_words_from=2, iterate_words_to=3,
                    string="bojāts produkts"
                ),
                ClosestFuzzyPatternConfig(
                    name="produkta nosaukums",
                    fuzzy_matching=ColognePhoneticsConfig(
                        fuzzy_match_config_for_phonetics=LevenshteinDistanceConfig()
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
                            fuzzy_matching=LevenshteinDistanceConfig(
                                max_distance=3,
                                insertion_weight=1,
                                deletion_weight=5,
                                substitution_weight=5
                            ),
                            save_original_text_instead=True,
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
                    fuzzy_matching=LevenshteinDistanceConfig(
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
                    fuzzy_matching=LevenshteinDistanceConfig(
                        max_distance=3,
                        insertion_weight=1,
                        deletion_weight=5,
                        substitution_weight=5
                    ),
                    iterate_words_from=1,
                    iterate_words_to=2,
                    min_fuzzy_match_score=-30,
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
                    fuzzy_matching=ColognePhoneticsConfig(
                        fuzzy_match_config_for_phonetics=LevenshteinDistanceConfig()
                    ),
                    iterate_words_from=2, iterate_words_to=3,
                    string="atlikumu uzskaite"
                ),
                ClosestFuzzyPatternConfig(
                    name="produkta nosaukums",
                    fuzzy_matching=ColognePhoneticsConfig(
                        fuzzy_match_config_for_phonetics=LevenshteinDistanceConfig()
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
                            fuzzy_matching=LevenshteinDistanceConfig(
                                max_distance=3,
                                insertion_weight=1,
                                deletion_weight=5,
                                substitution_weight=5
                            ),
                            save_original_text_instead=True,
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
                    fuzzy_matching=LevenshteinDistanceConfig(
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