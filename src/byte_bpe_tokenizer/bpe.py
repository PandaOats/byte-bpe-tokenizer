# Convert text into UTF-8 bytes
def text_to_byte_ids(text: str) -> list[int]:
    byte_ids = text.encode("utf-8")
    return [int(i) for i in byte_ids]

# Count the occurences of pair of neighboring token IDs
def calc_pair_frequency(token_ids: list[int]) -> dict[tuple[int, int], int]:
    pass

# Replace token_ids matches of a pair with a new token ID
def merge_pair(token_ids: list[int], pair: tuple[int, int], new_id: int) -> list[int]:
    pass


TESTING = False
UNIT_TEST = True

if TESTING:
    # Test options
    do_string_test, do_word_test = True, False

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


if UNIT_TEST:
    # text_to_byte_ids
    assert text_to_byte_ids("hello") == [104, 101, 108, 108, 111]
    assert text_to_byte_ids(" é ") == [32, 195, 169, 32]
    assert text_to_byte_ids("") == []