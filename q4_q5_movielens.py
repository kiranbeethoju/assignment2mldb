import random
import math

def read_movielens(filename):
    users = {}
    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split('\t')
            user_id = int(parts[0])
            movie_id = int(parts[1])
            if user_id not in users:
                users[user_id] = set()
            users[user_id].add(movie_id)
    return users

def exact_jaccard(set1, set2):
    inter = len(set1 & set2)
    union = len(set1 | set2)
    return inter / union if union > 0 else 0

def create_hash_functions(t):
    hash_funcs = []
    m = 20011
    for _ in range(t):
        a = random.randint(1, m-1)
        b = random.randint(0, m-1)
        hash_funcs.append(lambda x, a=a, b=b, m=m: (a * x + b) % m)
    return hash_funcs

def min_hash(user_movies, hash_funcs, all_movies):
    signature = []
    for h in hash_funcs:
        min_hash_val = float('inf')
        for movie in all_movies:
            if movie in user_movies:
                val = h(movie)
                if val < min_hash_val:
                    min_hash_val = val
        if min_hash_val == float('inf'):
            min_hash_val = 0
        signature.append(min_hash_val)
    return signature

def approx_jaccard(sig1, sig2):
    matches = 0
    for i in range(len(sig1)):
        if sig1[i] == sig2[i]:
            matches += 1
    return matches / len(sig1)

def lsh_bands(signature, r):
    bands = []
    for i in range(0, len(signature), r):
        band = tuple(signature[i:i+r])
        bands.append(band)
    return bands

def find_candidates(signatures, r, b):
    buckets = {}
    for user_id, sig in signatures.items():
        bands = lsh_bands(sig, r)
        for band_idx, band in enumerate(bands):
            key = (band_idx, band)
            if key not in buckets:
                buckets[key] = []
            buckets[key].append(user_id)

    candidates = set()
    for doc_list in buckets.values():
        if len(doc_list) > 1:
            for i in range(len(doc_list)):
                for j in range(i+1, len(doc_list)):
                    pair = tuple(sorted([doc_list[i], doc_list[j]]))
                    candidates.add(pair)
    return candidates

data_file = "u.data"

try:
    users = read_movielens(data_file)
    user_ids = list(users.keys())
    all_movies = set()
    for m in users.values():
        all_movies.update(m)
    all_movies = sorted(list(all_movies))

    print(f"Number of users: {len(users)}")
    print(f"Number of movies: {len(all_movies)}\n")

    print("=== Question 4: Min-Hashing on MovieLens ===\n")

    pairs = []
    for i in range(len(user_ids)):
        for j in range(i+1, len(user_ids)):
            pairs.append((user_ids[i], user_ids[j]))

    print("Computing exact Jaccard similarities...")
    exact_pairs = []
    for u1, u2 in pairs:
        sim = exact_jaccard(users[u1], users[u2])
        if sim >= 0.5:
            exact_pairs.append((u1, u2))
    print(f"Exact pairs with similarity >= 0.5: {len(exact_pairs)}")
    print("Exact pairs:", exact_pairs[:10], "..." if len(exact_pairs) > 10 else "")
    print()

    t_values = [50, 100, 200]
    num_runs = 5

    for t in t_values:
        print(f"\nUsing t = {t} hash functions:")
        avg_fp = 0
        avg_fn = 0

        for run in range(num_runs):
            print(f"  Run {run+1}:", end=" ")

            hash_funcs = create_hash_functions(t)
            signatures = {}
            for uid in user_ids:
                signatures[uid] = min_hash(users[uid], hash_funcs, all_movies)

            approx_pairs = []
            for u1, u2 in pairs:
                sim = approx_jaccard(signatures[u1], signatures[u2])
                if sim >= 0.5:
                    approx_pairs.append((u1, u2))

            fp = 0
            for pair in approx_pairs:
                if pair not in exact_pairs:
                    real_sim = exact_jaccard(users[pair[0]], users[pair[1]])
                    if real_sim < 0.5:
                        fp += 1

            fn = 0
            for pair in exact_pairs:
                if pair not in approx_pairs:
                    fn += 1

            print(f"FP={fp}, FN={fn}, Found pairs: {len(approx_pairs)}")
            if run == 0:
                print(f"    Approx pairs: {approx_pairs[:10]}{'...' if len(approx_pairs) > 10 else ''}")
            avg_fp += fp
            avg_fn += fn

        print(f"  Average FP: {avg_fp/num_runs:.1f}")
        print(f"  Average FN: {avg_fn/num_runs:.1f}")

    print("\n\n=== Question 5: LSH on MovieLens ===\n")

    thresholds = [0.6, 0.8]

    for tau in thresholds:
        print(f"\nFinding pairs with similarity >= {tau}\n")

        exact_pairs_tau = []
        for u1, u2 in pairs:
            sim = exact_jaccard(users[u1], users[u2])
            if sim >= tau:
                exact_pairs_tau.append((u1, u2))
        print(f"Exact pairs with similarity >= {tau}: {len(exact_pairs_tau)}")

        configs = [(2, 20), (4, 10), (5, 8), (8, 5), (10, 4), (20, 2)]

        for r, b in configs:
            print(f"\n  Using r={r}, b={b} (t={r*b}):")
            avg_fp = 0
            avg_fn = 0

            for run in range(num_runs):
                print(f"    Run {run+1}:", end=" ")

                t = r * b
                hash_funcs = create_hash_functions(t)
                signatures = {}
                for uid in user_ids:
                    signatures[uid] = min_hash(users[uid], hash_funcs, all_movies)

                candidates = find_candidates(signatures, r, b)

                approx_pairs_tau = []
                for u1, u2 in candidates:
                    sim = approx_jaccard(signatures[u1], signatures[u2])
                    if sim >= tau:
                        approx_pairs_tau.append((u1, u2))

                fp = 0
                for pair in approx_pairs_tau:
                    real_sim = exact_jaccard(users[pair[0]], users[pair[1]])
                    if real_sim < tau:
                        fp += 1

                fn = 0
                for pair in exact_pairs_tau:
                    if pair not in approx_pairs_tau:
                        fn += 1

                print(f"FP={fp}, FN={fn}")
                avg_fp += fp
                avg_fn += fn

            print(f"    Average FP: {avg_fp/num_runs:.1f}")
            print(f"    Average FN: {avg_fn/num_runs:.1f}")

except FileNotFoundError:
    print("Please download u.data from MovieLens 100k dataset")
    print("URL: http://www.grouplens.org/node/73")
    print("Place u.data in the same directory as this script")
