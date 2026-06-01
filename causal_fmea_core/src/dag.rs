// 文件：src/dag.rs

#[derive(Debug, Clone)]
pub struct CompactCausalGraph {
    // 邻接表：索引代表起点 node_id，里面的 Vec 存下游节点的 node_id
    pub adjacency_list: Vec<Vec<usize>>,
    // 反向邻接表：索引代表终点 node_id，里面的 Vec 存上游节点的 node_id
    pub rev_adjacency_list: Vec<Vec<usize>>,
    // 记录目前图里有多少个节点
    pub node_count: usize,
}

impl CompactCausalGraph {
    /// 创世指令：初始化一个空图
    pub fn new(initial_capacity: usize) -> Self {
        CompactCausalGraph {
            adjacency_list: vec![Vec::new(); initial_capacity],
            rev_adjacency_list: vec![Vec::new(); initial_capacity],
            node_count: 0,
        }
    }

    /// 物理动作：动态扩容。如果大模型吐出了未知的 ID，强行把数组撑大
    pub fn ensure_capacity(&mut self, max_id: usize) {
        if max_id >= self.adjacency_list.len() {
            self.adjacency_list.resize(max_id + 1, Vec::new());
            self.rev_adjacency_list.resize(max_id + 1, Vec::new());
        }
        if max_id >= self.node_count {
            self.node_count = max_id + 1;
        }
    }

    /// 物理动作：插入一条因果边
    pub fn add_edge(&mut self, from_id: usize, to_id: usize) {
        self.ensure_capacity(from_id.max(to_id));

        // 只有当这条边不存在时，才插进去（防止大模型重复吐出同一条边）
        if !self.adjacency_list[from_id].contains(&to_id) {
            self.adjacency_list[from_id].push(to_id);
            self.rev_adjacency_list[to_id].push(from_id);
        }
    }

    /// 获取反向邻接表的引用（无需重建，O(1) 返回）
    pub fn rev_adj(&self) -> &Vec<Vec<usize>> {
        &self.rev_adjacency_list
    }
}