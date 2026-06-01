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
        self.is_active = false; // 表示"死神"已执行清理动作

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

    /// 任务 1：注册节点（已废弃，请使用 inject_edges）
    #[deprecated(note = "请使用 inject_edges 替代，该方法会同时更新 interner 和 graph")]
    pub fn register_node(&mut self, node_name: String) -> PyResult<usize> {
        let mut pool = self.interner.lock().unwrap_or_else(|e| e.into_inner());
        let id = pool.insert_full(node_name).0;
        drop(pool);  // 释放锁后再操作 graph
        self.graph.ensure_capacity(id);
        Ok(id)
    }

    /// 任务 2：反向查询
    pub fn get_node_name(&self, node_id: usize) -> PyResult<Option<String>> {
        let pool = self.interner.lock().unwrap_or_else(|e| e.into_inner());

        // 获取引用，并克隆一份 String 扔回给 Python 把内部数据"拷贝"出来，安全返回给 Python
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
        let mut pool = self.interner.lock().unwrap_or_else(|e| e.into_inner());

        for (source, target) in py_edges {
            let (src_id, _) = pool.insert_full(source);
            let (tgt_id, _) = pool.insert_full(target);

            // 物理拦截：跳过自环边（source == target），自环在因果图中无意义且会导致 Kahn 算法误判
            if src_id == tgt_id {
                continue;
            }

            self.graph.add_edge(src_id, tgt_id);
        }

        Ok(())
    }


    /// 战术核心：跨界破绽提取器！自动寻找 Z 节点，验证 d-分离，并翻译成常识断言
    pub fn extract_testable_claims(&self) -> PyResult<Vec<String>> {
        const MAX_TOTAL_CLAIMS: usize = 20;
        let mut claims = Vec::new();
        let pool = self.interner.lock().unwrap_or_else(|e| e.into_inner());
        let n = self.graph.node_count;

        // 1. 遍历所有可能的 (X, Y) 节点对
        for i in 0..n {
            if claims.len() >= MAX_TOTAL_CLAIMS { break; }
            for j in (i + 1)..n {
                if claims.len() >= MAX_TOTAL_CLAIMS { break; }
                // 如果 X 和 Y 有直接连线，绝对不可能独立，跳过
                let has_direct = self.graph.adjacency_list[i].contains(&j) ||
                                 self.graph.adjacency_list[j].contains(&i);
                if has_direct { continue; }

                let name_i = pool.get_index(i).unwrap();
                let name_j = pool.get_index(j).unwrap();

                // 测试 1：无条件独立性（适用于 Collider 对撞结构 X→Z←Y）
                let empty_observed = std::collections::HashSet::new();
                let unconditionally_independent = CausalAlgorithms::is_d_separated(
                    &self.graph, i, j, &empty_observed
                );

                if unconditionally_independent {
                    let claim = format!(
                        "图结构推断: 在不引入额外条件时, [{}]与[{}]之间不存在活跃的因果路径. 这两个事件在现实中是否确实互不影响?",
                        name_i, name_j
                    );
                    claims.push(claim);
                }

                // 测试 2：遍历所有可能的阀门节点 Z
                for k in 0..n {
                    if claims.len() >= MAX_TOTAL_CLAIMS { break; }
                    if k == i || k == j { continue; }

                    let name_k = pool.get_index(k).unwrap();
                    let mut observed = std::collections::HashSet::new();
                    observed.insert(k);
                    let conditionally_independent = CausalAlgorithms::is_d_separated(
                        &self.graph, i, j, &observed
                    );

                    if conditionally_independent && !unconditionally_independent {
                        // Confounder 结构：Z 是阻断阀门，观测 Z 后 X 与 Y 独立
                        let claim = format!(
                            "图结构推断: 若将[{}]固定为常量, 则[{}]的变化不会经由图中的因果路径传导至[{}]. 这个统计推断在现实中成立吗?",
                            name_k, name_i, name_j
                        );
                        claims.push(claim);
                    } else if !conditionally_independent && unconditionally_independent {
                        // Collider 结构：Z 是对撞因子，观测 Z 后 X 与 Y 变得相关
                        let claim = format!(
                            "图结构推断: [{}]与[{}]在无条件下互不影响, 但若观测到[{}], 则二者之间会出现活跃的因果路径. 这个对撞因子激活现象在现实中是否成立?",
                            name_i, name_j, name_k
                        );
                        claims.push(claim);
                    }
                }
            }
        }
        Ok(claims)
    }

}

#[pymodule]  // 声明为 Python 模块初始化函数
fn causal_fmea_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<FmeaScore>()?;
    m.add_class::<CausalParadigmEngine>()?;

    Ok(())
}