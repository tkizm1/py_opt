# distutils: language=c

from libc.string cimport strlen
from libc.stdlib cimport malloc, free
from libc.stdio cimport printf # 保留printf以供调试，但不是必需

# LPS数组计算部分无需修改，它是正确的
cdef void prefixSuffixArray(const char* pat, int M, int* pps):
    cdef int length = 0
    pps[0] = 0
    cdef int i = 1
    while i < M:
        if pat[i] == pat[length]:
            length += 1
            pps[i] = length
            i += 1
        else:
            if length != 0:
                length = pps[length - 1]
            else:
                pps[i] = 0
                i += 1

cdef KMPAlgorithm(const char* text, const char* pattern):
    cdef int M = strlen(pattern)
    cdef long long N = strlen(text)
    arr = []
    
    if M == 0 or N == 0:
        return arr
        
    # Alocar memória para pps
    cdef int* pps = <int*>malloc(M * sizeof(int))
    if not pps:
        raise MemoryError()

    cdef long long i = 0  # index for text[]
    cdef int j = 0  # index for pattern[]

    try:
        prefixSuffixArray(pattern, M, pps)
        
        # 修复后的 KMP 搜索主循环
        while i < N:
            # 1. 匹配成功
            if pattern[j] == text[i]:
                i += 1
                j += 1
            
            # 2. 模式完全匹配
            # 必须在成功匹配后检查 j 是否达到 M
            if j == M:
                # 记录找到的模式的起始索引
                arr.append(i - j) 
                
                # 重置 j，继续查找下一个匹配
                # j 必须回溯到 pps[M-1] 的位置
                j = pps[j - 1]
            
            # 3. 匹配失败
            # 必须使用 'elif' 来保证与 'if pattern[j] == text[i]' 互斥
            elif i < N and pattern[j] != text[i]:
                if j != 0:
                    # j > 0 时，根据 pps 数组进行模式回溯
                    j = pps[j - 1]
                    # i 不变，在新 j 的位置重新比较
                else:
                    # j == 0 时，模式无法回溯，text 向前移动一位
                    i = i + 1
        
    finally:
        # Liberar a memória alocada
        free(pps)
    return arr

def main(text, pattern):
    # 确保 Python 字符串被正确编码为 bytes，以便 KMPAlgorithm 接收 const char*
    if isinstance(text, str):
        text = text.encode('utf-8')
    if isinstance(pattern, str):
        pattern = pattern.encode('utf-8')
        
    return KMPAlgorithm(text, pattern)