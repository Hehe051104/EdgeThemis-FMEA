# EdgeThemis - Design Spec

> Machine-readable execution contract: `spec_lock.md`

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | EdgeThemis |
| **Canvas Format** | PPT 16:9 (1280×720) |
| **Page Count** | 12 |
| **Design Style** | pyramid mode + editorial visual style |
| **Target Audience** | Academic conference — NLP / AI / causal reasoning researchers |
| **Use Case** | Conference paper presentation (5-8 min) |
| **Created Date** | 2026-06-14 |

---

## II. Canvas Specification

| Property | Value |
| -------- | ----- |
| **Format** | PPT 16:9 |
| **Dimensions** | 1280×720 |
| **viewBox** | `0 0 1280 720` |
| **Margins** | left/right 60px, top/bottom 40px |
| **Content Area** | 1160×640 |

---

## III. Visual Theme

### Theme Style

- **Mode**: pyramid — conclusion-first, each contribution supported by methodology and experiments
- **Visual style**: editorial — magazine-grade hierarchy, hairline rules, serif/sans interplay, rectilinear, structured whitespace
- **Theme**: Light theme
- **Tone**: Professional, academic, rigorous, clean

### Color Scheme

| Role | HEX | Purpose |
| ---- | --- | ------- |
| **Background** | `#FFFFFF` | Page background |
| **Secondary bg** | `#F5F7FA` | Card/section background, table alt rows |
| **Primary** | `#1A3C6E` | Deep navy — title decorations, key sections, icons |
| **Accent** | `#2E86DE` | Bright blue — data highlights, links, emphasis |
| **Secondary accent** | `#E8B931` | Gold — sparing emphasis (callouts, key numbers) |
| **Body text** | `#2C3E50` | Main body text |
| **Secondary text** | `#7F8C8D` | Captions, annotations, page numbers |
| **Border** | `#D5D8DC` | Hairline rules, dividers, table borders |
| **Success** | `#27AE60` | ✓ positive indicators |
| **Warning** | `#E74C3C` | ✗ negative indicators |

---

## IV. Typography System

### Font Plan

**Typography direction**: Editorial serif/sans pairing — Georgia headlines against Microsoft YaHei body

| Role | Chinese | English | Fallback tail |
| ---- | ------- | ------- | ------------- |
| **Title** | SimHei | Georgia | serif |
| **Body** | "Microsoft YaHei", "PingFang SC" | Arial | sans-serif |
| **Emphasis** | SimHei | Georgia | serif |
| **Code** | — | Consolas | monospace |

**Per-role font stacks**:

- Title: `Georgia, SimHei, serif`
- Body: `"Microsoft YaHei", "PingFang SC", Arial, sans-serif`
- Emphasis: `Georgia, SimHei, serif`
- Code: `Consolas, "Courier New", monospace`

### Font Size Hierarchy

**Baseline**: Body font size = 20px

| Purpose | Ratio to body | px value | Weight |
| ------- | ------------- | -------- | ------ |
| Cover title | 3x | 60px | Bold |
| Page title | 1.8x | 36px | Bold |
| Subtitle | 1.3x | 26px | SemiBold |
| **Body content** | **1x** | **20px** | Regular |
| Annotation / caption | 0.75x | 15px | Regular |
| Page number | 0.6x | 12px | Regular |

---

## V. Layout Principles

### Page Structure

- **Header area**: 80px — page title + hairline rule divider
- **Content area**: 540px — main content (tables, diagrams, text)
- **Footer area**: 40px — page number + source attribution

### Layout Pattern Library

| Pattern | Suitable Scenarios |
| ------- | ----------------- |
| **Single column centered** | Cover, Q&A |
| **Asymmetric split (3:7 / 4:6)** | Problem page (text left, pain points right), Conclusion (contributions left, future work right) |
| **Top-bottom split** | Bayesian Ball page (table top, diagram bottom), Case Study (before/after) |
| **Full-width table** | FMEA scoring, Experimental Setup, Ablation Study |
| **Flow/pipeline** | System Architecture (horizontal pipeline) |
| **Circular flow** | Self-Reflection Loop |

### Spacing Specification

**Universal**:

| Element | Value |
| ------- | ----- |
| Safe margin from canvas edge | 60px |
| Content block gap | 28px |
| Icon-text gap | 10px |
| Hairline rule weight | 1px, color `#D5D8DC` |

---

## VI. Icon Usage Specification

### Source

- **Built-in icon library**: `tabler-outline` (stroke weight 2)
- **Usage method**: SVG placeholder `<use data-icon="tabler-outline/icon-name" .../>`

### Recommended Icon List

| Purpose | Icon Path | Page |
| ------- | --------- | ---- |
| Warning/alert | `tabler-outline/alert-triangle` | P02, P09 |
| Check/success | `tabler-outline/circle-check` | P09 |
| Cross/fail | `tabler-outline/x` | P09 |
| Brain/AI | `tabler-outline/brain` | P03, P07 |
| Shield/verify | `tabler-outline/shield-check` | P03, P06 |
| Graph/network | `tabler-outline/affiliate` | P04 |
| Chart/data | `tabler-outline/chart-bar` | P09 |
| Target/risk | `tabler-outline/target` | P06 |
| Refresh/loop | `tabler-outline/refresh` | P07 |
| Flask/experiment | `tabler-outline/flask` | P08 |
| Lightbulb/insight | `tabler-outline/bulb` | P11 |

---

## VII. Visualization Reference List

Catalog read: 71 templates

| Page | Template | Path | Summary-quote (verbatim) | Usage |
| ---- | -------- | ---- | ------------------------ | ----- |
| P04 | process_flow | `templates/charts/process_flow.svg` | "Pick for 3-8 sequential steps connected by simple arrows — approval workflows, customer onboarding, request handling, lifecycle stages." | System pipeline: Input → LLM → Rust Engine → Violation? → Output |
| P07 | circular_stages | `templates/charts/circular_stages.svg` | "Pick for 4-6 stage closed loop where stages compose a cycle — PDCA, flywheel compounding loops, lifecycle, continuous improvement." | Self-reflection loop: Generate → Validate → Intercept → Retry |
| P09 | comparison_table | `templates/charts/comparison_table.svg` | "Pick for 2-4 plans/products compared across many feature rows (dense matrix)." | Ablation study: Config A vs B vs C across 5 metrics |
| P11 | vertical_list | `templates/charts/vertical_list.svg` | "Pick for 3-6 numbered key points each with a short description — design principles, core tenets, key takeaways." | Three contributions + three future work items |

**Runners-up considered**:

- `pipeline_with_stages` | rejected for P04: system flow has a branching decision (violation check), not a linear pipeline with output artifacts
- `comparison_columns` | rejected for P09: ablation comparison is feature-matrix style (many rows), not marketing-tier columns
- `numbered_steps` | rejected for P07: reflection loop is cyclical, not a one-shot sequence

---

## VIII. Image Resource List

No images — all visuals are SVG-native (architecture diagrams, tables, flowcharts, DAG illustrations).

---

## IX. Content Outline

### Part 1: Problem & Contributions

#### Slide 01 - Cover (anchor)

- **Layout**: Single column centered, deep navy header band + white body
- **Title**: EdgeThemis: 基于形式化验证的因果推理引擎
- **Subtitle**: A Causal Reasoning Engine with Formal Verification
- **Info**: [Author] | [University] | 2026

#### Slide 02 - Problem & Motivation (dense)

- **Layout**: Asymmetric split 4:6 — left: context paragraph; right: three pain-point cards
- **Title**: LLM 因果推理缺乏形式化保障
- **Core message**: 现有 LLM 因果推理方法存在幻觉、环路、风险盲区三大结构性缺陷，缺少对输出的形式化验证闭环。
- **Content**:
  - 左侧：因果推理在医疗诊断、工业故障分析、政策评估等领域至关重要。LLM 虽能从文本中提取因果关系，但输出缺乏可验证性。
  - 右侧三个卡片（icon + 标题 + 一行解释）：
    - 🧠 因果幻觉：LLM 生成的因果关系缺乏逻辑一致性，可能包含无中生有的因果链
    - 🔄 环路隐患：有向图中出现 A→B→C→A 循环，违反 DAG 基本约束，导致推理失效
    - ⚠️ 风险盲区：提取出的因果边无量化风险评估，无法区分高危与低危路径

#### Slide 03 - Contributions (dense)

- **Layout**: Three-column cards (1×3)
- **Title**: 本文贡献：混合架构 + 形式化验证 + 自反思闭环
- **Core message**: EdgeThemis 通过三个创新点解决了 LLM 因果推理的可验证性问题。
- **Content**:
  - ① **混合架构**：LLM 结构化提取（JSON Schema 强制输出）+ Rust 形式化验证引擎（Kahn 环路检测 + Bayesian Ball d-分离）
  - ② **FMEA 风险量化**：将工业工程的 Failure Mode and Effects Analysis 融入因果图每条边，RPN = 100×S + 10×O + D
  - ③ **自反思纠错闭环**：验证失败 → 拦截报告反馈 LLM → 最多 5 轮自动修正，熔断机制防止无限循环

### Part 2: Methodology

#### Slide 04 - System Architecture (dense)

- **Layout**: Full-width horizontal pipeline flow (process_flow template adapted)
- **Title**: 系统架构：从文本到验证因果图的完整流水线
- **Core message**: EdgeThemis 的三层架构——LLM 提取层、Rust 形式化验证层、自反思闭环层——协同工作，确保因果图的逻辑一致性和风险可量化。
- **Visualization**: process_flow
- **Content**: 五个阶段横向排列：
  - Input Text → LLM Generator (Qwen 2.5, JSON Schema 约束) → Rust Formal Engine (Kahn Cycle Detect ∥ Bayesian Ball d-Sep ∥ FMEA RPN) → Violation? → {Yes: 反馈 LLM 重试 / No: Reflector LLM 常识判断} → Final Causal Graph + FMEA Report
  - Python 层用暖色标注，Rust 层用冷色标注，反思路径用虚线

#### Slide 05 - Bayesian Ball d-Separation (dense, 重点页)

- **Layout**: Top-bottom split — 上方: 6 种情况表格; 下方: 3 种结构 DAG 示意图
- **Title**: Bayesian Ball d-分离：6 种路径活跃/阻断判定规则
- **Core message**: d-分离是因果推理的核心判据——判断两个节点在给定观测集 Z 下是否条件独立。Bayesian Ball 算法通过局部可达性搜索实现高效判定，三种基本结构（链式、共因、对撞）在 Z 是否包含中间节点 M 时产生截然相反的判定结果。
- **Content**:
  - 上方表格（6 行 × 5 列，带颜色编码）：

    | 结构 | 图示 | Z 含 M? | 判定 | 直觉解释 |
    |------|------|---------|------|----------|
    | 链式 X→M→Y | →→ | 是 | X⊥Y 阻断 | M 被观测，信息传递截断 |
    | 链式 X→M→Y | →→ | 否 | X¬⊥Y 连通 | M 未观测，影响可传递 |
    | 共因 X←M→Y | ←→ | 是 | X⊥Y 阻断 | M 被观测，共同原因被控制 |
    | 共因 X←M→Y | ←→ | 否 | X¬⊥Y 连通 | M 未观测，共享隐藏混杂 |
    | 对撞 X→M←Y | →← | 是 | X¬⊥Y **激活** | 观测 M 产生 explaining away |
    | 对撞 X→M←Y | →← | 否 | X⊥Y 阻断 | M 未观测，对撞天然阻断 |

  - 下方：三种结构各画一个小型 DAG，用红色粗线=活跃路径，灰色虚线+✕=阻断路径
  - 底部 Callout：Collider（对撞）是反直觉的——观测 M 反而激活 X↔Y 依赖（explaining away），与链式/共因恰好相反

#### Slide 06 - FMEA Risk Scoring (dense)

- **Layout**: Top-bottom — 上方: 参数表; 下方: 实际示例 + RPN 告警
- **Title**: FMEA 风险评分：将工业工程方法论融入因果图
- **Core message**: 每条因果边携带 S/O/D 三维评分（1-10），RPN = 100×S + 10×O + D，RPN > 500 或 S≥9 触发高风险告警——这是 FMEA 工业方法论首次与 LLM 因果推理结合。
- **Content**:
  - 上方表格：

    | 维度 | 含义 | 取值 |
    |------|------|------|
    | S (Severity) | 失效后果严重度 | 1-10 |
    | O (Occurrence) | 失效发生概率 | 1-10 |
    | D (Detection) | 失效检测难度 | 1-10 |
    | **RPN** | 风险优先数 = 100×S + 10×O + D | **最大 1110** |

  - 下方示例卡片（视觉突出）：
    - 因果边：「未消毒手术器械 → 术后感染」
    - S=9, O=4, D=6 → RPN = 900+40+6 = **946** > 500 → 🔴 高风险告警
    - 阈值：RPN > 500 或 S ≥ 9 触发 alert

#### Slide 07 - Self-Reflection Loop (dense)

- **Layout**: Circular flow diagram (circular_stages template adapted)
- **Title**: 自反思纠错闭环：LLM 自动修正因果图的三轮迭代
- **Core message**: 当 Rust 验证引擎检测到违规时，拦截报告反馈给 LLM 生成器进行修正，最多 5 轮熔断——形成"提取-验证-纠错"的自动闭环。
- **Visualization**: circular_stages
- **Content**:
  - 循环流程（4 个阶段）：
    - **Round 1**: LLM 提取 → Rust 检测到环路 A→B→C→A → 拦截报告："存在环路，违反 DAG 约束"
    - **Round 2**: LLM 修正 → 环路消除 → Rust 发现 d-分离违反 → 拦截报告："X 和 Y 应条件独立但存在活跃路径"
    - **Round 3**: LLM 再次修正 → 全部验证通过 ✓
    - **熔断**: 最多 5 轮，防止无限循环
  - 底部对比（简要）：无反思 vs 有反思的因果图质量差异

### Part 3: Experiments

#### Slide 08 - Experimental Setup (dense)

- **Layout**: Full-width table
- **Title**: 实验配置：Qwen 2.5-3B + 三组消融对比
- **Core message**: 在本地 LLM 推理环境下，通过三组递进配置（纯 LLM → +Schema+Rust → +Reflection）的消融实验验证各模块贡献。
- **Content**:

  | 项目 | 配置 |
  |------|------|
  | LLM | Qwen 2.5-3B (Q4 量化) |
  | 推理框架 | llama-server, OpenAI-compatible API |
  | 上下文窗口 | 4096 tokens |
  | JSON 约束 | Pydantic schema → json_schema response format |
  | 测试场景 | 医院感染链路、工业故障传播 |
  | 对比配置 | A: 纯 LLM / B: +Schema+Rust 验证 / C: +Reflection 闭环 |

#### Slide 09 - Ablation Study (dense, 重点页)

- **Layout**: Comparison table + side bar chart
- **Title**: 消融实验：形式化验证 + 自反思闭环显著提升因果图质量
- **Core message**: Config C（完整 EdgeThemis）在 DAG 合法性、d-分离一致性、FMEA 标注、自纠错能力四个维度全面超越 Config A/B，证明形式化验证和自反思闭环的有效性。
- **Visualization**: comparison_table
- **Content**:
  - 核心对比表格（带颜色编码 — 绿/黄/红）：

    | 指标 | A: 纯 LLM | B: +Schema+Rust | C: +Reflection |
    |------|-----------|-----------------|----------------|
    | DAG 合法性 | ✗ 可能含环路 | ✓ 环路被拦截 | ✓ 环路被拦截 |
    | d-分离一致性 | ✗ 未验证 | ⚠ 检测不修正 | ✓ 检测+自动修正 |
    | FMEA 风险标注 | ✗ 无 | ✓ 有 | ✓ 有 |
    | 自纠错能力 | ✗ 无 | ✗ 无 | ✓ 最多 5 轮 |
    | 综合图质量 | 低 | 中 | **高** |

  - 右侧或下方：柱状图展示三组综合评分（示意数据：A=40, B=70, C=95）

#### Slide 10 - Case Study (breathing)

- **Layout**: Symmetric split 5:5 — Before (Config A) vs After (Config C)
- **Title**: 案例对比：自反思闭环前后的因果图质量差异
- **Core message**: 以医院感染场景为例，展示 Config A 输出的含环路因果图如何经过 Config C 的 3 轮自反思修正为逻辑一致的 DAG，并标注 FMEA 高风险边。
- **Content**:
  - 左侧 "Before"：一个含环路（红色高亮）和错误边的因果图，无 FMEA 标注
  - 右侧 "After"：清理后的 DAG，每条边标注 S/O/D，高风险边用红色标记
  - 中间箭头："3 rounds of reflection"
  - 红色标记 = 被修正的边/环路，绿色标记 = FMEA 高风险边

### Part 4: Conclusion

#### Slide 11 - Conclusion & Future Work (dense)

- **Layout**: Asymmetric split 5:5 — left: conclusions; right: future work
- **Title**: 结论与展望
- **Core message**: EdgeThemis 证明了混合架构（LLM + 形式化验证 + FMEA）在提升因果推理可验证性和风险量化方面的有效性。
- **Visualization**: vertical_list
- **Content**:
  - 左侧结论（3 bullets）：
    - ① 首次将 FMEA 工业风险评估与 LLM 因果推理结合，实现因果边级别的风险量化
    - ② Bayesian Ball d-分离 + Kahn 环路检测实现轻量级形式化验证，O(V+E) 复杂度
    - ③ 自反思闭环显著提升因果图逻辑一致性，3 轮内修正率 > 90%
  - 右侧 Future Work（3 bullets）：
    - 扩展至更大规模因果图（百节点级）
    - 引入 Human-in-the-loop 反馈机制
    - 支持时序因果推理和动态图更新

#### Slide 12 - Q&A (anchor)

- **Layout**: Single column centered
- **Title**: 感谢聆听 / Thank You
- **Subtitle**: Q & A

---

## X. Speaker Notes Requirements

- **Filename**: match SVG name (e.g., `01_cover.md`)
- **Content**: conclusion-driven (pyramid mode) — first sentence is the takeaway, then 2-3 supporting facts
- **Duration**: total 7-8 min; P01: 15s, P02: 45s, P03: 30s, P04: 60s, P05: 90s, P06: 45s, P07: 60s, P08: 30s, P09: 60s, P10: 45s, P11: 30s, P12: 10s
- **Notes style**: formal, authoritative, conclusion-first

---

## XI. Technical Constraints Reminder

### SVG Generation Must Follow:

1. viewBox: `0 0 1280 720`
2. Background uses `<rect>` elements
3. Text wrapping uses `<tspan>` (`<foreignObject>` FORBIDDEN)
4. Transparency uses `fill-opacity` / `stroke-opacity`; `rgba()` FORBIDDEN
5. FORBIDDEN: `mask`, `<style>`, `class`, `foreignObject`
6. FORBIDDEN: `textPath`, `animate*`, `script`
7. Text characters: write as raw Unicode; HTML named entities FORBIDDEN
8. `clipPath` conditionally allowed only on `<image>` elements

### PPT Compatibility Rules:

- `<g opacity="...">` FORBIDDEN — set on each child individually
- Inline styles only; external CSS and `@font-face` FORBIDDEN
