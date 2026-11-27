import string
from collections import Counter

# Count word chunks and punctuation runs while skipping whitespace 
def split_count_text(text: str, chunk_freq: Counter[str] | None = None) -> Counter[str]:
    freq = Counter() if chunk_freq is None else chunk_freq

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


def split_count_file(file_path: str, initial_line: int = 0, chunk_freq: Counter[str] | None = None) -> Counter[str]:
    file_counts: Counter[str] = Counter()

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            split_count_text(line, file_counts)

    if chunk_freq is None:
        return file_counts

    chunk_freq.update(file_counts)
    return chunk_freq

# Convert chunk keys into byte-ID tuples, keeping their frequencies
def encode_chunk_frequencies(chunk_frequencies: dict[str, int]) -> dict[tuple[int, ...], int]:
    encoded_freq = dict()
    for key, value in chunk_frequencies.items():
        encoded_freq[tuple(key.encode("utf-8"))] = value

    return encoded_freq

# Count the occurences of pair of neighboring token IDs
def calc_pair_frequency(encoded_freq: dict[tuple[int, ...], int]) -> Counter[tuple[int, int]]:
    pair_freq = Counter()
    for encodings, freq in encoded_freq.items():
        for i in range(len(encodings) - 1):
            pair_freq[encodings[i], encodings[i + 1]] += freq

    return pair_freq

# Replace token_ids matches of a pair with a new token ID
def merge_pair(token_ids: list[int], pair: tuple[int, int], new_id: int) -> list[int]:
    merged_ids = []
    i = 0

    while i < len(token_ids):
        if i + 1 < len(token_ids) and (token_ids[i], token_ids[i + 1]) == pair:
            merged_ids.append(new_id)
            i += 2
        else:
            merged_ids.append(token_ids[i])
            i += 1

    return merged_ids

# Train vocabulary up to vocab_size
def train_bpe(text: str, vocab_size: int) -> tuple[dict[int, bytes], dict[tuple[int, int], int]]:
    vocab = {byte_id: bytes([byte_id]) for byte_id in range(256)}
    merges: dict[tuple[int, int], int] = dict()

    chunk_freq = split_count_text(text)
    encoded_freq = encode_chunk_frequencies(chunk_freq)

    while len(vocab) < vocab_size:
        pair_freq = calc_pair_frequency(encoded_freq)
        if not pair_freq:
            break

        best_pair, _ = pair_freq.most_common(1)[0]
        new_id = len(vocab)
        merges[best_pair] = new_id

        left_id, right_id = best_pair
        vocab[new_id] = vocab[left_id] + vocab[right_id]
        
        # Make new encoded_freq given the merges
        merged_freq = dict()
        for token_ids, freq in encoded_freq.items():
            merged_ids = tuple(merge_pair(list(token_ids), best_pair, new_id))
            merged_freq[merged_ids] = freq

        encoded_freq = merged_freq

    return vocab, merges


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
        #assert text_to_byte_ids("hello") == [104, 101, 108, 108, 111]
        #assert text_to_byte_ids(" é ") == [32, 195, 169, 32]
        #assert text_to_byte_ids("") == []

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

        # Reuse an empty counter and accumulate across calls
        chunk_freq = Counter()
        assert split_count_text("hi!! hi", chunk_freq) is chunk_freq
        assert chunk_freq == {"hi": 2, "!!": 1}
        assert split_count_text("hi!! there", chunk_freq=chunk_freq) is chunk_freq
        assert chunk_freq == {"hi": 3, "!!": 2, "there": 1}

        # Whitespace-only input leaves an existing counter's counts intact
        assert split_count_text(" \t\n", chunk_freq) is chunk_freq
        assert chunk_freq == {"hi": 3, "!!": 2, "there": 1}

        # Omitted and explicit None each give an independent counter
        first_counts = split_count_text("hi!!")
        second_counts = split_count_text("hi!!", None)
        assert first_counts == second_counts == {"hi": 1, "!!": 1}
        assert first_counts is not second_counts

        # ----- split_count_file() -----

        from pathlib import Path
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "corpus.txt"

            # Count UTF-8 chunks across lines, including a final line without a newline
            file_path.write_bytes("café!!\r\n\r\ncafé?!\n🙄!!\rfin".encode("utf-8"))
            assert split_count_file(str(file_path)) == {
                "café": 2,
                "!!": 2,
                "?!": 1,
                "🙄": 1,
                "fin": 1,
            }

            # Update and return the supplied counter
            chunk_freq = Counter({"café": 3, "existing": 1})
            assert split_count_file(str(file_path), chunk_freq=chunk_freq) is chunk_freq
            assert chunk_freq == {
                "café": 5,
                "existing": 1,
                "!!": 2,
                "?!": 1,
                "🙄": 1,
                "fin": 1,
            }

            # Empty files produce no chunks
            file_path.write_bytes(b"")
            assert split_count_file(str(file_path)) == {}

            # Missing-file errors reach the caller
            try:
                split_count_file(str(Path(temp_dir) / "missing.txt"))
            except FileNotFoundError:
                pass
            else:
                raise AssertionError("Expected FileNotFoundError for a missing file")

            # A late decoding error leaves the supplied counter safe to retry
            valid_lines = b"hi!!\n" * 10_000
            file_path.write_bytes(valid_lines + b"\xff")
            chunk_freq = Counter({"hi": 2, "existing": 1})
            try:
                split_count_file(str(file_path), chunk_freq=chunk_freq)
            except UnicodeDecodeError:
                pass
            else:
                raise AssertionError("Expected UnicodeDecodeError for invalid UTF-8")
            assert chunk_freq == {"hi": 2, "existing": 1}

            file_path.write_bytes(valid_lines)
            assert split_count_file(str(file_path), chunk_freq=chunk_freq) is chunk_freq
            assert chunk_freq == {"hi": 10_002, "!!": 10_000, "existing": 1}

        # ----- encode_chunk_frequencies() -----

        # Empty input
        assert encode_chunk_frequencies({}) == {}

        # ASCII chunks keep their frequencies
        assert encode_chunk_frequencies({"abab": 2, "!": 3}) == {
            (97, 98, 97, 98): 2,
            (33,): 3,
        }

        # Characters that require multiple UTF-8 bytes
        assert encode_chunk_frequencies({"é": 4, "🙄": 1}) == {
            (195, 169): 4,
            (240, 159, 153, 132): 1,
        }

        # ----- calc_pair_frequency() -----

        # Empty and single-token inputs
        assert calc_pair_frequency({}) == {}
        assert calc_pair_frequency({(97,): 3}) == {}

        # Repeated pairs, ordering, and frequency weighting
        assert calc_pair_frequency({(97, 98, 97, 98): 3}) == {
            (97, 98): 6,
            (98, 97): 3,
        }

        # Overlapping occurrences
        assert calc_pair_frequency({(97, 97, 97): 2}) == {
            (97, 97): 4,
        }

        # Learned token IDs above 255
        assert calc_pair_frequency({(256, 257): 1}) == {
            (256, 257): 1,
        }

        # ----- merge_pair() -----

        # Empty and single-token inputs
        assert merge_pair([], (97, 98), 256) == []
        assert merge_pair([97], (97, 98), 256) == [97]

        # Repeated non-overlapping matches
        assert merge_pair([97, 98, 97, 98], (97, 98), 256) == [256, 256]

        # Unmatched tokens are preserved
        assert merge_pair([99, 97, 98, 100], (97, 98), 256) == [99, 256, 100]

        # Overlapping matches are merged from left to right
        assert merge_pair([97, 97, 97], (97, 97), 256) == [256, 97]

        # ----- train_bpe() -----

        # Repeated chunks outweigh a pair that occurs twice in one chunk
        vocab, merges = train_bpe("xyxy abc abc abc ab", 258)
        assert len(vocab) == 258
        assert vocab[256] == b"ab"
        assert vocab[257] == b"abc"
        assert merges == {(97, 98): 256, (256, 99): 257}

        # Single-byte chunks have no pairs, even across punctuation and spaces
        vocab, merges = train_bpe("x! y?", 300)
        assert vocab == {byte_id: bytes([byte_id]) for byte_id in range(256)}
        assert merges == {}

        print("UNIT TEST PASSED")
