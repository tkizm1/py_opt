---
# try also 'default' to start simple
theme: seriph
# random image from a curated Unsplash collection by Anthony
# like them? see https://unsplash.com/collections/94734566/slidev
background: https://cdn.jsdelivr.net/gh/slidevjs/slidev-covers@main/static/SgtU7sK6oP4.webp
# some information about your slides (markdown enabled)
# 如何加速python代码
title: Boosting Python Performance with Rust and C
info: |
  ## Slidev Starter Template
  Presentation slides for developers.

  Learn more at [Sli.dev](https://sli.dev)
# apply UnoCSS classes to the current slide
class: text-center
# https://sli.dev/features/drawing
drawings:
  persist: false
# slide transition: https://sli.dev/guide/animations.html#slide-transitions
transition: slide-left
# enable MDC Syntax: https://sli.dev/features/mdc
mdc: true
---

# Boosting Python Performance with Rust and C

Kevin, Tang

<div @click="$slidev.nav.next" class="mt-12 py-1" hover:bg="white op-10">
  Let's begin<carbon:arrow-right />
</div>

<!-- <div class="abs-br m-6 text-xl">
  <button @click="$slidev.nav.openInEditor()" title="Open in Editor" class="slidev-icon-btn">
    <carbon:edit />
  </button>
  <a href="https://github.com/slidevjs/slidev" target="_blank" class="slidev-icon-btn">
    <carbon:logo-github />
  </a>
</div> -->

<!--
The last comment block of each slide will be treated as slide notes. It will be visible and editable in Presenter Mode along with the slide. [Read more in the docs](https://sli.dev/guide/syntax.html#notes)
-->

---
transition: fade-out
---

Today, I want to talk about a topic about optimize python performance.

Before switching to a different programming language, I think we can try the following approaches: 

- **Algorithms and Data Structures**
- **Choose built-in data structures wisely**
- **Optimize Loop Operations**
- **Memory Management/Iteration**
- **Caching Mechanism**


---
transition: fade-out
---
With the power of AI, try using copilot to optimize your code

My personal favorite prompt:

> check what is missing. Cover validation, development standards and any other optimisation you can recommend

<!-- ![alt text](./assets/image.png = 300x200) -->
<img src="./assets/image.png" alt="alt text" width="600" height="300" />

<!--
You can have `style` tag in markdown to override the style for the current page.
Learn more: https://sli.dev/features/slide-scope-style
-->

<style>
h1 {
  background-color: #2B90B6;
  background-image: linear-gradient(45deg, #4EC5D4 10%, #146b8c 20%);
  background-size: 100%;
  -webkit-background-clip: text;
  -moz-background-clip: text;
  -webkit-text-fill-color: transparent;
  -moz-text-fill-color: transparent;
}
</style>

<!--
Here is another comment.
-->

---
transition: fade-out
---

When optimizations in Python are not sufficient, we can consider integrating Rust or C to enhance performance.

Nowadays, there are many libraries that allow seamless integration between Python and Rust/C, such as PyO3 for Rust and Cython for C.

These libraries enable developers to write performance-critical code in Rust or C and call it from Python, combining the ease of use of Python with the speed of compiled languages.

Here are some libraries already use C/C++ or Rust to speed up python performance:
- NumPy is based on C
- Pandas is based on C
- uv is based on pyo3, pyo3 is rust bindings for python
- gevent is based on cython，cython is C bindings for python

I will try to show you how to do that in the following slides.


---
transition: slide-up
level: 2
---

# Finding sensitive words in a document

> I want to use Python to find the locations of all sensitive words in a document.

### Comparison of Common Keyword Search Algorithms

| Algorithm | Primary Purpose | Search Time Complexity | Memory Usage | Python Suitability |
| :--- | :--- | :--- | :--- | :--- |
| **Aho-Corasick (AC Automaton)** | **Multi-Pattern Matching** | $O(n)$ (Linear with text length) | High | Excellent (Fastest option via C-extension libraries) |
| **KMP (Knuth-Morris-Pratt)** | **Single-Pattern Matching** | $O(m + n)$ (m = pattern, n = text length) | Low | Poor (Requires $M$ runs for $M$ patterns: $O(M \times n)$) |
| **Regular Expressions (Regex)** | Flexible/Fuzzy Matching | $O(n \times m)$ (highly variable/slow) | Low | Worst (Slowest performance for large, static keyword lists) |

---
transition: slide-up
level: 2
---

After comparing these algorithms, we can see that KMP is the best choice for our use case.
In this example, we will use KMP algorithm to find the occurance of one word in a text file.

# First, generate a large text file for testing

```python
# code of random string generator

def generate_random_string(length):
    """Generates a random string of a fixed length."""
    # Define the characters to choose from (letters + digits) and whitespace
    characters = string.ascii_letters + string.digits+ string.whitespace
    # Generate the random string
    random_string = ''.join(random.choice(characters) for i in range(length))
    return random_string

```
---
transition: slide-up
level: 2
---

# Simple pure python implementation

## the KMP algorithm description

You can refer to this [wikipedia article](https://en.wikipedia.org/wiki/Knuth–Morris–Pratt_algorithm) for more details about KMP algorithm.

## KMP Python Implementation is located 

 `code/python/kmp.py`

### how much does it cost in pure python?

90 seconds to search "3J1" in 1GB text file.

### how can we make it faster?

1. keep use python and split it into multiple processes to utilize multiple cores.
2. use Cython to compile python code into C extension.
3. use Rust to implement KMP and use pyo3 to call rust code in python

---
layoutClass: gap-16
---

# Trunking in Python

## split the text into multiple chunks and search in parallel

before we start, how to split the text into multiple chunks without breaking the pattern?

To avoid to border breaking, we can add len(pattern)-1 overlap between chunks.

If your content is `"This is block one. The TAREGT is here." and your pattern is "TAREGT" (length L=6)`.Now you want to split the text into 2 chunks. We assume the chunk size is 24 bytes.

*   Block 1: `This is block one. The T`
*   Block 2: `AREGT is here.`

When the pattern `"TAREGT"` spans across the boundary of Block 1 and Block 2, it gets split into two parts: `"T"` in Block 1 and `"AREGT"` in Block 2.

When searching for the pattern in each block separately we will lose the match:
* Thread 1 searches Block 1: does not find `"TAREGT"`.
* Thread 2 searches Block 2: does not find `"TAREGT"`.

---
layoutClass: gap-16
---

## How to solve the border breaking issue?

### Boundary Overlap

The solution to the border breaking issue is to ensure that **each chunk starts with a portion of data from the end of the previous chunk**. The size of this overlapping region should be at least **the length of the search string L minus 1** (L - 1).

$$ \text{Overlap Size} = \text{len}(\text{Search String}) - 1 $$

If we search `TAREGT` (L=6), the overlap size should be 5. Chuck size is 24 bytes.

* Chunk 1 | Start: 0 | Read Size: 29 | Found: True | Content: [This is block one. The TAREGT]
   --> MATCH SUCCESS in Chunk 1
* Chunk 2 | Start: 19 | Read Size: 19 | Found: True | Content: [The T|AREGT is here.]

---
layoutClass: gap-16
---

## Which is the correct size of each chunk?
To determine the correct size of each chunk, we need to consider the total length of the text, the number of chunks we want to create (based on the number of CPU cores), and the overlap size.

$$ \text{Chunk Size} = \frac{\text{Total Length of Text}}{\text{Number of Chunks}} + (\text{len}(\text{Search String}) - 1) $$

```python
# 1. get total length of the text
with open('random_str.txt', 'r') as f:
    FILE_CONTENT=f.read()
# 2. calculate chunk size
NUM_PROCESSES = 4 # os.cpu_count()
L = len(pattern)
OVERLAP_SIZE = len(pattern) - 1
STANDARD_CHUNK_SIZE = len(FILE_CONTENT) // NUM_PROCESSES + OVERLAP_SIZE
print(STANDARD_CHUNK_SIZE)
```

---
layoutClass: gap-16
---

https://github.com/tkizm1/py_runner is all codes about this implementation.

## The performance result comparison (without calculating loading file in memory time)

| Implementation | Time Taken (seconds) |
| :--- | :---: |
| **Pure Python KMP without trunking** | **262** |
| **Multiprocessing KMP pure python** | **25** |
| **Cython KMP single process** | **5** |
| **pyO3 KMP Multiprocessing** | **0.94** |

---
layoutClass: gap-16
---

# Use multiprocessing with memory-mapped files

Directly use multiprocessing with large files may lead to high memory consumption. To solve this, we can use memory-mapped files (mmap) to share file content across processes without loading the entire file into memory for each process.

## first, create a temporary mmap file for sharing
```python
file_content = file_content.encode('utf8')
with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tmp_file:
    tmp_file.write(file_content)
    file_path = tmp_file.name 

...
# after code execution, remember to delete the temporary file
os.remove(file_path)
```

---
layoutClass: gap-16
---

## second, use mmap to read the file in each process
```python
# --- Key Step: Map the file using mmap ---
with open(file_path, 'rb') as f:
    # mmap.mmap maps the entire file into memory, but multiple processes share the same physical memory block
    # And allows us to access the file content like accessing a sequence of bytes
    # length=0 means map the entire file
    # access=mmap.ACCESS_READ means read-only
    with mmap.mmap(f.fileno(), length=0, access=mmap.ACCESS_READ) as m:
        # m can now be used like a bytes object
        
        # Calculate the actual start of reading: start_index minus overlap_size
        actual_start = max(0, start_index - OVERLAP_SIZE) 
        
        # Determine the content of the buffer to be processed (slicing from the mmap object)
        # Note: mmap slicing returns bytes. If the search term is a str, ensure consistent encoding.
        buffer = m[actual_start : end_index].decode('utf-8')
        
        # Calculate the starting offset of the buffer in the original file
        buffer_file_start_offset = actual_start
```

---
layoutClass: gap-16
---

# Use cython to compile python code into C extension

```python

## we use long long to store the length of text to support large file (>2GB)
cdef KMPAlgorithm(const char* text, const char* pattern):
    cdef int M = strlen(pattern)
    cdef long long N = strlen(text)
    # Alocar memória para pps
    # we use malloc to allocate memory in C style
    cdef int* pps = <int*>malloc(M * sizeof(int))
```

With the help of copilot, convert the python code into cython code is quite straightforward. But type conversion between str and bytes need to be handled carefully.And memory management is also important in C code.

```python
def main(text, pattern):
    # to ensure the type coversion between str and bytes
    if isinstance(text, str):
        text = text.encode('utf-8')
    if isinstance(pattern, str):
        pattern = pattern.encode('utf-8')
```

---
layoutClass: gap-16
---

## The pro and cons of using Cython
### Pros:
- Performance Improvement: Cython can significantly speed up Python code, especially for computationally intensive tasks
- Easy Integration: Cython code can be easily integrated into existing Python projects
- Access to C Libraries: Cython allows direct access to C libraries, enabling the use of
  high-performance C functions within Python code
### Cons:
- Learning Curve: Cython introduces additional syntax and concepts that may require some learning for Python developers
- Debugging Complexity: Debugging Cython code can be more complex than pure Python code due
  to the additional layer of compilation
- Build Process: Cython code needs to be compiled, which adds a build step to the development process
- Cross Platform Issues: Compiled Cython extensions may face compatibility issues across different platforms and Python versions

---
layoutClass: gap-16
---

# Use Rust with pyo3 to speed up python code

## GIL and Multithreading with pyo3 and Rayon

### Which is GIL?
The Global Interpreter Lock (GIL) is a mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecodes at once. This lock is necessary because CPython's memory management is not thread-safe. While the GIL simplifies the implementation of CPython, it can be a bottleneck in CPU-bound and multithreaded programs, as it effectively serializes execution of threads.

### free threading python 3.14

With the release of Python 3.14, the Global Interpreter Lock (GIL) has been redesigned to improve multithreading performance. The new GIL implementation aims to reduce contention and improve the efficiency of thread switching, allowing for better utilization of multiple CPU cores in multithreaded applications. This redesign is expected to enhance the performance of CPU-bound tasks that rely on multithreading, making Python more competitive for parallel processing workloads.

https://github.com/facebookexperimental/free-threading-benchmarking

---
layoutClass: gap-16
---

### Pros and Cons of GIL

**Pros:**
- Simplicity: The GIL simplifies the implementation of the Python interpreter, making it easier
  to manage memory and object lifetimes.
- Safety: It prevents race conditions and ensures that only one thread executes Python bytecode at a time,
  which can prevent certain types of bugs.

**Cons:**
- Performance Bottleneck: In CPU-bound multithreaded programs, the GIL can become
  a significant performance bottleneck, as threads must wait for the GIL to be released before they can execute.
- Limited Multithreading: The GIL limits the effectiveness of multithreading in Python, as threads cannot run in parallel on multiple CPU cores.

---
layoutClass: gap-16
---

### How to release GIL in pyo3?
When integrating Rust with Python using pyo3, managing the Global Interpreter Lock (GIL) is crucial for performance, especially in multithreaded scenarios. The GIL is a mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecodes at once. This can lead to performance bottlenecks in CPU-bound tasks.

### Releasing the GIL for Multithreaded Rust Code
```rust
let final_matches = Python::with_gil(|py| {
    // Use py.allow_threads to release the GIL and execute Rust multithreaded code within the closure
    py.allow_threads(|| {
        // Execute tasks using the Rayon thread pool
        let all_results: Vec<Vec<usize>> = tasks.par_iter()
            .map(|&(start, end)| {
                search_chunk(
                    start, 
                    end, 
                    file_content, // &str (string slice) is safe to share across threads
                    search_term, 
                    overlap_size
                )
            })
            .collect();
            ...
    })
});
```

---
layoutClass: gap-16
---

### Aggregate the results from all threads

```rust
// code of ... in last slide
// Aggregate and sort the results
let mut final_matches: Vec<usize> = all_results.into_iter().flatten().collect();
final_matches.sort();
final_matches
```

---
layoutClass: gap-16
---

### Pros and Cons of using Rust with pyo3

**Pros:**
- Performance: Rust is a systems programming language that offers performance comparable to C and C++. Using
  Rust with pyo3 can significantly speed up performance-critical sections of Python code.
- Safety: Rust's ownership model and type system help prevent common programming errors, such as null pointer dereferences and data races.

**Cons:**
- Learning Curve: Rust has a steep learning curve, especially for developers unfamiliar with systems programming concepts.
- Build Complexity: Integrating Rust code into Python projects can add complexity to the build process, requiring additional tooling and configuration.

---
layoutClass: gap-16
---
# Compare Cython and pyo3
While Cython has long been the standard for optimizing Python, Rust (specifically combined with PyO3 and Maturin) is increasingly recommended for modern high-performance Python extensions.

1. Memory Safety (The "Killer Feature")

    Cython: Cython is essentially a superset of Python that compiles to C. If you make a mistake with pointers or memory management in Cython (especially when interacting with C arrays), you can cause segmentation faults, buffer overflows, and memory leaks. Debugging these crashes is notoriously difficult.

    Rust: Rust guarantees memory safety at compile-time through its ownership and borrow checker system. It effectively eliminates entire classes of bugs (like null pointer dereferences and data races) without needing a garbage collector. If your Rust code compiles, it is almost certainly memory-safe.

2. Superior Tooling and Package Management

    Cython: Building Cython extensions usually involves complex setup.py configurations, dependency on specific C compilers (gcc, clang, MSVC), and dealing with cryptic linker errors. Managing dependencies is manual and painful.

    Rust: Rust has Cargo, arguably the best package manager in the industry.

        Maturin (a tool for building Python wheels with Rust) integrates seamlessly with Cargo. You can often compile and install a high-performance Rust module with zero configuration, just by running maturin develop.
---
layoutClass: gap-16
---

3. You need robust parallelism (multi-threading).

  Cython: While Cython can release the GIL (Global Interpreter Lock) to achieve parallelism, you are responsible for thread safety. You must manually manage locks and synchronization, which is error-prone and hard to get right.

  Rust: Rust's type system understands threading. The compiler will refuse to compile code that introduces data races. This allows you to write highly parallel code (using libraries like Rayon) that fully utilizes multi-core CPUs with confidence that it won't crash due to race conditions.

4. You prefer modern tooling (Cargo/Maturin) over makefiles and C compilers.

Cython: Cython is a hybrid syntax—a mix of Python and C. It lacks many modern programming language features.

Rust: Rust is a fully-featured modern system language. It has powerful abstractions (traits, generics, pattern matching), a rich standard library, and a vibrant ecosystem of crates (libraries). If you enjoy writing idiomatic, expressive code, Rust is a joy to work with.

---
layoutClass: gap-16
---

# Some tools 

## uv: 
![alt text](./assets/03aa9163-1c79-4a87-a31d-7a9311ed9310.svg)
A lightning-fast CLI tool for searching and processing text files, built with Rust and PyO3.

https://docs.astral.sh/uv/

## slidev:

Slidev is a powerful tool for creating presentations using Markdown and Vue.js. It allows developers to create visually appealing slides with ease, leveraging the flexibility of web technologies.

https://github.com/slidevjs/slidev

---
layoutClass: gap-16
---

Thank you for your attention! The sharing slides and code examples can be found at:

https://github.com/tkizm1/py_runner

# Bye!