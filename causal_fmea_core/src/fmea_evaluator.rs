// 实现FMEA算法 SOD
use pyo3::prelude::*;

#[pyclass]
#[derive(Clone, Copy, Debug)]
pub struct FmeaScore {
    #[pyo3(get, set)] pub s: u32, // 让 s、o、d 这三个字段在 Python 侧可以直接读写（即 obj.s、obj.s = 1）。
    #[pyo3(get, set)] pub o: u32,
    #[pyo3(get, set)] pub d: u32,
}

#[pymethods]
impl FmeaScore {
    #[new]
    pub fn new(s: u32, o: u32, d: u32) -> Self {
        FmeaScore { s, o, d }
    }

    /// 核心任务：用 Rust 确立裁判法则
    pub fn calculate_rpn(&self) -> u32 {
        // 隐式返回法则：这行不加分号，直接将其作为 u32 结果扔给 Python
        (100 * self.s) + (10 * self.o) + self.d
    }
}