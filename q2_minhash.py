import os
import random

def read_file(filename):
    with open(filename, 'r') as f:
        return f.read().strip()

def char_grams(text, k):
    grams = set()
    for i in range(len(text) - k + 1):
        grams.add(text[i:i+k])
    return grams

def create_hash_functions(t):
    hash_funcs = []
    m = 10007
    for _ in range(t):
        a = random.randint(1, m-1)
        b = random.randint(0, m-1)
        hash_funcs.append(lambda x, a=a, b=b, m=m: (a * x + b) % m)
    return hash_funcs

def min_hash(grams, hash_funcs):
    signature = []
    for h in hash_funcs:
        min_hash_val = float('inf')
        for gram in grams:
            val = h(hash(gram))
            if val < min_hash_val:
                min_hash_val = val
        signature.append(min_hash_val)
    return signature

def approx_jaccard(sig1, sig2):
    matches = 0
    for i in range(len(sig1)):
        if sig1[i] == sig2[i]:
            matches += 1
    return matches / len(sig1)

dir_path = "/Users/kiran/Downloads/minhash"

d1_text = read_file(os.path.join(dir_path, 'D1.txt'))
d2_text = read_file(os.path.join(dir_path, 'D2.txt'))

d1_grams = char_grams(d1_text, 3)
d2_grams = char_grams(d2_text, 3)

exact_jaccard = len(d1_grams & d2_grams) / len(d1_grams | d2_grams)
print(f"Exact Jaccard similarity (D1 vs D2): {exact_jaccard:.4f}\n")

t_values = [20, 60, 150, 300, 600]

for t in t_values:
    hash_funcs = create_hash_functions(t)
    sig1 = min_hash(d1_grams, hash_funcs)
    sig2 = min_hash(d2_grams, hash_funcs)
    approx_sim = approx_jaccard(sig1, sig2)
    error = abs(approx_sim - exact_jaccard)
    print(f"t = {t:3d}: Approx Jaccard = {approx_sim:.4f}, Error = {error:.4f}")
