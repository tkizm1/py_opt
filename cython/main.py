# main.py
import time

import kmp_cython

with open('../random_str.txt') as f:
    text = f.read()
pattern = "CyDw"
start_time = time.time()
result = kmp_cython.main(text, pattern)
end_time = time.time()
print(f"Execution Time: {end_time - start_time:.4f} seconds")
print(f"Total Matches Found: {len(result)}")
print(result)