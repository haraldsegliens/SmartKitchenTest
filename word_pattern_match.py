import copy
import re
import typing
from enum import Enum

from Levenshtein import distance


class FuzzyMatchingAlgorithm(Enum):
    LEVENSHTEIN_DISTANCE = 1


class FuzzyMatchingConfig:
    def __init__(self, algorithm: FuzzyMatchingAlgorithm, max_distance: int = 3, insertion_weight: int = 1, deletion_weight: int = 1, substitution_weight: int = 1):
        self.algorithm = algorithm
        self.max_distance = max_distance
        self.insertion_weight = insertion_weight
        self.deletion_weight = deletion_weight
        self.substitution_weight = substitution_weight


class PatternConfig:
    def __init__(self, name: str = None, skip_adding_match: bool = False):
        self.name = name
        self.skip_adding_match = skip_adding_match


class JoinPatternConfig(PatternConfig):
    def __init__(self, pattern_list: list[PatternConfig], name: str = None, skip_adding_match: bool = False):
        super().__init__(name, skip_adding_match)
        self.pattern_list = pattern_list


class SinglePatternConfig(PatternConfig):
    def __init__(self, fuzzy_matching: FuzzyMatchingConfig = None, string: str = None, regex_string: str = None, iterate_words_from: int = None, iterate_words_to: int = None, name: str = None, skip_adding_match: bool = False):
        if string is not None and regex_string is not None:
            raise Exception("string and regex_string can't both be defined in SinglePatternConfig name=" + name)
        if fuzzy_matching is not None and regex_string is not None:
            raise Exception("fuzzy_matching and regex_string can't both be defined in SinglePatternConfig name=" + name)
        if iterate_words_from is not None and iterate_words_to is not None and iterate_words_from > iterate_words_to:
            raise Exception("iterate_words_from must be smaller or equal to iterate_words_to in SinglePatternConfig name=" + name)
        super().__init__(name, skip_adding_match)
        self.fuzzy_matching = fuzzy_matching
        self.string = string
        self.regex_string = regex_string
        self.iterate_words_from = iterate_words_from
        self.iterate_words_to = iterate_words_to


class OneOfPatternConfig(PatternConfig):
    def __init__(self, pattern_list: list[PatternConfig], name: str = None, skip_adding_match: bool = False):
        super().__init__(name, skip_adding_match)
        self.pattern_list = pattern_list
        if name is not None:
            for pattern in pattern_list:
                if pattern.name is None:
                    pattern.name = name


class ClosestFuzzyPatternConfig(PatternConfig):
    def __init__(self, string_list: list[str], fuzzy_matching: FuzzyMatchingConfig, iterate_words_from: int = None, iterate_words_to: int = None, name: str = None, save_original_text_instead: bool = False, min_fuzzy_match_score: int = -15, skip_adding_match: bool = False):
        super().__init__(name, skip_adding_match)
        if iterate_words_from is not None and iterate_words_to is not None and iterate_words_from > iterate_words_to:
            raise Exception("iterate_words_from must be smaller or equal to iterate_words_to in ClosestFuzzyPatternConfig name=" + name)
        self.string_list = string_list
        self.fuzzy_matching = fuzzy_matching
        self.iterate_words_from = iterate_words_from
        self.iterate_words_to = iterate_words_to
        self.save_original_text_instead = save_original_text_instead
        self.min_fuzzy_match_score = min_fuzzy_match_score


class WordBuffer:
    def __init__(self):
        self.word_buffer = []
        self.pointers = []

    def insert(self, text: str):
        self.word_buffer.extend(text.split())

    def create_pointer_from_start(self):
        pointer = WordBufferPointer(self, 0)
        self.pointers.append(pointer)
        return pointer

    def copy_pointer(self, pointer):
        pointer = WordBufferPointer(self, copy.copy(pointer.index))
        self.pointers.append(pointer)
        return pointer

    def delete_pointer(self, pointer):
        self.pointers.remove(pointer)
        self.__update_buffer_and_pointers__()
        del pointer

    def peek_words_between_pointers(self, pointer1, pointer2) -> str:
        min_index = min(pointer1.index, pointer2.index)
        max_index = max(pointer1.index, pointer2.index)
        return " ".join(self.word_buffer[min_index:max_index])

    def __update_buffer_and_pointers__(self):
        min_index = len(self.word_buffer) - 1
        for pointer in self.pointers:
            min_index = min(min_index, pointer.index)

        # TODO: add some minimum number of words configuration that is necessary to reduce the word_buffer.
        #  So that we don't reduce word_buffer for every small request
        if min_index == 0:
            return

        self.word_buffer = self.word_buffer[min_index:]

        for pointer in self.pointers:
            pointer.index = pointer.index - min_index


class WordBufferPointer:
    def __init__(self, word_buffer: WordBuffer, index: int):
        self.word_buffer = word_buffer
        self.index = index

    def read_words(self, word_count: int) -> str:
        return " ".join(self.read_word_list(word_count))

    def read_word_list(self, word_count: int) -> list[str]:
        # TODO: make this call wait for some time for new words
        if self.index + word_count > len(self.word_buffer.word_buffer):
            result = self.word_buffer.word_buffer[self.index:]
            self.index = len(self.word_buffer.word_buffer)
        else:
            result = self.word_buffer.word_buffer[self.index:self.index + word_count]
            self.index = self.index + word_count
        self.word_buffer.__update_buffer_and_pointers__()
        return result

    def peek_word_count_for_min_symbols(self, symbol_count: int) -> int:
        word_count = 0
        symbol_sum = 0
        while (symbol_sum + word_count - 1) < symbol_count and self.index + word_count < len(self.word_buffer.word_buffer):
            symbol_sum = symbol_sum + len(self.word_buffer.word_buffer[self.index + word_count])
            word_count = word_count + 1

        return word_count

    def read_min_symbols(self, symbol_count: int) -> str:
        return self.read_words(self.peek_word_count_for_min_symbols(symbol_count))

    def move_to(self, pointer):
        self.index = pointer.index


class HandleIterateWordsWorkResult:
    def __init__(self, result: object, end_iteration: bool):
        self.result = result
        self.end_iteration = end_iteration


class HandleIterateWordsResultPair:
    def __init__(self, result: object, word_count: int):
        self.result = result
        self.word_count = word_count


def handle_iterate_words(work: typing.Callable[[str], HandleIterateWordsWorkResult], pointer: WordBufferPointer, iterate_words_from: int = None, iterate_words_to: int = None) -> [HandleIterateWordsResultPair]:
    if iterate_words_from is None or iterate_words_to is None:
        new_pointer = pointer.word_buffer.copy_pointer(pointer)
        r = work(new_pointer.read_words(1))
        new_pointer.word_buffer.delete_pointer(new_pointer)
        return [
            HandleIterateWordsResultPair(
                result=r.result,
                word_count=1
            )
        ]
    else:
        result = []
        for i in range(iterate_words_from, iterate_words_to + 1):
            new_pointer = pointer.word_buffer.copy_pointer(pointer)
            r = work(new_pointer.read_words(i))
            result.append(HandleIterateWordsResultPair(
                result=r.result,
                word_count=i
            ))
            new_pointer.word_buffer.delete_pointer(new_pointer)
            if r.end_iteration is True:
                break
        return result


def fuzzy_match_score(text, target_text, config: FuzzyMatchingConfig) -> int:
    if config.algorithm == FuzzyMatchingAlgorithm.LEVENSHTEIN_DISTANCE:
        return config.max_distance - distance(
            text.lower(),
            target_text.lower(),
            weights=(
                config.insertion_weight,
                config.deletion_weight,
                config.substitution_weight
            )
        )
    return False


def fuzzy_match(text, target_text, config: FuzzyMatchingConfig) -> bool:
    return fuzzy_match_score(text, target_text, config) >= 0


def pattern_matcher(pointer: WordBufferPointer, config: PatternConfig, matches: dict[str, str]) -> bool:
    if isinstance(config, JoinPatternConfig):
        return join_pattern_matcher(pointer, config, matches)
    elif isinstance(config, SinglePatternConfig):
        return single_pattern_matcher(pointer, config, matches)
    elif isinstance(config, OneOfPatternConfig):
        return one_of_pattern_algorithm(pointer, config, matches)
    elif isinstance(config, ClosestFuzzyPatternConfig):
        return closest_fuzzy_pattern_algorithm(pointer, config, matches)
    return False


def join_pattern_matcher(pointer: WordBufferPointer, config: JoinPatternConfig, matches: dict[str, str]) -> bool:
    start_pointer = pointer.word_buffer.copy_pointer(pointer)
    for pattern in config.pattern_list:
        if pattern_matcher(pointer, pattern, matches) is False:
            return False
    if config.name is not None and not config.skip_adding_match:
        matches[config.name] = pointer.word_buffer.peek_words_between_pointers(start_pointer, pointer)
    start_pointer.word_buffer.delete_pointer(start_pointer)
    return True


def single_pattern_matcher(pointer: WordBufferPointer, config: SinglePatternConfig, matches: dict[str, str]) -> bool:
    def work(text) -> HandleIterateWordsWorkResult:
        r = None
        if config.string is not None:
            if config.fuzzy_matching is not None:
                if fuzzy_match(text, config.string, config.fuzzy_matching):
                    r = config.string
            else:
                if config.string.lower() == text.lower():
                    r = config.string
        elif config.regex_string is not None:
            match = re.match(config.regex_string, text)
            if match is not None and match.string == text:
                r = match.string

        return HandleIterateWordsWorkResult(
            result=r,
            end_iteration=r is not None
        )

    result_pairs = handle_iterate_words(work, pointer, config.iterate_words_from, config.iterate_words_to)

    if len(result_pairs) == 0:
        return False

    result_pair = result_pairs[0]

    if result_pair.result is None:
        return False

    pointer.read_words(result_pair.word_count)
    if config.name not in matches and not config.skip_adding_match:
        matches[config.name] = str(result_pair.result)

    return True


def one_of_pattern_algorithm(pointer: WordBufferPointer, config: OneOfPatternConfig, matches: dict[str, str]) -> bool:
    for pattern in config.pattern_list:
        new_pointer = pointer.word_buffer.copy_pointer(pointer)
        if pattern_matcher(new_pointer, pattern, matches) is True:
            if config.name is not None and config.name not in matches and not config.skip_adding_match:
                matches[config.name] = pointer.word_buffer.peek_words_between_pointers(pointer, new_pointer)
            pointer.move_to(new_pointer)
            new_pointer.word_buffer.delete_pointer(new_pointer)
            return True
        new_pointer.word_buffer.delete_pointer(new_pointer)
    return False


def closest_fuzzy_pattern_algorithm(pointer: WordBufferPointer, config: ClosestFuzzyPatternConfig, matches: dict[str, str]) -> bool:
    most_matching_pair: typing.Optional[(HandleIterateWordsResultPair, str)] = None
    for string in config.string_list:
        def work1(text) -> HandleIterateWordsWorkResult:
            score = fuzzy_match_score(text, string, config.fuzzy_matching)
            #print(f"string=\"{string}\" text=\"{text}\" score={score}")
            return HandleIterateWordsWorkResult(
                result=score,
                end_iteration=False
            )

        result_pairs = handle_iterate_words(work1, pointer, config.iterate_words_from, config.iterate_words_to)

        for pair in result_pairs:
            if (most_matching_pair is None or most_matching_pair[0].result < pair.result) and pair.result >= config.min_fuzzy_match_score:
                most_matching_pair = (pair, string)

    if most_matching_pair is None:
        return False

    original_text = pointer.read_words(most_matching_pair[0].word_count)
    if config.name not in matches and not config.skip_adding_match:
        matches[config.name] = original_text if config.save_original_text_instead else most_matching_pair[1]

    return True


def pattern_match(pattern_config: PatternConfig, value: str) -> typing.Optional[dict[str, str]]:
    word_buffer = WordBuffer()
    word_buffer.insert(value)
    matches = {}
    result = pattern_matcher(word_buffer.create_pointer_from_start(), pattern_config, matches)
    if result:
        return matches
    else:
        return None
