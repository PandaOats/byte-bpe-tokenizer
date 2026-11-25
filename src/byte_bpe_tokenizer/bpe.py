testString = "Hello, my name is Panda, this is a test 🙄"
encodedTest = testString.encode("utf-8")

assert(encodedTest.decode("utf-8") == testString)
"""
print("String: ", testString)
print("UTF-8 Encoded (string): ", encodedTest)
print("UTF-8 Encoded (byte): ", [byte for byte in encodedTest])
"""

# Convert text into UTF-8 bytes
def text_to_byte_ids(text: str) -> list[int]:
    pass

# Count the occurences of pair of neighboring token IDs
def calc_pair_frequency(token_ids: list[int]) -> dict[tuple[int, int], int]:
    pass

# Replace token_ids matches of a pair with a new token ID
def merge_pair(token_ids: list[int], pair: tuple[int, int], new_id: int) -> list[int]:
    pass



""""
unicodeTest = [ord(c) for c in testString]
print("\nUnicode: ", unicodeTest)
print("Revert: ", [chr(i) for i in unicodeTest])
"""
