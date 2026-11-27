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
