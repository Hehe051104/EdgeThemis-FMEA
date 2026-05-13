# ⚡ EdgeThemis-FMEA: The Edge Causal Paradigm

**面向 8GB 边缘算力的 Agentic 因果推理失效模式分析（FMEA）与动态纠错范式**

![CUDA](https://img.shields.io/badge/CUDA-12.4-green.svg) ![Rust](https://img.shields.io/badge/Rust-Zero_Copy_FFI-orange.svg) ![VRAM](https://img.shields.io/badge/VRAM-8GB_Limit-blue.svg) ![Paper](https://img.shields.io/badge/Target-NeurIPS%2FICLR-purple.svg)

## 🚀 核心哲学：剥离云端幻觉，重塑硅基因果

学术界与工业界正逐渐回归理性：大语言模型（LLM）本质上是极其强大的“语义相关性捕获器”，而非“因果逻辑推演器”。在自动驾驶、医疗辅助等具身智能和边缘计算高危场景中，轻微的表层语义扰动极易导致 LLM 发生因果推理崩溃。

**EdgeThemis-FMEA** 是一套极端克制、专精于“纠错与验伤”的通用智能体外脑系统。我们面对的是 8GB 显存这一极其重要却被忽视的物理边界。本系统不追求提升通用生成质量，而是通过底层显存微操与图论拦截，建立起“符号-神经网络”协同进化的鲁棒性范式。

---

## 🛠️ 降维打击的架构设计 (System 1 + System 2)

传统多智能体系统（如 OrcheCause 等）在 8GB 设备上由于多个模型实例的加载，会瞬间触发 Out Of Memory (OOM) 崩溃。我们采取了绝对质疑的物理重构路线：

### 1. Python-Rust 极速零拷贝双系统
放弃臃肿的纯 Python 科学计算栈（如 DoWhy），利用 PyO3 绑定建立 Native Rust FFI 桥梁。在 Rust 侧手写扁平化一维邻接表，实现 `O(V+E)` 时间复杂度的增量 Kahn 无环检测与 d-分离（d-separation）路径扫描。

### 2. 时间多路复用与 KV 缓存锁闭 (Prefix Caching)
利用 `llama.cpp` 底层的 `/slots` 管理器锁死公共因果提示词状态。通过单实例时间多路复用，Agent 在物理内存中零延迟切换 Generator、Validator 与 Reflector 身份，将峰值显存死死锁在 4.5GB 以下。

### 3. FMEA 工业级量化拦截框架
将工业界 FMEA（失效模式与效应分析）引入大模型决策。系统计算严重度（S）、频度（O）、探测度（D）指标。通过核心公式 `SOD = 100 * S + 10 * O + D` 对“黑天鹅逻辑崩溃”进行量化，一旦风险越界（如 SOD > 600），Rust 引擎将执行硬性物理阻断。

---

## 🏗️ 核心流转引擎 (State Machine)

EdgeThemis-FMEA 将推演过程抽象为极简状态流：
1. **生成 (Generator)**: Python Agent 层基于 4-bit 量化大模型（如 NF4/Q4_K_M）提取变量节点及先验关系。
2. **验伤 (Validator)**: 零拷贝跨越 FFI 边界进入 Rust 核心（`CompactCausalGraph`）。执行后门准则（Backdoor Adjustment）校验与对撞节点（Collider Bias）探测。
3. **反思 (Reflector)**: 生成 `FmeaInterceptionReport` 诊断书，在 Python 侧拼装 Corrective Prompt 强制模型修正图谱。

---

## 📦 快速复现 (Zero-Configuration Metal)

本项目采用大厂标准的 Python-Rust 混合标准模块布局（Mixed Maturin Layout）。

**1. 拉取代码与配置环境**
```bash
git clone [https://github.com/YourName/EdgeThemis-FMEA.git](https://github.com/YourName/EdgeThemis-FMEA.git)
cd EdgeThemis-FMEA
# 在devcontainer.json文件中修改args里的CUDA_ARCH为当前设备显卡对应数值
# 推荐使用 VS Code DevContainer 打开，内置多阶段 CUDA 编译基座
# build之后终端执行：
sudo rm /usr/local/cuda/lib64/stubs/libcuda.so.1