import math
import multiprocessing
from multiprocessing import freeze_support
import os
import tempfile
import mmap
import time

pattern = 'CyDw'
# 1. get total length of the text
FILE_CONTENT = ''
with open('random_str.txt', 'r') as f:
    FILE_CONTENT=f.read()
# print(FILE_CONTENT)
# 2. calculate chunk size
NUM_PROCESSES = 4 # os.cpu_count()
L = len(pattern)
OVERLAP_SIZE = len(pattern) - 1
STANDARD_CHUNK_SIZE = len(FILE_CONTENT) // NUM_PROCESSES + OVERLAP_SIZE
print(STANDARD_CHUNK_SIZE)

SEARCH_TERM = pattern

# 定义一个全局变量来存储文件名 (子进程需要知道它)
GLOBAL_TEMP_FILE_PATH = None 

# --- 基于 mmap 的并行搜索函数 ---

def parallel_search_mmap(start_index, end_index, file_path):
    """
    接收 (start_index, end_index, file_path)，使用 mmap 访问文件内容，
    避免内存溢出。
    """
    # start_index, end_index, file_path = task_params
    
    # 从全局获取共享参数
    global SEARCH_TERM, OVERLAP_SIZE, L 
    
    # --- 关键步骤：使用 mmap 映射文件 ---
    with open(file_path, 'rb') as f:
        # mmap.mmap 会将整个文件映射到内存，但多个进程共享同一个物理内存块
        # 并允许我们像访问字符串一样访问文件内容
        # length=0 表示映射整个文件
        # access=mmap.ACCESS_READ 表示只读
        with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as m:
            # m 现在可以像 bytes 对象一样使用
            
            # 计算实际的读取起始点：start_index 减去 overlap_size
            actual_start = max(0, start_index - OVERLAP_SIZE) 
            
            # 确定要处理的缓冲区内容 (从 mmap 对象中切片)
            # 注意: mmap 切片返回 bytes，如果搜索词是 str，需要确保编码一致
            buffer = m[actual_start : end_index].decode('utf-8')
            
            # 计算缓冲区在原始文件中的起始偏移量
            buffer_file_start_offset = actual_start
            
            # --- 搜索逻辑 ---
            matches = []
            search_start_index = 0
            
            while True:
                # 在 buffer 中搜索
                match_index_in_buffer = buffer.find(SEARCH_TERM, search_start_index)
                
                if match_index_in_buffer == -1:
                    break
                    
                # 转换为原始文件偏移量
                file_match_offset = buffer_file_start_offset + match_index_in_buffer
                
                # 排除重叠区域的重复匹配
                if file_match_offset >= start_index:
                    matches.append(file_match_offset)
                
                # 继续搜索
                search_start_index = match_index_in_buffer + L 

    # print(f"[Process {os.getpid()}] Start: {start_index}, End: {end_index}, Matches: {matches}")
    
    return matches

# --- 主执行逻辑 ---

def run_parallel_search_mmap(file_content, search_term, num_processes):
    
    # 1. 将文件内容写入一个临时文件 (关键的内存卸载步骤)
    file_content = file_content.encode('utf8')
    with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmp_file:
        tmp_file.write(file_content)
        file_path = tmp_file.name
        
    print(f"File content written to temporary file: {file_path}")
    
    # 确保全局变量被设置，供子进程使用
    global SEARCH_TERM, L, OVERLAP_SIZE, FILE_SIZE
    SEARCH_TERM = search_term
    L = len(search_term)
    OVERLAP_SIZE = max(0, L - 1) 
    FILE_SIZE = len(file_content)

    # 2. 确定每个进程的理想块大小 (不含重叠)
    chunk_size = math.ceil(FILE_SIZE / num_processes)
    
    tasks = []
    
    # 3. 划分任务范围 (只包含起始和结束索引，以及文件路径)
    for i in range(num_processes):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, FILE_SIZE)
        
        if start >= FILE_SIZE:
            break
            
        # 任务只包含 (start, end, file_path)
        tasks.append((start, end, file_path))
        
        print(f"Task {i+1}: Main Range [{start} to {end}]")


    # 4. 使用进程池和 imap_unordered 执行任务
    print(f"\nStarting parallel search with {len(tasks)} processes using mmap...")
    
    final_matches = []
    
    with multiprocessing.Pool(processes=len(tasks)) as pool:
        # 使用 imap_unordered 和 starmap 的结合 (starmap 的迭代器版本)
        for chunk_matches in pool.starmap(parallel_search_mmap, tasks):
            final_matches.extend(chunk_matches) 

    # 5. 清理临时文件
    os.remove(file_path)
    print(f"\nTemporary file cleaned up: {file_path}")
    
    # 6. 排序结果
    final_matches.sort()
    
    return final_matches

# --- 运行和输出 ---

NUM_PROCESSES = 4 

# print(f"File Size: {FILE_SIZE}, Search Term: '{SEARCH_TERM}' (L={L})\n")
if __name__ == "__main__":
    # 执行并行搜索
    start_time = time.time()
    final_results = run_parallel_search_mmap(FILE_CONTENT, SEARCH_TERM, NUM_PROCESSES)
    end_time = time.time()

    # 最终输出
    print(f"Execution Time: {end_time - start_time:.4f} seconds")
    print("\n--- Final Consolidated and Sorted Matches ---")
    print(f"Total Matches Found: {len(final_results)}")
    print(f"Offsets: {final_results}")
# print(f"Execution Time: {end_time - start_time:.4f} seconds")