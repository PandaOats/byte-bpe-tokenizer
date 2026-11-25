import string
from collections import Counter

def split_count_text(text:str) -> dict:
    freq = Counter()
    start = 0
    
    for i, char in enumerate(text):
        next_is_boundary = (
            i + 1 == len(text)
            or text[i + 1] in string.whitespace
            or text[i + 1] in string.punctuation
        )

        if (char in string.whitespace 
            or char in string.punctuation and next_is_boundary):
            if start != i:
                freq[text[start:i]] += 1
            freq[char] += 1
            start = i + 1

    if start != len(text):
        freq[text[start:]] += 1

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
            print([(key, value) for key, value in split_count_text(" ---!mkfasfona asd'asdasd'a.  \t").items()])


    if UNIT_TEST:
        # text_to_byte_ids
        assert text_to_byte_ids("hello") == [104, 101, 108, 108, 111]
        assert text_to_byte_ids(" é ") == [32, 195, 169, 32]
        assert text_to_byte_ids("") == []

        # ----- split_count_text() ------

        # Empty input
        assert split_count_text("") == {}

        # Repeated words
        assert split_count_text("hello hello") == {
            "hello": 2,
            " ": 1,
        }

        # Leading, repeated, and trailing whitespace
        assert split_count_text(" a  b\n") == {
            " ": 3,
            "a": 1,
            "b": 1,
            "\n": 1,
        }

        # Punctuation
        assert split_count_text("hi, there!") == {
            "hi": 1,
            ",": 1,
            " ": 1,
            "there": 1,
            "!": 1,
        }

        assert split_count_text("hi?!") == {
            "hi": 1,
            "?": 1,
            "!": 1,
        }

        print("UNIT TEST PASSED")