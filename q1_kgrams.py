import os

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read().strip()

def char_grams(text, k):
    grams = set()
    for i in range(len(text) - k + 1):
        grams.add(text[i:i+k])
    return grams

def word_grams(text, k):
    words = text.split()
    grams = set()
    for i in range(len(words) - k + 1):
        grams.add(' '.join(words[i:i+k]))
    return grams

def jaccard(set1, set2):
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union > 0 else 0

dir_path = "/Users/kiran/Downloads/minhash"
docs = {}
for i in range(1, 5):
    docs[f'D{i}'] = read_file(os.path.join(dir_path, f'D{i}.txt'))

print("=== Question 1A: k-grams for all documents ===\n")

char2grams = {}
char3grams = {}
word2grams = {}

for name, text in docs.items():
    char2grams[name] = char_grams(text, 2)
    char3grams[name] = char_grams(text, 3)
    word2grams[name] = word_grams(text, 2)
    print(f"{name} 2-char grams: {len(char2grams[name])}")
    print(f"{name} 3-char grams: {len(char3grams[name])}")
    print(f"{name} 2-word grams: {len(word2grams[name])}")
    print()

print("=== Question 1B: Jaccard similarity for all pairs ===\n")

gram_types = {'2-char': char2grams, '3-char': char3grams, '2-word': word2grams}
pairs = [('D1', 'D2'), ('D1', 'D3'), ('D1', 'D4'), ('D2', 'D3'), ('D2', 'D4'), ('D3', 'D4')]

for gtype, grams in gram_types.items():
    print(f"\n{gtype} grams:")
    for d1, d2 in pairs:
        sim = jaccard(grams[d1], grams[d2])
        print(f"  {d1} vs {d2}: {sim:.4f}")
