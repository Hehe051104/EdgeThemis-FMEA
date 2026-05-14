use pyo3::prelude::*;
use indexmap::IndexSet;
use std::sync::{Arc, Mutex};   // Arc（原子引用计数指针）和 Mutex（互斥锁）

#[pyclass]
pub struct CausalParadigmEngine {   // 声明 Rust 结构体可以暴露给 Python 使用
    interner: Arc<Mutex<IndexSet<String>>>,  // 类型为 Arc<Mutex<IndexSet<String>>>，即线程安全、可共享的字符串集合
}

#[pymethods]  // 声明这是实现的方法
impl CausalParadigmEngine {     // 实现 CausalParadigmEngine 的方法，并暴露给 Python
    #[new]  // 指定为 Python 构造函数
    pub fn new() -> Self {  // 返回一个新的 CausalParadigmEngine 实例 就像Py中的 __init__ 方法一样
        println!("⚡ [CausalForge] 正在初始化 EdgeThemis 引擎...");
        println!("⚡ [CausalForge] 正在开辟底层字符串驻留池...");
        CausalParadigmEngine {
            interner: Arc::new(Mutex::new(IndexSet::new())),  // 初始化为一个空的 IndexSet，并用 Arc 和 Mutex 包裹，保证线程安全和可共享
        }
    }

    /// 任务 1：注册节点
    pub fn register_node(&self, node_name: String) -> PyResult<usize> {
        // 你的逻辑 1：极其粗暴地拿锁，并声明为可变 (mut)
        let mut pool = self.interner.lock().unwrap();
        
        // 你的逻辑 2：插入数据，并用 .0 提取第一个元素 (ID)  insert_full 返回 (index, bool),取下标
        let id = pool.insert_full(node_name).0;
        
        Ok(id)
    }

    /// 任务 2：反向查询
    pub fn get_node_name(&self, node_id: usize) -> PyResult<Option<String>> {
        // 拿锁（只读，所以不需要 mut）
        let pool = self.interner.lock().unwrap();
        
        // 获取引用，并克隆一份 String 扔回给 Python 把内部数据“拷贝”出来，安全返回给 Python
        Ok(pool.get_index(node_id).cloned())
    }
}

#[pymodule]  // 声明为 Python 模块初始化函数
fn causal_fmea_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<CausalParadigmEngine>()?;
    Ok(())
}