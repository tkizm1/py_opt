# main.py

import time
import str_compare

with open('../random_str.txt') as f:
    text = f.read()
pattern = "CyDw"


start_time = time.time()

# 调用 Rust 的并行搜索函数
final_results = str_compare.run_parallel_search_rs(
    text, 
    pattern, 
    4
)

end_time = time.time()
# 最终输出
print("\n--- Final Consolidated and Sorted Matches ---")
print(f"Total Matches Found: {len(final_results)}")
# print(f"Offsets: {final_results[:10]}...") # 只打印前 10 个以防结果过多
print(f"Time taken (Rust+Rayon): {end_time - start_time:.4f} seconds")
# if index != -1:
#     print(f"Padrão encontrado no índice: {index}")
# else:
#     print("Padrão não encontrado.")
