use pyo3::prelude::*;
use indexmap::IndexSet;
use std::sync::{Arc, Mutex};   // Arc（原子引用计数指针）和 Mutex（互斥锁）

// 物理连线：告诉 Rust 编译器去加载那个新文件
pub mod fmea_evaluator; 
// 提取武器：把 FmeaScore 拉到当前作用域
use fmea_evaluator::FmeaScore;

pub mod dag;  // 加载我们定义的图结构模块
use dag::CompactCausalGraph;  // 把 CompactCausalGraph 拉到当前作用域

pub mod algorithms;  // 加载算法模块
use algorithms::CausalAlgorithms;  // 把 CausalAlgorithms 拉到当前作用域


// 变量销毁，内存回收😋
// ==========================================
struct LlamaMemoryReaper {
    is_active: bool,
}

// 当 Rust 检测到没有任何变量再持有 LlamaMemoryReaper 时，也就是Arc=0时会自动调用 drop 方法
impl Drop for LlamaMemoryReaper {
    fn drop(&mut self) {
        // 死神苏醒时的动作
        println!("🔥 [Rust 死神机制] 侦测到 Python 宿主抛弃了引擎！");
        println!("🔥 [Rust 死神机制] 正在跨界挥下镰刀，清除 4060 底层物理内存...");
        self.is_active = false; // 表示“死神”已执行清理动作

        // 注意：没有任何 unsafe 代码。
        // Rust 的编译器会自动在这里插入代码，把 interner 和 graph 彻底销毁！


        // 在这里，你可以调用 unsafe { llama_free(...) } 来强行释放 C++ 分配的显存
        // 真正的杀招（伪代码）：
        // unsafe {
        //     llama_free_model(self.model_ptr);
        //     llama_free(self.ctx_ptr);
        // }
    }
}


// ----------------------------------------------------------------------------------------
// ----------------------------------------------------------------------------------------

// 实现将输入的字符串注册到驻留池，并返回一个唯一的 ID，后续可以通过这个 ID 来查询原始字符串

#[pyclass]
pub struct CausalParadigmEngine {   // 声明 Rust 结构体可以暴露给 Python 使用  ARC:引用计数
    interner: Arc<Mutex<IndexSet<String>>>,  // 字符串驻留池，Arc 和 Mutex 包裹保证线程安全和可共享
    _reaper: Arc<LlamaMemoryReaper>,  // 挂载死神, 只要引擎实例活着，死神就沉睡；一旦实例被销毁，死神就苏醒，执行内存清理
    graph: CompactCausalGraph,  // 因果图结构，存储节点和边的信息
}

#[pymethods]  // 声明这是实现的方法
impl CausalParadigmEngine {     // 实现 CausalParadigmEngine 的方法，并暴露给 Python
    #[new]  // 指定为 Python 构造函数
    pub fn new() -> Self {  // 返回一个新的 CausalParadigmEngine 实例 就像Py中的 __init__ 方法一样
        println!("⚡ [CausalForge] 正在初始化 EdgeThemis 引擎...");
        println!("⚡ [CausalForge] 正在开辟底层字符串驻留池...");
        CausalParadigmEngine {
            interner: Arc::new(Mutex::new(IndexSet::new())),  // 初始化为一个空的 IndexSet，并用 Arc 和 Mutex 包裹，保证线程安全和可共享
            // 实例化这颗死神炸弹
            _reaper: Arc::new(LlamaMemoryReaper { is_active: true }),
            graph: CompactCausalGraph::new(100),  // 初始化一个容量为 100 的空图
        }
    }

    /// 任务 1：注册节点    光荣退役，由inject_edges接管
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


    /// 检查图是否为有向无环图
    pub fn check_graph_health(&self) -> PyResult<bool> {
        let is_healthy = CausalAlgorithms::kahn_cycle_detect(&self.graph);
        if !is_healthy {
            println!("[Rust 物理拦截] 侦测到大模型发生逻辑死循环幻觉！");
        }
        Ok(is_healthy)
    }


    /// 跨界物理注射器：接收 Python 传来的 [(String, String)] 列表
    pub fn inject_edges(&mut self, py_edges: Vec<(String, String)>) -> PyResult<()> {
        // 物理动作 1：获取驻留池的互斥锁
        let mut pool = self.interner.lock().unwrap();
        
        for (source, target) in py_edges {
            // 物理动作 2：极其暴力的字符串没收！
            // insert_full 会检查池子里有没有这个词。没有就塞进去，有就直接返回它的唯一 ID！
            let (src_id, _) = pool.insert_full(source);
            let (tgt_id, _) = pool.insert_full(target);
            
            // 物理动作 3：把纯数字 ID 压入我们的一维数组图谱中！
            self.graph.add_edge(src_id, tgt_id);
        }
        
        Ok(())
    }



}

#[pymodule]  // 声明为 Python 模块初始化函数
fn causal_fmea_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<FmeaScore>()?;
    m.add_class::<CausalParadigmEngine>()?;

    Ok(())
}