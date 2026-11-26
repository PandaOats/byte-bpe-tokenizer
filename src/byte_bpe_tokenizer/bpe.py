import string
from collections import Counter

# Count word chunks and punctuation runs while skipping whitespace
def split_count_text(text:str) -> dict:
    freq = Counter()
    current_chunk_start = 0
    walker = 0

    while walker < len(text):
        if text[walker] in string.whitespace:
            if current_chunk_start != walker:
                freq[text[current_chunk_start:walker]] += 1
            
            walker += 1
            while walker < len(text) and text[walker] in string.whitespace:
                walker += 1
            
            current_chunk_start = walker

        elif text[walker] in string.punctuation:
            if current_chunk_start != walker:
                freq[text[current_chunk_start:walker]] += 1

            current_chunk_start = walker
            walker += 1
            while walker < len(text) and text[walker] in string.punctuation:
                walker += 1
            freq[text[current_chunk_start:walker]] += 1

            current_chunk_start = walker

        else: 
            walker += 1

    if current_chunk_start != len(text):
        freq[text[current_chunk_start:walker]] += 1
            

    return freq

# Convert text into UTF-8 bytes
def text_to_byte_ids(text: str) -> list[int]:
    return list(text.encode("utf-8"))

# Count the occurences of pair of neighboring token IDs
def calc_pair_frequency(token_ids: list[int]) -> dict[tuple[int, int], int]:
    pass

# Replace token_ids matches of a pair with a new token ID
def merge_pair(token_ids: list[int], pair: tuple[int, int], new_id: int) -> list[int]:
    pass


if __name__ == "__main__":
    TESTING = False
    UNIT_TEST = True

    if TESTING:
        # Test options
        do_string_test, do_word_test = False, False
        do_split = True

        # Test inputs
        testWord = "Hello "
        testString = "Hello, my name is Panda, this is a test 🙄"

        encodedWord = testWord.encode("utf-8")
        encodedString = testString.encode("utf-8")

        assert(encodedString.decode("utf-8") == testString)
        

        if do_string_test:
            print("String: ", testString)
            print("UTF-8 Encoded (string): ", encodedString)
            print("----- text_to_byte_ids() -----\n", text_to_byte_ids(testString))
        
        if do_word_test:
            print("Word: ", testWord)
            print("Encoded: ", encodedWord)
            print("----- text_to_byte_ids() -----\n", text_to_byte_ids(testWord))

        if do_split:
            blank = ""
            many_punctutation = "!.???"
            scramble = "asndjia/.,,asdsd.,as,d/.as,"
            scramble_w_space = "sadna sasd ;;; asd;; a(;)"
            print([(key, value) for key, value in split_count_text(testString).items()])


    if UNIT_TEST:
        # text_to_byte_ids
        assert text_to_byte_ids("hello") == [104, 101, 108, 108, 111]
        assert text_to_byte_ids(" é ") == [32, 195, 169, 32]
        assert text_to_byte_ids("") == []

        # ----- split_count_text() ------

        # Empty input
        assert split_count_text("") == {}

        # Whitespace-only input
        assert split_count_text(" \t\n") == {}

        # Repeated words
        assert split_count_text("hello hello") == {
            "hello": 2,
        }

        # Leading, repeated, and trailing whitespace
        assert split_count_text(" a  b\n") == {
            "a": 1,
            "b": 1,
        }

        # Punctuation separated from words
        assert split_count_text("hi, there!") == {
            "hi": 1,
            ",": 1,
            "there": 1,
            "!": 1,
        }

        # Consecutive punctuation grouped together
        assert split_count_text("hi?!") == {
            "hi": 1,
            "?!": 1,
        }

        # Whitespace immediately after punctuation
        assert split_count_text("hi! there ") == {
            "hi": 1,
            "!": 1,
            "there": 1,
        }

        # Repeated words and punctuation runs without whitespace
        assert split_count_text("hi!!hi!!") == {
            "hi": 2,
            "!!": 2,
        }

        print("UNIT TEST PASSED")