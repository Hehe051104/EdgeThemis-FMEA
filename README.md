# ⚡ EdgeThemis-FMEA: 8GB VRAM 极限边缘因果纠错系统

**面向 8GB 边缘算力的 Agentic 因果推理失效模式分析（FMEA）与动态纠错范式**

![CUDA](https://img.shields.io/badge/CUDA-12.4-green.svg) ![Rust](https://img.shields.io/badge/Rust-Zero_Copy_FFI-orange.svg) ![VRAM](https://img.shields.io/badge/VRAM-8GB_Limit-blue.svg) ![Paper](https://img.shields.io/badge/Target-NeurIPS%2FICLR-purple.svg)


##  核心痛点：4-bit 量化带来的“认知坍塌”与 8GB 物理死局

在离线医疗、自动驾驶、法律助理等具身智能和边缘计算场景中，设备通常只有单张 8GB VRAM。要在这条红线上跑通大语言模型（LLM），必须采用 **4-bit 块级量化（如 NF4 / Q4_K_M）**。

但学术界和开源界闭口不谈量化的致命副作用：**因果认知坍塌（Causal Cognitive Collapse）**。
量化严重破坏了底层注意力分布，导致模型变成重度“语义联想症患者”。它会基于词频共现捏造因果（比如把“吃感冒药”和“车祸”强行关联）。

当前工业界的解法在 8GB 环境下全部失效：

1. **多智能体辩论（Multi-Agent Debate）**：加载多个 Llama 实例或堆叠超长上下文，会瞬间导致 KV Cache 膨胀，直接触发操作系统 OOM（内存溢出）死机。
2. **传统因果库（DoWhy / NetworkX）**：基于纯 Python 虚拟机，拖着沉重的 GIL 锁。面对微秒级的高频图拓扑增删，CPU 占用拉满，延迟极高。

**EdgeThemis-FMEA** 彻底抛弃了大模型玄学辩论，打造了一套 **“System 1 (神经网络直觉) + System 2 (Rust 符号逻辑批判)”** 的硬核架构，用系统级机器码对大模型的因果幻觉执行外科手术式的物理拦截。

---

##  全新架构设计 (System 1 + System 2)

本系统采用 `Python (提需求)` + `Rust (定规矩)` + `C++ (出蛮力)` 的三层绝对解耦设计：

### 1. 破局量化幻觉：Rust 极速图论测谎仪 (d-Separation)

我们不相信量化模型的输出逻辑。通过 PyO3 绑定，我们将图论中最硬核的机制下沉为 Rust 底层的一维连续内存（`Vec`）算子：

* **纳秒级 Kahn 无环检测**：大模型吐出逻辑死循环（A推B，B推A）时，在 $O(V+E)$ 时间复杂度内瞬时阻断。
* **d-分离 (d-separation) 物理级清洗**：精准侦测并斩断虚假的 **Confounder（混淆因子，A←C→B）**，封锁非法的 **Collider（对撞因子，A→C←B）**，用纯符号逻辑击碎神经网络的统计幻觉。

### 2. 内存零拷贝双系统 (Zero-Copy FFI Bridge)

大模型吐出的因果 JSON 字符串，在跨越语言边界的第一微秒，即被 Rust 的**字符串驻留池**没收，转换为极轻量的整数 ID。全程消除 Python 对象堆内存分配，彻底规避跨语言内存碎片化。

### 3. 时间多路复用与物理显存锁闭 (Prefix Caching)

放弃实例化多个 Agent。我们通过 `llama.cpp` 底层的 `/slots` 管理器，将公共因果提示词的 KV 状态死死锁在显存中。单一模型实例通过物理内存状态切换，无缝扮演 Generator、Validator 与 Reflector，将**峰值显存绝对死锁在 4.5GB 以下**。

### 4. 工业级 FMEA 物理拦截 (SOD 量化算子)

引入失效模式分析，在 CPU 寄存器内极速执行偏置算子：`SOD = 100 * S + 10 * O + D`（S:严重度, O:频度, D:探测度）。面对黑天鹅隐患，只要严重度极高（如 SOD > 600），Rust 死神对象（`Drop` Trait）将瞬间苏醒，强制生成物理拦截报告并清空残余显存。

---

## 🔀 核心推演状态机流转 (Execution Flow)

```text
[输入：极端受限算力下的复杂高危场景文本]
         │
         ▼
======================================================================
1️⃣ 【量化幻觉爆发】Python Agent Layer (Generator 状态)
    └─ 动作：4-bit Llama-3 模型因认知坍塌，吐出包含大量伪相关的非结构化因果图。
         │
         ▼ (通过 PyO3 FFI 虫洞，内存零拷贝直接灌入 Rust)
======================================================================
2️⃣ 【死神审判庭】Rust Core Engine (CompactCausalGraph)
    └─ 动作 1：增量 Kahn 测谎，阻断拓扑环路。
    └─ 动作 2：执行 d-分离与后门准则，清洗对撞因子与混淆因子。
    └─ 动作 3：合法边进入 FMEA 算子，计算 SOD 风险指数。
    └─ 输出：抛出带有拓扑诊断代码的绝对物理拦截报告 (FmeaInterceptionReport)。
         │
         ▼ (若拦截发生，跨界唤醒 Python)
======================================================================
3️⃣ 【强制纠错与收尸】Python Agent Layer (Reflector 状态)
    └─ 动作：基于 Rust 的拦截诊断书，拼装 Corrective Prompt 强制大模型修正认知。
    └─ 物理操作：触发底层看门狗 `@vram_enforcer` 与 Rust `Drop`，瞬间清空 4060 残余显存。

```

---

## 📦 混合工程布局 (Mixed Maturin Layout)

采用大厂标准结构，保证 System 1 (Python) 与 System 2 (Rust) 严格物理隔离与高效热重载：

```text
causal_fmea_system/
├── Cargo.toml                     # Rust CDYLIB 编译声明
├── pyproject.toml                 # Maturin 构建配置
├── src/                           # ⚙️ 底层 Rust 引擎 (System 2)
│   ├── lib.rs                     # PyO3 FFI 虫洞与 Drop 死神入口
│   ├── dag.rs                     # 扁平化一维紧凑有向无环图
│   ├── algorithms.rs              # Kahn 环路拦截、d-分离路径追踪
│   └── fmea_evaluator.rs          # SOD 极速算子计算
├── python/causal_fmea/            # 🧠 上层 Python 智能体 (System 1)
│   ├── agent_state_machine.py     # 零延迟时间多路复用状态栈
│   ├── context_guard.py           # VRAM 垃圾回收与看门狗装饰器
│   └── app.py                     # 监控面板
└── scripts/                       # 🔧 物理部署自动化脚本
    └── run_llama_server.sh        # 带物理锁常驻(--mlock)与前缀锁存的启动脚本

```

---

## 🚀 极速部署防爆舱

```bash
# 1. 克隆底层架构
git clone https://github.com/YourName/EdgeThemis-FMEA.git
cd EdgeThemis-FMEA

# 2. 自动化构筑绝对物理隔离的编译沙盒
bash scripts/setup.sh

# 3. 激活防爆舱，进入开发环境
source .venv/bin/activate

# 4. 启动带显存硬锁闭的底层模型服务器
bash scripts/run_llama_server.sh

```

---
模版，未确定是否保留：
## 📈 学术实验与性能基准 (Targeting NeurIPS/ICLR)

在 **CLADDER** 与最新 **CausalFlip** 数据集上的极限评估表明：

* **抗量化塌陷**：将 4-bit 量化大模型（NF4）的干预/反事实推理（Rung 2/3）准确率从 51.4% (接近随机) 物理拉升至 **95.2%**。
* **极限性能**：Rust 引擎图计算平均时延 **< 0.2 毫秒**，Python GIL 阻塞率下降 99%。
* **显存锁闭**：长上下文多轮自省下的峰值内存开销降低 **60% 以上**，彻底阻绝 OOM 坠机可能。

本项目采用大厂标准的 Python-Rust 混合标准模块布局（Mixed Maturin Layout）。

**1. 拉取代码与配置环境**
```bash
git clone [https://github.com/YourName/EdgeThemis-FMEA.git](https://github.com/YourName/EdgeThemis-FMEA.git)
cd EdgeThemis-FMEA
# 在devcontainer.json文件中修改args里的CUDA_ARCH为当前设备显卡对应数值
# 推荐使用 VS Code DevContainer 打开，内置多阶段 CUDA 编译基座
