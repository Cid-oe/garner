"""Deterministic inputs for the differential check: random words plus combinations of the
letter groups Metaphone treats specially, and some mixed-case and punctuation noise."""
import random
import string

random.seed(42)
CHUNKS = ["TCH", "SCH", "GH", "PH", "TH", "WH", "WR", "KN", "GN", "PN", "AE", "X", "CIA", "TIO", "SIO",
          "SH", "DGE", "MB", "CC", "CK", "Q", "Z", "V", "Y", "W", "H", "GG", "NN"]
words = set()
for _ in range(200000):
    r = random.random()
    if r < 0.5:
        w = "".join(random.choice(string.ascii_uppercase) for _ in range(random.randint(1, 9)))
    elif r < 0.9:
        w = "".join(random.choice(CHUNKS + list("AEIOU")) for _ in range(random.randint(1, 5)))
    else:
        w = "".join(random.choice(string.ascii_letters + " -'1") for _ in range(random.randint(1, 8)))
    words.add(w)
print("\n".join(sorted(words)))
