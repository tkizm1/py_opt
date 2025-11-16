import time

class KMP:
    def partial(self, pattern):
        """ Calculate partial match table: String -> [Int]"""
        ret = [0]
        
        for i in range(1, len(pattern)):
            j = ret[i - 1]
            while j > 0 and pattern[j] != pattern[i]:
                j = ret[j - 1]
            ret.append(j + 1 if pattern[j] == pattern[i] else j)
        return ret
        
    def search(self, T, P):
        """ 
        KMP search main algorithm: String -> String -> [Int] 
        Return all the matching position of pattern string P in T
        """
        partial, ret, j = self.partial(P), [], 0
        
        for i in range(len(T)):
            while j > 0 and T[i] != P[j]:
                j = partial[j - 1]
            if T[i] == P[j]: j += 1
            if j == len(P): 
                ret.append(i - (j - 1))
                j = partial[j - 1]
            
        return ret

if __name__ == '__main__':
    with open('random_str.txt') as f:
        text = f.read()
    pattern = "CyDw"
    # print(p1)
    # p1 = "aa"
    # t1 = "aaaaaaaa"
    kmp = KMP()
    start_time = time.time()
    res = kmp.search(text, pattern)
    end_time = time.time()
    print(f"Execution Time: {end_time - start_time:.4f} seconds")
    print(f"Total Matches Found: {len(res)}")
    print(res)

# from 00:08:01 to 00:14:38