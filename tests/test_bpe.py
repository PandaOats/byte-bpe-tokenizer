from collections import Counter
from pathlib import Path

import pytest

from byte_bpe_tokenizer.bpe import (
    calc_pair_frequency,
    encode_chunk_frequencies,
    merge_pair,
    split_count_file,
    split_count_text,
    train_bpe,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", {}),
        (" \t\n", {}),
        ("hello hello", {"hello": 2}),
        (" a  b\n", {"a": 1, "b": 1}),
        ("hi, there!", {"hi": 1, ",": 1, "there": 1, "!": 1}),
        ("hi?!", {"hi": 1, "?!": 1}),
        ("hi! there ", {"hi": 1, "!": 1, "there": 1}),
        ("hi!!hi!!", {"hi": 2, "!!": 2}),
    ],
)
def test_split_count_text(text, expected):
    assert split_count_text(text) == expected


def test_split_count_text_accumulates_into_supplied_counter():
    chunk_freq = Counter()
    assert split_count_text("hi!! hi", chunk_freq) is chunk_freq
    assert chunk_freq == {"hi": 2, "!!": 1}
    assert split_count_text("hi!! there", chunk_freq=chunk_freq) is chunk_freq
    assert chunk_freq == {"hi": 3, "!!": 2, "there": 1}


def test_split_count_text_preserves_counter_for_whitespace():
    chunk_freq = Counter({"hi": 3, "!!": 2, "there": 1})
    assert split_count_text(" \t\n", chunk_freq) is chunk_freq
    assert chunk_freq == {"hi": 3, "!!": 2, "there": 1}


def test_split_count_text_creates_independent_counters():
    first_counts = split_count_text("hi!!")
    second_counts = split_count_text("hi!!", None)
    assert first_counts == second_counts == {"hi": 1, "!!": 1}
    assert first_counts is not second_counts


@pytest.fixture
def corpus_path(tmp_path: Path) -> str:
    file_path = tmp_path / "corpus.txt"
    file_path.write_bytes("café!!\r\n\r\ncafé?!\n🙄!!\rfin".encode("utf-8"))
    return str(file_path)


def test_split_count_file_handles_utf8_and_mixed_line_endings(corpus_path: str):
    assert split_count_file(corpus_path) == {
        "café": 2,
        "!!": 2,
        "?!": 1,
        "🙄": 1,
        "fin": 1,
    }


def test_split_count_file_accumulates_into_supplied_counter(corpus_path: str):
    chunk_freq = Counter({"café": 3, "existing": 1})
    assert split_count_file(corpus_path, chunk_freq=chunk_freq) is chunk_freq
    assert chunk_freq == {
        "café": 5,
        "existing": 1,
        "!!": 2,
        "?!": 1,
        "🙄": 1,
        "fin": 1,
    }


def test_split_count_file_handles_empty_file(tmp_path: Path):
    file_path = tmp_path / "empty.txt"
    file_path.write_bytes(b"")
    assert split_count_file(str(file_path)) == {}


def test_split_count_file_raises_for_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        split_count_file(str(tmp_path / "missing.txt"))


def test_split_count_file_can_retry_after_late_decoding_error(tmp_path: Path):
    file_path = tmp_path / "corpus.txt"
    valid_lines = b"hi!!\n" * 10_000
    file_path.write_bytes(valid_lines + b"\xff")
    chunk_freq = Counter({"hi": 2, "existing": 1})

    with pytest.raises(UnicodeDecodeError):
        split_count_file(str(file_path), chunk_freq=chunk_freq)
    assert chunk_freq == {"hi": 2, "existing": 1}

    file_path.write_bytes(valid_lines)
    assert split_count_file(str(file_path), chunk_freq=chunk_freq) is chunk_freq
    assert chunk_freq == {"hi": 10_002, "!!": 10_000, "existing": 1}


@pytest.mark.parametrize(
    ("chunk_frequencies", "expected"),
    [
        ({}, {}),
        ({"abab": 2, "!": 3}, {(97, 98, 97, 98): 2, (33,): 3}),
        ({"é": 4, "🙄": 1}, {(195, 169): 4, (240, 159, 153, 132): 1}),
    ],
)
def test_encode_chunk_frequencies(chunk_frequencies, expected):
    assert encode_chunk_frequencies(chunk_frequencies) == expected


@pytest.mark.parametrize(
    ("encoded_freq", "expected"),
    [
        ({}, {}),
        ({(97,): 3}, {}),
        ({(97, 98, 97, 98): 3}, {(97, 98): 6, (98, 97): 3}),
        ({(97, 97, 97): 2}, {(97, 97): 4}),
        ({(256, 257): 1}, {(256, 257): 1}),
    ],
)
def test_calc_pair_frequency(encoded_freq, expected):
    assert calc_pair_frequency(encoded_freq) == expected


@pytest.mark.parametrize(
    ("token_ids", "pair", "expected"),
    [
        ([], (97, 98), []),
        ([97], (97, 98), [97]),
        ([97, 98, 97, 98], (97, 98), [256, 256]),
        ([99, 97, 98, 100], (97, 98), [99, 256, 100]),
        ([97, 97, 97], (97, 97), [256, 97]),
    ],
)
def test_merge_pair(token_ids, pair, expected):
    assert merge_pair(token_ids, pair, 256) == expected


def test_train_bpe_weights_repeated_chunks():
    vocab, merges = train_bpe("xyxy abc abc abc ab", 258)
    assert len(vocab) == 258
    assert vocab[256] == b"ab"
    assert vocab[257] == b"abc"
    assert merges == {(97, 98): 256, (256, 99): 257}


def test_train_bpe_stops_when_no_pairs_remain():
    vocab, merges = train_bpe("x! y?", 300)
    assert vocab == {byte_id: bytes([byte_id]) for byte_id in range(256)}
    assert merges == {}
