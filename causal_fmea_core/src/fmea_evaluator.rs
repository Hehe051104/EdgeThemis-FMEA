// 实现FMEA算法 SOD
use pyo3::prelude::*;

#[pyclass]
#[derive(Clone, Copy, Debug)]
pub struct FmeaScore {
    #[pyo3(get, set)] pub s: u32,
    #[pyo3(get, set)] pub o: u32,
    #[pyo3(get, set)] pub d: u32,
}

#[pymethods]
impl FmeaScore {
    #[new]
    pub fn new(s: u32, o: u32, d: u32) -> PyResult<Self> {
        if s < 1 || s > 10 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                format!("严重度 S 必须在 1-10 之间，收到: {}", s)
            ));
        }
        if o < 1 || o > 10 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                format!("频度 O 必须在 1-10 之间，收到: {}", o)
            ));
        }
        if d < 1 || d > 10 {
            return Err(pyo3::exceptions::PyValueError::new_err(
                format!("探测度 D 必须在 1-10 之间，收到: {}", d)
            ));
        }
        Ok(FmeaScore { s, o, d })
    }

    /// 核心任务：用 Rust 确立裁判法则
    pub fn calculate_rpn(&self) -> u32 {
        (100 * self.s) + (10 * self.o) + self.d
    }
}