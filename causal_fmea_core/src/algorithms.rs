// 文件：src/algorithms.rs 
// 拓扑排序，检测是否为有向无环图
use crate::dag::CompactCausalGraph;   // crate（从你自己的项目/库开始找） 比如 src/dag.rs
use std::collections::{HashSet, VecDeque}; // 引入队列和集合

pub struct CausalAlgorithms;

impl CausalAlgorithms {
    /// 核心任务 1：Kahn 算法拦截逻辑死循环
    /// 返回值：如果图是健康的（无环），返回 true；如果侦测到死循环幻觉，返回 false 触发拦截！
    pub fn kahn_cycle_detect(graph: &CompactCausalGraph) -> bool {
        let n = graph.node_count;
        if n == 0 { return true; }

        // 物理动作 1：在堆内存开辟入度统计表，全部置零
        let mut in_degree = vec![0; n];
        
        // 物理动作 2：全面扫描图谱，统计每个节点的入度（被指向的次数）
        for from_node in 0..n {
            if from_node < graph.adjacency_list.len() {
                for &to_node in &graph.adjacency_list[from_node] {
                    in_degree[to_node] += 1;
                }
            }
        }

        // 物理动作 3：把刚开始的时候所有入度为 0 的“自由节点”（比如案卷的初始证据）推入处理队列  用于开启while循环
        let mut zero_in_degree_queue = Vec::new();
        for i in 0..n {
            if in_degree[i] == 0 {
                zero_in_degree_queue.push(i);
            }
        }

        // 物理动作 4：像剥洋葱一样，层层拆解因果图
        let mut processed_nodes = 0;
        while let Some(node) = zero_in_degree_queue.pop() {
            processed_nodes += 1;
            
            if node < graph.adjacency_list.len() {
                for &neighbor in &graph.adjacency_list[node] {
                    // 砍断连接的边
                    in_degree[neighbor] -= 1;
                    // 如果下家也没有依赖了，进入自由队列
                    if in_degree[neighbor] == 0 {
                        zero_in_degree_queue.push(neighbor);
                    }
                }
            }
        }

        // 终极物理审判：如果成功拆解的节点数等于总节点数，说明没有死扣；否则，绝对有环！
        processed_nodes == n
    }

// ------------------------------------------------------------
// ------------------------------------------------------------

    // 核心任务 2：贝叶斯球算法检测 d-分离
    // 注意：这条通用的路可能是合法的因果链 (Chain)，也可能是具有欺骗性的后门伪相关 (Confounder)。
    // 未来在完整系统中我们会提前把X➡️Y的合法路径先剪断掉，这样下面都是在判断非法路径能不能到终点
    // 下面分支条件记住：与之前讲的d分离算法中的阻断相反，我们要用非法方法看能不能到达终点，所以用的条件是相反的
    pub fn is_d_separated(
        graph: &CompactCausalGraph, 
        x: usize, 
        y: usize, 
        observed: &HashSet<usize>
    ) -> bool {
        let n = graph.node_count;
        if n == 0 || x == y { return false; }

        // 你的战术执行：榨干 CPU！在寄存器里动态开辟内存，临时反转图谱！  down是天生的，但是我们需要up，所以要反转得到
        let mut rev_adj = vec![Vec::new(); n];
        for u in 0..n {
            if u < graph.adjacency_list.len() {
                for &v in &graph.adjacency_list[u] {
                    rev_adj[v].push(u); // 逆向记录：v 的上游是 u
                }
            }
        }

        // 物理准备：找出所有观察节点及其孙子节点（用于对撞因子的激活判断）
        // 在对撞结构中，不仅仅是Z被观测到这条路就通，只要Z的孩子被观测到，这条路也通！所以我们需要先找到所有被观测节点的祖先，才能正确判断对撞结构是否被激活。
        // 比如对于 A -> C <- B，如果  C 的孩子为 D 被观测到了，那么ancestors_of_observed可以通过D将C存进去，这样当贝叶斯球滚到D时，就能正确判断这条路是通的！
        let mut ancestors_of_observed = HashSet::new();  // 用于存放所有观测节点及其祖先节点
        let mut q = VecDeque::new();  // 创建一个队列，用于广度优先遍历
        for &obs in observed {
            q.push_back(obs);
            ancestors_of_observed.insert(obs);
        }
        while let Some(node) = q.pop_front() {  // 拿到所有父节点是为了collider，因为collider
            for &parent in &rev_adj[node] {  // 逆着箭头往父节点走，找到所有祖先
                if ancestors_of_observed.insert(parent) { // 尝试把父节点插入
                    q.push_back(parent);
                }
            }
        }

        // ------------------------------------------------------------------------------------

        // 贝叶斯球开始滚动！状态元组：(当前节点, 运动方向)
        // 方向：true 代表往子节点滚 (Down)，false 代表往父节点滚 (Up)
        let mut queue = VecDeque::new();
        let mut visited = HashSet::new();

        queue.push_back((x, false));   // 每个分支都要有queue.push_back，因为一个点可能有多个分支，要克隆一下这个球
        visited.insert((x, false));    // 默认为false，表示从x开始往上滚，最开始可以运行所有分支
        // visited里存的状态是（节点，方向），因为同一个节点在不同方向上可能有不同的访问状态，这样就能区分开来，避免混淆。避免重复路径

        while let Some((curr, is_down)) = queue.pop_front() {
            // 未来在完整系统中我们会提前把X➡️Y的合法路径先剪断掉，这样下面都是在判断非法路径能不能到终点
            // 如果贝叶斯球成功滚到了终点，说明没有被 d-分离（存在连通的幻觉路径）
            
            // chain和confounder中Z没观测到才能往后走，因为观测到意味着路径被阻断了（不用手动放个墙拦截，不给分支（通行证）就行）；
            // 而collider中Z被观测到或者Z的孩子被观测到才能往后走，因为观测到意味着路径被激活了。
            
            //能走通道终点才有问题！！！  说明d分离没有成功，路径没被阻断，X与Y之间有非法相关性
            if curr == y { return false; }  // 找到一条边通就有问题 类似BFS，最后的时候能到Y说明路径是通的；d-separated = false，没有分离成功

            // 向上后往下 confounder  要未观测才通路
            if !is_down && !observed.contains(&curr) {
                for &child in &graph.adjacency_list[curr] {
                    if visited.insert((child, true)) { queue.push_back((child, true)); }
                }
            // 向下后往上
            } else if is_down {  // 要观测到才通路
                // 如果是 Collider（对撞），只有它或它的孙子节点被观察到时，路径才通！
                if ancestors_of_observed.contains(&curr) {   // 如果观测到Z的孩子那也算Z被观测了，路径就通了
                    for &parent in &rev_adj[curr] {
                        if visited.insert((parent, false)) { queue.push_back((parent, false)); }
                    }
                }
            }

            // 先上后向上 chain反向    要未观测才通路
            if !is_down && !observed.contains(&curr) {
                for &parent in &rev_adj[curr] {
                    if visited.insert((parent, false)) { queue.push_back((parent, false)); }
                }
            //  向下后向下         要未观测才通路
            } else if is_down && !observed.contains(&curr) {    // Chain 正向 合法路径    纯粹的X➡️Y最开始就没了，这里的chain只是为了能让路线传递下去，因为很有可能有这种情况
                for &child in &graph.adjacency_list[curr] {            // X⬅️Z➡️A➡️B➡️Y  起码要让这个线路中间跑通      没观测到才能往后走
                    if visited.insert((child, true)) { queue.push_back((child, true)); }
                }
            }
        }

        // 贝叶斯球滚遍了全图都没碰到 y，说明路径被成功物理切断！(d-separated = true)
        true
    }

}