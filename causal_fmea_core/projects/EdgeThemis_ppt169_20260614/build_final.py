#!/usr/bin/env python3
"""Build final EdgeThemis PPT — workflow-ordered, all components covered."""
import os, math

OUT = "svg_output"
os.makedirs(OUT, exist_ok=True)

# ============================================================
# Stage indicator — maps to project pipeline stages
# ============================================================
PIPELINE = [
    ("input",      "Input",       "#7F8C8D", 30),
    ("generator",  "Generator",   "#E8B931", 110),
    ("intern",     "Interning",   "#2E86DE", 190),
    ("cycle",      "Kahn Cycle",  "#2E86DE", 275),
    ("dsep",       "d-Separation","#1A3C6E", 365),
    ("fmea",       "FMEA RPN",    "#2E86DE", 450),
    ("reflector",  "Reflector",   "#E8B931", 530),
    ("output",     "Output",      "#27AE60", 605),
]

def indicator(active, label_override=None):
    lines = ['<g id="stage-indicator" transform="translate(590, 14)">',
             '<rect x="0" y="0" width="640" height="42" rx="6" fill="#F5F7FA" stroke="#D5D8DC" stroke-width="1"/>']
    for sid, label, color, cx in PIPELINE:
        act = (sid == active)
        r = 10 if act else 6
        fill = color if act else "#D5D8DC"
        tf = color if act else "#7F8C8D"
        fw = ' font-weight="bold"' if act else ''
        fs = "10" if act else "8"
        lines.append(f'<circle cx="{cx}" cy="14" r="{r}" fill="{fill}"/>')
        if act:
            lines.append(f'<text x="{cx}" y="38" text-anchor="middle" font-family="Arial, sans-serif" font-size="{fs}" fill="{tf}"{fw}>{label}</text>')
        else:
            lines.append(f'<text x="{cx}" y="38" text-anchor="middle" font-family="Arial, sans-serif" font-size="7" fill="{tf}">{label}</text>')
    # Connecting lines
    for i in range(len(PIPELINE)-1):
        x1 = PIPELINE[i][3] + 10
        x2 = PIPELINE[i+1][3] - 10
        act_i = PIPELINE[i][0] == active
        act_next = PIPELINE[i+1][0] == active
        sc = "#D5D8DC"
        sw = "1.5"
        lines.append(f'<line x1="{x1}" y1="14" x2="{x2}" y2="14" stroke="{sc}" stroke-width="{sw}"/>')
    # Python/Rust labels
    lines.append('<rect x="630" y="5" width="60" height="30" rx="4" fill="#FFF" stroke="#D5D8DC" stroke-width="0.5"/>')
    lines.append('<circle cx="640" cy="14" r="3" fill="#E8B931"/><text x="648" y="17" font-family="Arial, sans-serif" font-size="7" fill="#7F8C8D">Python</text>')
    lines.append('<circle cx="640" cy="26" r="3" fill="#2E86DE"/><text x="648" y="29" font-family="Arial, sans-serif" font-size="7" fill="#7F8C8D">Rust</text>')
    lines.append('</g>')
    return "\n".join(lines)

# ============================================================
# Common SVG elements
# ============================================================
def svg(content):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">\n{content}\n</svg>'

def shadow_filter():
    return '<defs><filter id="cs" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur in="SourceAlpha" stdDeviation="4"/><feOffset dx="0" dy="2" result="ob"/><feFlood flood-color="#000" flood-opacity="0.06" result="sc"/><feComposite in="sc" in2="ob" operator="in" result="s"/><feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'

def header(title, subtitle, stage, label_override=None):
    return f'''<rect width="1280" height="720" fill="#FFFFFF"/>
<g id="header"><rect x="60" y="30" width="5" height="32" rx="2" fill="#1A3C6E"/>
<text x="78" y="56" font-family="Georgia, SimHei, serif" font-size="28" font-weight="bold" fill="#1A3C6E">{title}</text>
<text x="78" y="76" font-family="Arial, sans-serif" font-size="14" fill="#7F8C8D">{subtitle}</text>
<line x1="60" y1="88" x2="1220" y2="88" stroke="#D5D8DC" stroke-width="1"/></g>
{indicator(stage, label_override)}'''

def footer(n):
    return f'<text x="60" y="695" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">{n:02d}</text><text x="1220" y="695" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">EdgeThemis</text>'

def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {name}")

# ============================================================
# Load existing SVGs and update stage indicators
# ============================================================
def update_stage(filename, new_stage):
    """Read existing SVG, replace stage indicator, write back."""
    path = os.path.join(OUT, filename)
    if not os.path.exists(path):
        return False
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    # Remove existing stage indicator
    start = content.find('<g id="stage-indicator"')
    if start != -1:
        end = content.find('</g>', start) + 4
        content = content[:start] + content[end:]
    # Insert new indicator after header closing </g>
    header_end = content.find('</g>', content.find('id="header"'))
    if header_end == -1:
        header_end = content.find('</g>', content.find('header'))
    if header_end != -1:
        insert_pos = content.find('>', header_end) + 1
        content = content[:insert_pos] + "\n" + indicator(new_stage) + "\n" + content[insert_pos:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return True

# ============================================================
# Build all pages
# ============================================================
print("=== Building EdgeThemis Final PPT ===\n")

# --- P01: Cover (keep existing) ---
print("[KEEP] P01 cover")

# --- P02: Motivation (keep existing, stage=generator) ---
print("[KEEP] P02 motivation")

# --- P03: Problem (keep, stage=input) ---
print("[KEEP] P03 problem")

# --- P04: Contributions (keep, stage=overview) ---
print("[KEEP] P04 contributions")

# --- P05: Architecture (keep, stage=overview) ---
print("[KEEP] P05 architecture")

# --- P06: NEW — Generator Node: LLM Structured Extraction ---
write("06_generator.svg", svg(f'''{shadow_filter()}
{header("Generator 节点：LLM 结构化提取", "Structured Causal Graph Extraction via JSON Schema", "generator")}
<g id="overview" filter="url(#cs)">
  <rect x="60" y="105" width="560" height="300" rx="10" fill="#FFF"/>
  <rect x="60" y="105" width="560" height="6" rx="3" fill="#E8B931"/>
  <text x="80" y="140" font-family="Georgia, SimHei, serif" font-size="18" fill="#1A3C6E" font-weight="bold">工作流程</text>
  <text x="80" y="170" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">1. 接收自然语言文本输入</text>
  <text x="80" y="196" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">2. 通过<tspan font-weight="bold" fill="#1A3C6E">JSON Schema</tspan>约束 LLM 输出格式</text>
  <text x="80" y="222" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">3. 强制输出<tspan font-weight="bold" fill="#1A3C6E">CausalEdge</tspan>结构：</text>
  <text x="100" y="248" font-family="Consolas, monospace" font-size="13" fill="#2E86DE">{{cause, effect, S, O, D, reasoning}}</text>
  <text x="80" y="278" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">4. 同时输出<tspan font-weight="bold" fill="#1A3C6E">reasoning_process</tspan>（CoT 推理链）</text>
  <text x="80" y="304" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">5. Pydantic 模型校验：ExtractedGraph</text>
  <text x="80" y="330" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">6. 模型：<tspan font-weight="bold" fill="#1A3C6E">Qwen 2.5-3B</tspan> (Q4 量化, 4096 tokens)</text>
  <text x="80" y="360" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D">OpenAI-compatible API · llama-server · localhost:8080</text>
  <text x="80" y="388" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D">Python 层 · nodes.py → generate_graph_node()</text>
</g>
<g id="json-example" filter="url(#cs)">
  <rect x="640" y="105" width="580" height="300" rx="10" fill="#FFF"/>
  <rect x="640" y="105" width="580" height="6" rx="3" fill="#2E86DE"/>
  <text x="660" y="140" font-family="Georgia, SimHei, serif" font-size="18" fill="#1A3C6E" font-weight="bold">输出 JSON 示例</text>
  <text x="660" y="170" font-family="Consolas, monospace" font-size="12" fill="#2C3E50">{{</text>
  <text x="680" y="190" font-family="Consolas, monospace" font-size="12" fill="#2C3E50">"edges": [</text>
  <text x="700" y="210" font-family="Consolas, monospace" font-size="12" fill="#2C3E50">{{</text>
  <text x="720" y="230" font-family="Consolas, monospace" font-size="12" fill="#2E86DE">"cause": "消毒外包"</text>
  <text x="720" y="250" font-family="Consolas, monospace" font-size="12" fill="#2E86DE">"effect": "术后感染"</text>
  <text x="720" y="270" font-family="Consolas, monospace" font-size="12" fill="#E8B931">"S": 9, "O": 4, "D": 6</text>
  <text x="720" y="290" font-family="Consolas, monospace" font-size="12" fill="#7F8C8D">"reasoning": "..."</text>
  <text x="700" y="310" font-family="Consolas, monospace" font-size="12" fill="#2C3E50">}}]</text>
  <text x="680" y="330" font-family="Consolas, monospace" font-size="12" fill="#2C3E50">"reasoning_process": "...",</text>
  <text x="680" y="350" font-family="Consolas, monospace" font-size="12" fill="#2C3E50">"nodes": [...]</text>
  <text x="660" y="380" font-family="Consolas, monospace" font-size="12" fill="#2C3E50">}}</text>
</g>
<g id="note">
  <rect x="60" y="420" width="1160" height="55" rx="8" fill="#E8B931" fill-opacity="0.08"/>
  <text x="80" y="448" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50"><tspan font-weight="bold" fill="#1A3C6E">关键设计：</tspan>JSON Schema 约束确保 LLM 输出可被 Rust 引擎直接解析，无需后处理。Pydantic 校验在 Python 层兜底。</text>
  <text x="80" y="468" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D">agent_state_machine.py 定义 CausalEdge / ExtractedGraph / ReflectorVerdict / CausalAgentState</text>
</g>
{footer(6)}'''))

# --- P07: NEW — String Interning ---
write("07_interning.svg", svg(f'''{shadow_filter()}
{header("字符串驻留池：名称→整数 ID 映射", "String Interning: O(1) Node ID Lookup", "intern")}
<g id="concept" filter="url(#cs)">
  <rect x="60" y="105" width="560" height="250" rx="10" fill="#FFF"/>
  <rect x="60" y="105" width="560" height="6" rx="3" fill="#2E86DE"/>
  <text x="80" y="140" font-family="Georgia, SimHei, serif" font-size="18" fill="#1A3C6E" font-weight="bold">为什么需要字符串驻留？</text>
  <text x="80" y="170" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">LLM 输出的节点名是<tspan font-weight="bold" fill="#E74C3C">字符串</tspan>（如"术后感染"）</text>
  <text x="80" y="196" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">Rust 图算法操作的是<tspan font-weight="bold" fill="#27AE60">整数 ID</tspan>（如 0, 1, 2...）</text>
  <text x="80" y="226" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">字符串驻留池 = <tspan font-weight="bold" fill="#1A3C6E">IndexSet&lt;String&gt;</tspan> behind <tspan font-weight="bold" fill="#1A3C6E">Arc&lt;Mutex&gt;</tspan></text>
  <text x="80" y="256" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">• 去重：同一节点名只存一次</text>
  <text x="80" y="280" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">• O(1) 查找：名称→ID 瞬时完成</text>
  <text x="80" y="304" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">• 跨语言：Python FFI 零拷贝传入 Rust</text>
  <text x="80" y="334" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D">lib.rs → CausalParadigmEngine · string_pool: IndexSet&lt;String&gt;</text>
</g>
<g id="flow" filter="url(#cs)">
  <rect x="640" y="105" width="580" height="250" rx="10" fill="#FFF"/>
  <rect x="640" y="105" width="580" height="6" rx="3" fill="#2E86DE"/>
  <text x="660" y="140" font-family="Georgia, SimHei, serif" font-size="18" fill="#1A3C6E" font-weight="bold">数据流</text>
  <!-- Flow diagram -->
  <rect x="680" y="160" width="160" height="40" rx="8" fill="#E8B931" fill-opacity="0.15"/>
  <text x="760" y="185" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#E8B931" font-weight="bold">Python: "术后感染"</text>
  <text x="760" y="215" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#7F8C8D">↓ FFI inject_edges()</text>
  <rect x="680" y="230" width="160" height="40" rx="8" fill="#2E86DE" fill-opacity="0.15"/>
  <text x="760" y="255" text-anchor="middle" font-family="Consolas, monospace" font-size="13" fill="#2E86DE" font-weight="bold">Rust: ID = 3</text>
  <text x="760" y="285" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#7F8C8D">↓</text>
  <rect x="680" y="300" width="240" height="40" rx="8" fill="#1A3C6E" fill-opacity="0.1"/>
  <text x="800" y="325" text-anchor="middle" font-family="Consolas, monospace" font-size="13" fill="#1A3C6E" font-weight="bold">adjacency_list[3] = vec![7, 12]</text>
  <!-- Right side: memory layout -->
  <text x="960" y="160" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D" font-weight="bold">内存布局：</text>
  <text x="960" y="185" font-family="Consolas, monospace" font-size="12" fill="#2C3E50">IndexSet:</text>
  <text x="960" y="205" font-family="Consolas, monospace" font-size="12" fill="#2E86DE">0: "消毒外包"</text>
  <text x="960" y="225" font-family="Consolas, monospace" font-size="12" fill="#2E86DE">1: "灭菌浓度"</text>
  <text x="960" y="245" font-family="Consolas, monospace" font-size="12" fill="#2E86DE">2: "空气洁净度"</text>
  <text x="960" y="265" font-family="Consolas, monospace" font-size="12" fill="#2E86DE">3: "术后感染"</text>
  <text x="960" y="295" font-family="Consolas, monospace" font-size="12" fill="#7F8C8D">adjacency_list:</text>
  <text x="960" y="315" font-family="Consolas, monospace" font-size="12" fill="#2C3E50">[0] → [1, 2]</text>
  <text x="960" y="335" font-family="Consolas, monospace" font-size="12" fill="#2C3E50">[1] → [3]</text>
  <text x="960" y="355" font-family="Consolas, monospace" font-size="12" fill="#2C3E50">[2] → [3]</text>
</g>
<g id="note">
  <rect x="60" y="370" width="1160" height="50" rx="8" fill="#2E86DE" fill-opacity="0.06"/>
  <text x="80" y="398" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50"><tspan font-weight="bold" fill="#1A3C6E">CompactCausalGraph</tspan>：邻接表 + 反向邻接表，一维扁平数组，CPU 缓存友好。</text>
  <text x="80" y="416" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D">dag.rs · adjacency_list: Vec&lt;Vec&lt;usize&gt;&gt; · rev_adjacency_list: Vec&lt;Vec&lt;usize&gt;&gt; · dynamic capacity expansion</text>
</g>
{footer(7)}'''))

# --- P08: Kahn Cycle Detection (NEW) ---
write("08_kahn_cycle.svg", svg(f'''{shadow_filter()}
{header("Kahn 环路检测：拓扑排序拦截逻辑死循环", "Kahn Cycle Detection: O(V+E) Topological Sort", "cycle")}
<g id="algo" filter="url(#cs)">
  <rect x="60" y="105" width="560" height="320" rx="10" fill="#FFF"/>
  <rect x="60" y="105" width="560" height="6" rx="3" fill="#2E86DE"/>
  <text x="80" y="140" font-family="Georgia, SimHei, serif" font-size="18" fill="#1A3C6E" font-weight="bold">算法流程</text>
  <text x="80" y="170" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">1. 统计每个节点的<tspan font-weight="bold" fill="#1A3C6E">入度</tspan>（被指向的次数）</text>
  <text x="80" y="196" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">2. 将所有入度=0 的"自由节点"推入队列</text>
  <text x="80" y="222" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">3. 像<tspan font-weight="bold" fill="#1A3C6E">剥洋葱</tspan>一样层层拆解：</text>
  <text x="100" y="248" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">• 出队一个节点，processed++</text>
  <text x="100" y="274" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">• 将其所有邻居的入度-1</text>
  <text x="100" y="300" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">• 入度=0 的邻居入队</text>
  <text x="80" y="330" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">4. 终极审判：processed == n ? <tspan fill="#27AE60" font-weight="bold">无环</tspan> : <tspan fill="#E74C3C" font-weight="bold">有环!</tspan></text>
  <text x="80" y="360" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D">复杂度：O(V+E) · 空间：O(V)</text>
  <text x="80" y="380" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D">algorithms.rs → kahn_cycle_detect(graph) -> bool</text>
  <text x="80" y="400" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D">注入阶段即拦截自环边 v→v（add_edge 时检查）</text>
</g>
<g id="example" filter="url(#cs)">
  <rect x="640" y="105" width="580" height="320" rx="10" fill="#FFF"/>
  <rect x="640" y="105" width="580" height="6" rx="3" fill="#2E86DE"/>
  <text x="660" y="140" font-family="Georgia, SimHei, serif" font-size="18" fill="#1A3C6E" font-weight="bold">示例：检测到环路</text>
  <!-- DAG with cycle -->
  <g transform="translate(700, 200)">
    <circle cx="0" cy="0" r="24" fill="none" stroke="#E74C3C" stroke-width="2.5" stroke-dasharray="5,3"/>
    <text x="0" y="6" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#E74C3C" font-weight="bold">A</text>
    <line x1="24" y1="-12" x2="76" y2="-36" stroke="#2E86DE" stroke-width="2.5"/>
    <polygon points="76,-36 68,-30 72,-40" fill="#2E86DE"/>
    <circle cx="100" cy="-36" r="24" fill="none" stroke="#E74C3C" stroke-width="2.5" stroke-dasharray="5,3"/>
    <text x="100" y="-30" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#E74C3C" font-weight="bold">B</text>
    <line x1="124" y1="-24" x2="176" y2="0" stroke="#2E86DE" stroke-width="2.5"/>
    <polygon points="176,0 168,-6 172,8" fill="#2E86DE"/>
    <circle cx="200" cy="0" r="24" fill="none" stroke="#E74C3C" stroke-width="2.5" stroke-dasharray="5,3"/>
    <text x="200" y="6" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#E74C3C" font-weight="bold">C</text>
    <path d="M 176,16 Q 100,60 24,16" fill="none" stroke="#E74C3C" stroke-width="3" stroke-dasharray="8,4"/>
    <polygon points="26,14 18,22 30,22" fill="#E74C3C"/>
  </g>
  <text x="800" y="310" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#E74C3C" font-weight="bold">A→B→C→A 环路!</text>
  <!-- Kahn steps -->
  <text x="680" y="340" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">入度：A=1, B=1, C=1</text>
  <text x="680" y="365" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">入度=0 的节点：<tspan fill="#E74C3C" font-weight="bold">无！</tspan></text>
  <text x="680" y="390" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">processed=0 ≠ n=3 → <tspan fill="#E74C3C" font-weight="bold">有环！触发熔断！</tspan></text>
  <text x="680" y="415" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D">→ 生成拦截报告，反馈 LLM 重写</text>
</g>
{footer(8)}'''))

# --- P09: Bayesian Ball overview (keep existing P06, renumber) ---
# Will be handled by rename

# --- P10-P15: 6 d-separation cases (keep existing P07-P12, renumber) ---

# --- P16: FMEA (keep existing P13, renumber) ---

# --- P17: Reflector (keep existing P14, renumber) ---

# --- P18: Experiment (keep existing P15, renumber) ---

# --- P19: Ablation (keep existing P16, renumber) ---

# --- P20: Case Study (keep existing P17, renumber) ---

# --- P21: Conclusion (keep existing P18, renumber) ---

# --- P22: Q&A (keep existing P19, renumber) ---

print("\n[DONE] New pages generated. Now renaming existing pages...")

# ============================================================
# Rename existing pages to new numbering
# ============================================================
renames = {
    "06_bayesian_ball.svg": "09_bayesian_ball.svg",
    "07_case_chain_obs.svg": "10_case_chain_obs.svg",
    "08_case_chain_unobs.svg": "11_case_chain_unobs.svg",
    "09_case_fork_obs.svg": "12_case_fork_obs.svg",
    "10_case_fork_unobs.svg": "13_case_fork_unobs.svg",
    "11_case_collider_obs.svg": "14_case_collider_obs.svg",
    "12_case_collider_unobs.svg": "15_case_collider_unobs.svg",
    "13_fmea.svg": "16_fmea.svg",
    "14_reflection.svg": "17_reflection.svg",
    "15_experiment.svg": "18_experiment.svg",
    "16_ablation.svg": "19_ablation.svg",
    "17_case_study.svg": "20_case_study.svg",
    "18_conclusion.svg": "21_conclusion.svg",
    "19_qa.svg": "22_qa.svg",
}

for old, new in renames.items():
    op = os.path.join(OUT, old)
    np_ = os.path.join(OUT, new)
    if os.path.exists(op):
        os.rename(op, np_)
        print(f"  [RENAME] {old} → {new}")

# Update stage indicators on renamed pages
stage_map = {
    "09_bayesian_ball.svg": "dsep",
    "10_case_chain_obs.svg": "dsep",
    "11_case_chain_unobs.svg": "dsep",
    "12_case_fork_obs.svg": "dsep",
    "13_case_fork_unobs.svg": "dsep",
    "14_case_collider_obs.svg": "dsep",
    "15_case_collider_unobs.svg": "dsep",
    "16_fmea.svg": "fmea",
    "17_reflection.svg": "reflector",
    "18_experiment.svg": "output",
    "19_ablation.svg": "output",
    "20_case_study.svg": "output",
    "21_conclusion.svg": "output",
    "22_qa.svg": "output",
}

for filename, stage in stage_map.items():
    if update_stage(filename, stage):
        print(f"  [STAGE] {filename} → {stage}")

# Also update footer numbers
footer_updates = {
    "09_bayesian_ball.svg": "09",
    "10_case_chain_obs.svg": "10",
    "11_case_chain_unobs.svg": "11",
    "12_case_fork_obs.svg": "12",
    "13_case_fork_unobs.svg": "13",
    "14_case_collider_obs.svg": "14",
    "15_case_collider_unobs.svg": "15",
    "16_fmea.svg": "16",
    "17_reflection.svg": "17",
    "18_experiment.svg": "18",
    "19_ablation.svg": "19",
    "20_case_study.svg": "20",
    "21_conclusion.svg": "21",
    "22_qa.svg": "22",
}

import re
for filename, num in footer_updates.items():
    path = os.path.join(OUT, filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        # Update the page number in footer
        content = re.sub(r'font-size="12" fill="#7F8C8D">\d+</text><text x="1220"',
                         f'font-size="12" fill="#7F8C8D">{num}</text><text x="1220"', content)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

# Final file list
print("\n=== Final page list ===")
for f in sorted(os.listdir(OUT)):
    if f.endswith('.svg'):
        print(f"  {f}")
print(f"\nTotal: {len([f for f in os.listdir(OUT) if f.endswith('.svg')])} pages")
