import os
import random
import math

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

def lsh_bands(signature, r):
    bands = []
    for i in range(0, len(signature), r):
        band = tuple(signature[i:i+r])
        bands.append(band)
    return bands

def find_candidates(signatures, r, b):
    buckets = {}
    for doc_name, sig in signatures.items():
        bands = lsh_bands(sig, r)
        for band_idx, band in enumerate(bands):
            key = (band_idx, band)
            if key not in buckets:
                buckets[key] = []
            buckets[key].append(doc_name)

    candidates = set()
    for doc_list in buckets.values():
        if len(doc_list) > 1:
            for i in range(len(doc_list)):
                for j in range(i+1, len(doc_list)):
                    pair = tuple(sorted([doc_list[i], doc_list[j]]))
                    candidates.add(pair)
    return candidates

dir_path = "/Users/kiran/Downloads/minhash"
docs = {}
for i in range(1, 5):
    docs[f'D{i}'] = read_file(os.path.join(dir_path, f'D{i}.txt'))

char3grams = {}
for name, text in docs.items():
    char3grams[name] = char_grams(text, 3)

t = 160
tau = 0.7

print("=== Question 3A: Finding best r and b ===\n")

best_error = float('inf')
best_r, best_b = None, None

for r in [1, 2, 4, 5, 8, 10, 16, 20, 32, 40]:
    if t % r == 0:
        b = t // r
        f_tau = 1 - (1 - tau**r)**b
        f_tau_minus = 1 - (1 - (tau-0.1)**r)**b
        f_tau_plus = 1 - (1 - (tau+0.1)**r)**b
        separation = abs(f_tau_plus - f_tau_minus)
        error = abs(f_tau - 0.5)
        print(f"r={r:2d}, b={b:2d}: f({tau:.1f})={f_tau:.4f}, separation={separation:.4f}")

        if error < best_error:
            best_error = error
            best_r, best_b = r, b

print(f"\nBest choice: r = {best_r}, b = {best_b}")

print("\n=== Question 3B: LSH probability for all pairs ===\n")

r = best_r
b = best_b
print(f"Using r={r}, b={b}\n")

pairs = [('D1', 'D2'), ('D1', 'D3'), ('D1', 'D4'), ('D2', 'D3'), ('D2', 'D4'), ('D3', 'D4')]

real_sims = {}
for d1, d2 in pairs:
    inter = len(char3grams[d1] & char3grams[d2])
    union = len(char3grams[d1] | char3grams[d2])
    real_sims[(d1, d2)] = inter / union if union > 0 else 0

hash_funcs = create_hash_functions(t)
signatures = {}
for name in docs:
    signatures[name] = min_hash(char3grams[name], hash_funcs)

candidates = find_candidates(signatures, r, b)

print(f"Candidate pairs from LSH: {candidates}\n")

for d1, d2 in pairs:
    pair = tuple(sorted([d1, d2]))
    s = real_sims[(d1, d2)]
    f_s = 1 - (1 - s**r)**b
    is_candidate = pair in candidates
    print(f"{d1} vs {d2}: Real sim = {s:.4f}, f(s) = {f_s:.4f}, Candidate = {is_candidate}")
