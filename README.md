# ⚡ EdgeThemis-FMEA: 8GB VRAM 极限边缘因果纠错系统


![CUDA](https://img.shields.io/badge/CUDA-12.4-green.svg) ![Rust](https://img.shields.io/badge/Rust-Zero_Copy_FFI-orange.svg) ![VRAM](https://img.shields.io/badge/VRAM-8GB_Limit-blue.svg) ![Paper](https://img.shields.io/badge/Target-NeurIPS%2FICLR-purple.svg)

**面向 8GB 边缘算力的 Agentic 因果推理失效模式分析（FMEA）与动态纠错范式**

本项目是一个专为显存受限环境（如 RTX 4060 8GB）设计的工业级因果推理引擎。核心架构采用 **Python (LangGraph) + Rust (PyO3)** 混合开发。

设计思路很明确：用大模型（LLM）做逻辑推演，但绝不信任其输出。通过强类型约束（Pydantic/JSON Schema）限制生成格式，并将生成的拓扑图直接打入底层的 Rust 引擎执行 Kahn 环路检测与 d-分离验证。一旦发现逻辑死循环或伪相关，Rust 会立即中断并强制模型重写，同时清理显存。

---

## ⚡ 快速上手

我们已经将完整的 C++ 编译环境、CUDA 加速算子以及依赖沙盒固化在了 `.devcontainer` 中，强烈建议直接使用 VS Code 的 Dev Container 启动，避免本地配环境踩坑。

### 1. 环境准备

1. 宿主机安装 Docker 与 VS Code 的 Dev Containers 插件。
2. 使用 VS Code 打开项目根目录，点击右下角 `Reopen in Container`。
3. 等待镜像构建（初次启动会自动编译带 CUDA 支持的 `llama-cpp-python`）。
4. 将量化好的模型文件（如 `qwen2.5.gguf`）放入工作区根目录。

### 2. 编译 Rust 底层核心

进入核心目录并使用 Maturin 编译 Rust 代码到当前的 Python 虚拟环境中：

```bash
cd causal_fmea_core
maturin develop --release
```

### 3. 运行推理测试

退回 Python 侧工作目录，启动 LangGraph 状态机：

```bash
cd ../python/causal_fmea
python app.py
```

---

## 📂 目录结构

```text
causal_fmea_core/
├── Cargo.toml                          # Rust 依赖配置
├── pyproject.toml                      # Maturin 构建配置
├── src/                                # Rust 底层图引擎 (编译为 Python 扩展)
│   ├── lib.rs                          # PyO3 FFI 接口与内存回收生命周期管理
│   ├── dag.rs                          # 基于一维数组的高性能邻接表图结构
│   ├── algorithms.rs                   # Kahn 环路检测与贝叶斯球 d-分离算法
│   └── fmea_evaluator.rs               # FMEA (SOD) 风险评分计算模块
├── python/
│   └── causal_fmea/                    # Python 上层控制流
│       ├── app.py                      # LangGraph 状态机定义与执行入口
│       ├── agent_state_machine.py      # 全局状态字典与 Pydantic 结构约束
│       ├── nodes.py                    # 大模型生成节点 (Generator) 与 Rust 验证节点 (Validator)
│       └── context_guard.py            # VRAM 上下文管理器，控制 Rust 引擎销毁与 GC
└── testpy/                             # 早期功能测试脚本

```

---

## ⚙️ 核心模块解析

### Rust 侧核心 (`src/`)

负责所有计算密集型操作与严格的内存管理：

* **`dag.rs`**: 抛弃冗余的对象结构，直接用 `Vec<Vec<usize>>` 构建极度轻量的拓扑图。
* **`algorithms.rs`**: 核心测谎仪。包含查环路（Kahn）和查伪相关（d-separation）的实现。
* **`lib.rs`**: 暴露 `CausalParadigmEngine` 类给 Python。内置线程安全的字符串驻留池（String Interner），确保跨界数据零拷贝。通过实现 `Drop trait` 的 `LlamaMemoryReaper`，保证每次 Python 抛弃引擎引用时，底层内存被彻底回收。

### Python 侧核心 (`python/causal_fmea/`)

负责业务编排与大模型交互：

* **`agent_state_machine.py`**: 定义了 LangGraph 的全局数据总线 `CausalAgentState`。通过 Pydantic 定义 `ExtractedGraph`，配合 llama.cpp 的 GBNF 语法树强制约束 LLM 只输出合法 JSON。
* **`context_guard.py`**: 实现 `AgentContext`，确保 `validate_graph_node` 跑完后强制调用 `gc.collect()` 触发 Rust 底层的析构函数，防止 KV Cache 撑爆 8GB 显存。
* **`nodes.py`**: 包含两个工作节点。Generator 调用本地量化模型，Validator 将数据通过 FFI 传入 Rust 并返回拦截报告。
* **`app.py`**: 用 `should_continue` 函数实现条件路由（打回重做、达到重试上限熔断、验证通过结案）。

---

## 🔄 系统数据流转图

```text
 用户场景输入 ─→ [本地 LLM + JSON Schema 硬约束] ─→ ExtractedGraph (Pydantic)
                                                        │
                                                        ▼
                                             [(source, target)] 边列表
                                                        │
                                                   [ PyO3 FFI ]
                                                        │
                                                        ▼
                     ┌────────────────────────────────────────────────────────┐
                     │ Rust 底层引擎处理:                                     │
                     │ 1. 字符串驻留池映射为 usize ID                         │
                     │ 2. 写入 CompactCausalGraph 邻接表                      │
                     │ 3. 执行算法验证 (Kahn 查环 / d-分离)                   │
                     └────────────────────────────────────────────────────────┘
                                                        │
                                            ┌───────────┴───────────┐
                                            │                       │
                                          验证通过                验证失败 
                                            │                       │
                                            ▼                       ▼
                                       任务结束 END          附带 Rust 诊断报告
                                                             触发重试路由回滚至 LLM

```