# 一个随机字符串生成器
import random
import string

import random
import string
import os

def generate_and_write_random_string_in_chunks(length, filename, chunk_size=10**7):
    """
    分块生成指定长度的随机字符串，并写入文件。
    
    参数:
    length (int): 目标总长度（字符数）。
    filename (str): 要写入的文件名。
    chunk_size (int): 每次生成和写入的字符块大小（默认为 1000 万字符）。
    """
    # 定义字符集（与原代码一致）
    characters = string.ascii_letters + string.digits + string.whitespace
    total_written = 0
    
    # 采用 'w' 模式打开文件进行写入
    with open(filename, 'w', encoding='utf-8') as f:
        while total_written < length:
            # 确定当前块的大小，确保不超过总长度
            current_chunk_size = min(chunk_size, length - total_written)
            
            # **优化点 1: 使用 random.choices 一次性生成多个字符**
            # random.choices 批量生成效率通常高于循环调用 random.choice
            chunk_list = random.choices(characters, k=current_chunk_size)
            chunk = ''.join(chunk_list)
            
            # **优化点 2: 立即写入文件 (Streaming I/O)**
            # 避免将整个大字符串保存在内存中
            f.write(chunk)
            
            total_written += current_chunk_size
            
            # 可选：打印进度条（对于长时间运行的程序很有用）
            # print(f"进度: {total_written / 10**6:.2f} MB / {length / 10**6:.2f} MB", end='\r')


# 设定目标长度和文件名
TARGET_LENGTH = 5 * 1000 * 1000 * 1000
FILENAME = './random_str.txt'

# 执行优化的分块写入过程
# 注意：即使优化后，写入 5GB 数据到磁盘仍需要数分钟甚至更久，具体取决于您的硬件速度。
generate_and_write_random_string_in_chunks(TARGET_LENGTH, FILENAME)