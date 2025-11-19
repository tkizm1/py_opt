use pyo3::prelude::*;
use rayon::prelude::*;
use std::cmp::max;

// --- 搜索逻辑 (与之前相同) ---

/// 在文件的一个子范围 (带有前置重叠) 中执行搜索，并返回相对于原始文件的
/// 匹配偏移量 (字节索引)。
fn search_chunk(
    start_index: usize, 
    end_index: usize,   
    file_content: &str,
    search_term: &str,
    overlap_size: usize,
) -> Vec<usize> {
    // ... (保持与之前相同的 search_chunk 函数体)
    let actual_start = start_index.saturating_sub(overlap_size);
    let buffer = &file_content[actual_start..end_index];
    let buffer_file_start_offset = actual_start;

    let mut matches = Vec::new();
    for (match_index_in_buffer, _) in buffer.match_indices(search_term) {
        let file_match_offset = buffer_file_start_offset + match_index_in_buffer;
        if file_match_offset >= start_index {
            matches.push(file_match_offset);
        }
    }
    matches
}

// --- PyO3 接口函数 ---

/// Python 调用的主函数，它使用 Rayon 进行并行处理。
/// PyO3 会自动将 Python 字符串 (str) 转换为 Rust 字符串切片 (&str)。
#[pyfunction]
fn run_parallel_search_rs(
    file_content: &str, 
    search_term: &str, 
    num_processes: usize,
) -> PyResult<Vec<usize>> {
    
    let file_size = file_content.len();
    let l = search_term.len();
    let overlap_size = max(0, l.saturating_sub(1));
    
    // 1. 确定每个进程的理想块大小 (使用整数除法来计算 ceiling)
    let chunk_size = (file_size + num_processes - 1) / num_processes;
    
    let mut tasks = Vec::new();
    
    // 2. 划分任务范围并生成任务参数 (主区域 start, end)
    for i in 0..num_processes {
        let start = i * chunk_size;
        let end = (start + chunk_size).min(file_size);
        
        if start >= file_size {
            break;
        }
        tasks.push((start, end));
    }
    
    // 3. 关键步骤：释放 GIL
    // 在进入 Rayon 并行计算之前，我们让出 Python GIL。
    // 这允许其他 Python 线程在 Rust 线程进行计算时运行。
    // we can use attach and detach to manage GIL in newer version
    let final_matches = Python::attach(|py| {
        py.detach(|| {
            // 使用 Rayon 进程池执行任务
            let all_results: Vec<Vec<usize>> = tasks.par_iter()
                .map(|&(start, end)| {
                    search_chunk(
                        start, 
                        end, 
                        file_content, // &str 是可安全地在线程间共享的
                        search_term, 
                        overlap_size
                    )
                })
                .collect();

            // 汇总和排序结果
            let mut final_matches: Vec<usize> = all_results.into_iter().flatten().collect();
            final_matches.sort();
            final_matches
        })
    });
    
    Ok(final_matches)
}

// --- PyO3 模块定义 ---

#[pymodule]
fn str_compare(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // m.add_function(wrap_pyfunction!(sum_as_string, m)?)?;
    m.add_function(wrap_pyfunction!(run_parallel_search_rs, m)?)?;
    Ok(())
}