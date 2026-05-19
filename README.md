# EdgeThemis: A Deterministic Causal Inference Engine for Edge LLMs

![CUDA](https://img.shields.io/badge/CUDA-12.4-green.svg) ![Rust](https://img.shields.io/badge/rustc-1.95.0-orange.svg) ![FFI](https://img.shields.io/badge/PyO3-Zero__Copy__FFI-yellow.svg) ![VRAM](https://img.shields.io/badge/VRAM-8GB_Limit-blue.svg) ![Paper](https://img.shields.io/badge/Target-NeurIPS%2FICLR-purple.svg)

**EdgeThemis (因果失效模式与影响分析系统)** 是一个专为受限边缘硬件设计的混合架构因果推理引擎。它旨在解决大语言模型（LLM）在复杂因果拓扑图提取中普遍存在的“拓扑幻觉”问题。

本系统通过将**形式化数学验证（Rust）**无缝嵌入**大模型推理循环（Python 状态机）**，并剥离**底层张量计算（C++）**，实现了一个能够在 8GB VRAM (如 RTX 4060) 物理环境下稳定运行的工业级防爆架构。适用于自动驾驶 ROS 级联失效分析、复杂软件架构崩溃溯源等高危场景。

---

## 🗂️ 拓扑与文件分级

系统采用极端物理隔离的异构设计，工作区物理切割如下：

```text
Causal_FMEA/
├── qwen2.5.gguf                        # 量化模型权重 (~4GB, Q8_0)，纯算力燃料
├── .devcontainer/                      # 基础设施层
│   ├── Dockerfile                      # CUDA 12.4 + llama.cpp + Rust + maturin 全栈构建环境
│   └── devcontainer.json               # GPU 直通配置，含生命周期自动编译钩子
│
└── causal_fmea_core/                   # 核心子系统（Rust/Python 混合 crate）
    ├── Cargo.toml / pyproject.toml     # 跨语言构建约束
    ├── scripts/
    │   └── run_llama_server.sh         # C++ 张量推理层独立点火脚本（微服务化核心）
    │
    ├── src/                            # Rust 底层算力层 (The Judge)
    │   ├── lib.rs                      # FFI 门面：暴露引擎与内存防爆控制
    │   ├── dag.rs                      # 紧凑邻接表：因果图的物理容器
    │   ├── algorithms.rs               # 算法心脏：Kahn 环检测 + O(N³) 贝叶斯球 d-分离
    │   └── fmea_evaluator.rs           # 边缘 RPN 风险评分引擎
    │
    └── python/causal_fmea/             # Python 高层编排层 (The Orchestrator)
        ├── app.py                      # 运行时入口：LangGraph 状态机组装与条件路由
        ├── nodes.py                    # 业务车间：Generator、Validator、Reflector 及 HTTP 雷达
        ├── agent_state_machine.py      # Pydantic 强类型约束与状态流转数据包
        └── context_guard.py            # Rust 引擎生命周期沙盒（跨语言显存回收）

```

---

## 🎯 核心痛点与解决思路

在传统因果推断管线中，直接要求 LLM 生成因果图往往面临灾难性后果：大模型极易凭空捏造死循环环路、忽视隐藏的混淆因子（Confounders），或将时间先后误判为伪独立关系。

**EdgeThemis 的破局之道：注入图论与贝叶斯数学枷锁。**
我们不奢求小参数量化模型具备完美的逻辑闭环能力。当 LLM 输出因果图后，系统强制将其送入 Rust 引擎，在内存中执行严格的形式化数学验证。我们将这套“测谎”机制抽象为三大数学定理的强制执行：

**1. 有向无环图 (DAG) 的拓扑绝对约束**
系统首先剥夺 LLM 产生死循环的权力。对于生成的因果图 $G=(V,E)$，底层 Kahn 算法强制要求拓扑图必须满足：


$$\forall v_i \in V, \nexists \text{ path } v_i \rightarrow \dots \rightarrow v_i$$


一旦检测到有向环，物理防爆门瞬间落下，强行打回重做。

**2. d-分离 (d-separation) 与条件独立性反演**
对于无环的合法 DAG，系统利用 $O(|V|^3)$ 的贝叶斯球（Bayes Ball）算法，全量遍历提取图中的条件独立性断言。如果节点 $Z$ 阻断了 $X$ 和 $Y$ 之间的所有路径，系统提取出严谨的数学供词：


$$X \perp\!\!\!\perp Y \mid Z$$


这条冰冷的数学公式随即被翻译为人类自然语言，作为反向 Prompt 注入 LLM 的“常识审判庭”。如果该断言在现实物理世界中荒谬至极，系统便利用“反证法”撕毁 LLM 伪造的因果图。

**3. 边缘自适应风险评估 (FMEA RPN)**
在确认图谱结构符合地球物理常识后，系统跨越了传统 FMEA (失效模式与影响分析) 的连乘限制，采用自定义的指数级加权公式，以适应边缘软件系统的敏锐度：


$$RPN=100 \cdot S+10 \cdot O+D$$


通过拉大严重度 ($S$) 的方差，确保高危失效节点在边缘设备的日志监控中无处遁形。

本质上，EdgeThemis 是将**形式化验证的确定性**与 **LLM 的生成式直觉** 在数学层面上完成了一次暴力的物理缝合。

---

## 🔄 运行时动态交火机制 (The Loop)

当复杂案卷输入系统时，跨越三重异构边界的推演流程如下：

1. **创世提取 (Python -> C++):** 状态机将案卷封装为 HTTP JSON Payload 打向本地 `llama-server`。强制 LLM 按结构化 CoT 输出带节点与 FMEA 评分的图谱。
2. **物理熔断 (Python -> Rust):** 边列表通过 FFI `inject_edges` 零拷贝抛入 Rust 沙盒。执行 Kahn 算法，若检测到逻辑死循环，当场熔断并踢回重写。
3. **常识测谎仪 (Rust):** 若拓扑无环，执行 $O(N^3)$ 复杂度的 d-分离，全量扫描提取反直觉的“物理条件独立性断言”。
4. **终极审判 (Python -> C++):** 提取的断言被发回 LLM (`Reflector` 节点)。若 LLM 自身的常识网络拒绝了该数学结构，判决 `REJECT`，触发纠错循环；若通过，则安全结案。

---

## 🚀 快速部署 (Quick Start)

为保证底层 C++ 与 Rust 编译环境的纯净，本项目强制要求在 VS Code Devcontainers 下运行。

需要在Linux环境下，选择使用虚拟机或WSL2

### 1. 容器部署

* 在 VS Code 中打开项目根目录，点击 `Reopen in Container`。
* 需要手动完成跨语言动态链接库的注入，在项目根目录终端中执行

```bash
maturin develop --release

```

### 2. 启动纯 C++ 推理服务 (Terminal 1)

切勿将高强度张量计算与业务逻辑混同。打开终端 1 启动微服务：

```bash
source ~/.venv/bin/activate
cd causal_fmea_core/scripts
./run_llama_server.sh

```

等待出现 `HTTP server listening on 127.0.0.1:8080`，确保 GPU 内存挂载完成。

### 3. 执行推演管线 (Terminal 2)

打开独立终端 2，发射推演指令：

```bash
source ~/.venv/bin/activate
cd causal_fmea_core/python/causal_fmea
python app.py

```

---

## 🔬 已知局限性与未来探索方向

作为探索边缘算力极限的研究系统，EdgeThemis 在极值压榨下面临以下物理断层，系后续研究重点：

1. **$O(V^3)$ 算法的并发阻塞:** d-分离断言提取采用全量 $(X, Y | Z)$ 遍历。当节点数 $N > 50$ 时，Rust 底层 Mutex 锁持有时间呈指数级飙升，可能阻塞 Python 宿主的并发请求。
2. **大模型注意力坍塌:** 在多轮重试与超长上下文中，边缘量化模型（如 8B 4-bit）容易出现 JSON 语法截断；在 FMEA 风险打分时，暴露出严重的“方差坍塌”顽疾（倾向全局打中庸分数以节省算力）。
3. **硬编码僵化:** Rust 底层 FMEA 公式当前硬编码为 `100S + 10O + D`，未来将重构为跨语言动态注入的自适应权重分配器。

---

## 📚 学术支撑与理论溯源 (Academic References)

本系统的底层逻辑闭环与防爆架构，构建于以下两篇前沿顶会论文的理论基础之上，并对其进行了 边缘设备 适应性改造与工业级复现：

1. **痛点定义与问题定位：**
* **文献：** *Can Large Language Models Infer Causation from Correlation?* (Microsoft Research, 2023)
* **架构映射：** 该论文揭示了“大模型极易将相关性误判为因果性，并在复杂网络中产生拓扑幻觉”的致命缺陷。EdgeThemis 将此痛点作为系统开发的核心矛盾，彻底抛弃了单靠 Prompt 约束 LLM 画图的幻想。


2. **核心反思机制与解决方案：**
* **文献：** *Reflexion: Language Agents with Verbal Reinforcement Learning* (NeurIPS 2023)
* **架构映射：** 论文提出了“Actor 动作 -> Evaluator 评估 -> Reflection 反思”的语言强化学习闭环。EdgeThemis 对此架构进行了硬核升级：我们用 $O(N^3)$ 复杂度的 Rust 图论测谎仪取代了传统的软性 Evaluator，用 LangGraph 状态机实现了无情而精准的反思循环（Self-Reflection），利用底层系统语言（Rust）运行时的绝对规则生成prompt，对大模型进行冷酷的常识反问

3. **其余相关论文**
*    **评测基准**：CausalFlip: A Benchmark for LLM Causal Judgment Beyond Semantic Matching (arXiv: 2602.20094)

 *   **方法论假想敌 1**：CRAwDAD: Causal Reasoning Augmentation with Dual-Agent Debate (arXiv: 2511.22854)    “双 Agent 辩论”

  *  **架构层假想敌 2**：Causal Agent based on Large Language Model (arXiv: 2408.06849)  让LLM 去调用外部的 Python 因果库来处理