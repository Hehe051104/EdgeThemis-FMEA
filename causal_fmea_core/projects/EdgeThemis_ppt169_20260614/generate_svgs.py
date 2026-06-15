#!/usr/bin/env python3
"""Generate all 21 SVG pages for EdgeThemis PPT with stage indicators."""
import os

OUTPUT_DIR = "svg_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Stage indicator positions and labels
STAGES = [
    ("input",      "Input",      None,      30),
    ("generator",  "Generator",  "Python",  95),
    ("cycle",      "Cycle",      "Rust",    165),
    ("dsep",       "d-Sep",      "Rust",    235),
    ("fmea",       "FMEA",       "Rust",    305),
    ("reflector",  "Reflector",  "Python",  375),
    ("output",     "Output",     None,      445),
]

LANG_COLORS = {"Python": ("#E8B931", "#E8B931"), "Rust": ("#2E86DE", "#2E86DE")}

def stage_indicator(active_stage):
    """Generate stage indicator SVG group."""
    lines = []
    lines.append('  <g id="stage-indicator" transform="translate(670, 16)">')
    lines.append('    <rect x="0" y="0" width="550" height="40" rx="6" fill="#F5F7FA" stroke="#D5D8DC" stroke-width="1"/>')

    for i, (sid, label, lang, cx) in enumerate(STAGES):
        is_active = (sid == active_stage)
        r = 8 if is_active else 6
        fill = "#1A3C6E" if is_active else "#D5D8DC"
        text_fill = "#1A3C6E" if is_active else "#7F8C8D"
        font_weight = ' font-weight="bold"' if is_active else ""
        label_display = label
        if is_active and sid == "dsep":
            label_display = "d-Sep"

        lines.append(f'    <circle cx="{cx}" cy="14" r="{r}" fill="{fill}"/>')
        if is_active and sid == "dsep":
            lines.append(f'    <text x="{cx}" y="18" text-anchor="middle" font-family="Arial, sans-serif" font-size="7" fill="#FFFFFF" font-weight="bold">d</text>')
        lines.append(f'    <text x="{cx}" y="34" text-anchor="middle" font-family="Arial, sans-serif" font-size="8" fill="{text_fill}"{font_weight}>{label_display}</text>')

        # Language tag
        if lang:
            opacity = "0.6" if is_active else "0.3"
            lcolor = LANG_COLORS[lang][0]
            lw = 34 if lang == "Python" else 26
            lcx = cx - lw/2 + 13
            lines.append(f'    <rect x="{lcx}" y="1" width="{lw}" height="5" rx="2" fill="{lcolor}" fill-opacity="{opacity}"/>')
            fw = ' font-weight="bold"' if is_active else ""
            lines.append(f'    <text x="{cx}" y="5" text-anchor="middle" font-family="Arial, sans-serif" font-size="5" fill="{lcolor}"{fw}>{lang}</text>')

    # Connecting lines
    connections = [
        (36, 89, False), (101, 159, False), (171, 227, False),
        (243, 299, False), (311, 369, False), (381, 439, False)
    ]
    for x1, x2, _ in connections:
        lines.append(f'    <line x1="{x1}" y1="14" x2="{x2}" y2="14" stroke="#D5D8DC" stroke-width="1.5"/>')

    # Language legend
    lines.append('    <rect x="470" y="5" width="70" height="28" rx="4" fill="#FFFFFF" stroke="#D5D8DC" stroke-width="0.5"/>')
    lines.append('    <circle cx="482" cy="14" r="3" fill="#E8B931"/>')
    lines.append('    <text x="490" y="17" font-family="Arial, sans-serif" font-size="7" fill="#7F8C8D">Python</text>')
    lines.append('    <circle cx="482" cy="25" r="3" fill="#2E86DE"/>')
    lines.append('    <text x="490" y="28" font-family="Arial, sans-serif" font-size="7" fill="#7F8C8D">Rust</text>')
    lines.append('  </g>')
    return "\n".join(lines)

def write_svg(filename, content):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {filename}")

# ============================================================
# P01: Cover
# ============================================================
def gen_p01():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <defs>
    <linearGradient id="navyBand" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#1A3C6E"/><stop offset="100%" stop-color="#0F2445"/></linearGradient>
    <linearGradient id="accentLine" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#2E86DE"/><stop offset="100%" stop-color="#E8B931"/></linearGradient>
  </defs>
  <rect width="1280" height="720" fill="#FFFFFF"/>
  <rect x="0" y="0" width="1280" height="380" fill="url(#navyBand)"/>
  <rect x="920" y="40" width="320" height="320" rx="4" fill="#FFFFFF" fill-opacity="0.03" transform="rotate(15, 1080, 200)"/>
  <circle cx="1080" cy="200" r="80" fill="none" stroke="#2E86DE" stroke-width="1" stroke-opacity="0.15"/>
  <circle cx="1080" cy="200" r="120" fill="none" stroke="#E8B931" stroke-width="0.8" stroke-opacity="0.1"/>
  <rect x="80" y="380" width="1120" height="4" fill="url(#accentLine)"/>
  <text x="80" y="150" font-family="Georgia, SimHei, serif" font-size="48" font-weight="bold" fill="#FFFFFF">EdgeThemis</text>
  <text x="80" y="210" font-family="Georgia, SimHei, serif" font-size="28" fill="#FFFFFF" fill-opacity="0.95">基于形式化验证的因果推理引擎</text>
  <text x="80" y="255" font-family="Georgia, SimHei, serif" font-size="20" fill="#FFFFFF" fill-opacity="0.7" font-style="italic">A Causal Reasoning Engine with Formal Verification</text>
  <g id="cover-keywords">
    <rect x="80" y="300" width="120" height="30" rx="15" fill="#2E86DE" fill-opacity="0.25"/><text x="140" y="320" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#FFFFFF" font-weight="600">LLM</text>
    <rect x="215" y="300" width="160" height="30" rx="15" fill="#2E86DE" fill-opacity="0.25"/><text x="295" y="320" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#FFFFFF" font-weight="600">Formal Verification</text>
    <rect x="390" y="300" width="100" height="30" rx="15" fill="#2E86DE" fill-opacity="0.25"/><text x="440" y="320" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#FFFFFF" font-weight="600">FMEA</text>
    <rect x="505" y="300" width="80" height="30" rx="15" fill="#E8B931" fill-opacity="0.25"/><text x="545" y="320" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#FFFFFF" font-weight="600">DAG</text>
    <rect x="600" y="300" width="160" height="30" rx="15" fill="#E8B931" fill-opacity="0.25"/><text x="680" y="320" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#FFFFFF" font-weight="600">Neuro-Symbolic</text>
  </g>
  <text x="80" y="420" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D">Based on: MSR (2023) Corr2Cause + Reflexion (NeurIPS 2023) + FMEA Industrial Standards</text>
  <text x="80" y="445" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D">Target: 8GB VRAM Edge Deployment (RTX 4060) · NeurIPS / ICLR</text>
  <text x="80" y="500" font-family="Arial, sans-serif" font-size="18" fill="#2C3E50" font-weight="600">[Author Name]</text>
  <text x="80" y="528" font-family="Arial, sans-serif" font-size="16" fill="#7F8C8D">[University / Lab]</text>
  <text x="80" y="575" font-family="Arial, sans-serif" font-size="14" fill="#7F8C8D">2026</text>
  <text x="1200" y="695" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">EdgeThemis — Causal Reasoning with Formal Verification</text>
</svg>'''

# ============================================================
# P02: Academic Motivation
# ============================================================
def gen_p02():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <defs><filter id="cs" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur in="SourceAlpha" stdDeviation="4"/><feOffset dx="0" dy="2" result="ob"/><feFlood flood-color="#000" flood-opacity="0.06" result="sc"/><feComposite in="sc" in2="ob" operator="in" result="s"/><feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  <rect width="1280" height="720" fill="#FFFFFF"/>
  <g id="header"><rect x="60" y="40" width="5" height="36" rx="2" fill="#1A3C6E"/><text x="78" y="67" font-family="Georgia, SimHei, serif" font-size="34" font-weight="bold" fill="#1A3C6E">学术背景与动机</text><text x="420" y="67" font-family="Arial, sans-serif" font-size="16" fill="#7F8C8D">Academic Background</text><line x1="60" y1="90" x2="1220" y2="90" stroke="#D5D8DC" stroke-width="1"/></g>
  <g id="msr" filter="url(#cs)"><rect x="60" y="110" width="560" height="170" rx="10" fill="#FFFFFF"/><rect x="60" y="110" width="560" height="6" rx="3" fill="#E74C3C"/><rect x="80" y="128" width="100" height="22" rx="11" fill="#E74C3C" fill-opacity="0.12"/><text x="130" y="144" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#E74C3C" font-weight="bold">痛点定义</text><text x="80" y="178" font-family="Arial, sans-serif" font-size="15" fill="#2C3E50" font-weight="bold">MSR (2023): "Can LLMs Infer Causation from Correlation?"</text><text x="80" y="205" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">微软证明：LLM 是"因果复读机"(Causal Parrots)，</text><text x="80" y="225" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">只能记住语料中的词汇共现，遇到抽象变量</text><text x="80" y="245" font-family="Arial, sans-serif" font-size="14" fill="#E74C3C" font-weight="bold">就彻底瞎蒙，表现等同于随机猜测。</text><text x="80" y="268" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">微调只是自欺欺人，遇到 OOD 数据立刻原形毕露</text></g>
  <g id="reflexion" filter="url(#cs)"><rect x="660" y="110" width="560" height="170" rx="10" fill="#FFFFFF"/><rect x="660" y="110" width="560" height="6" rx="3" fill="#27AE60"/><rect x="680" y="128" width="100" height="22" rx="11" fill="#27AE60" fill-opacity="0.12"/><text x="730" y="144" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#27AE60" font-weight="bold">解决方案</text><text x="680" y="178" font-family="Arial, sans-serif" font-size="15" fill="#2C3E50" font-weight="bold">Reflexion (NeurIPS 2023):</text><text x="680" y="205" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">提出 Actor → Evaluator → Reflection 闭环。</text><text x="680" y="225" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">用自然语言给出强化信号，让 LLM 自我纠错。</text><text x="680" y="245" font-family="Arial, sans-serif" font-size="14" fill="#27AE60" font-weight="bold">但 Evaluator 是"软性的"，无法保证数学正确性。</text><text x="680" y="268" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">语言审判无法保证 100% 的数学绝对确定性</text></g>
  <g id="timeline"><text x="640" y="318" text-anchor="middle" font-family="Georgia, SimHei, serif" font-size="18" font-weight="bold" fill="#1A3C6E">因果推理方法进化史</text><line x1="100" y1="345" x2="1180" y2="345" stroke="#D5D8DC" stroke-width="2"/><polygon points="1180,345 1170,340 1170,350" fill="#D5D8DC"/><circle cx="220" cy="345" r="16" fill="#E74C3C" fill-opacity="0.12"/><circle cx="220" cy="345" r="8" fill="#E74C3C"/><text x="220" y="375" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#E74C3C">Fine-tuning</text><text x="220" y="390" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#7F8C8D">死记硬背</text><circle cx="420" cy="345" r="16" fill="#E8B931" fill-opacity="0.12"/><circle cx="420" cy="345" r="8" fill="#E8B931"/><text x="420" y="375" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#E8B931">CoT</text><text x="420" y="390" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#7F8C8D">模板背诵</text><circle cx="620" cy="345" r="16" fill="#2E86DE" fill-opacity="0.12"/><circle cx="620" cy="345" r="8" fill="#2E86DE"/><text x="620" y="375" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#2E86DE">Multi-Agent</text><text x="620" y="390" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#7F8C8D">双模型辩论</text><circle cx="820" cy="345" r="16" fill="#2E86DE" fill-opacity="0.12"/><circle cx="820" cy="345" r="8" fill="#2E86DE"/><text x="820" y="375" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#2E86DE">Tool Use</text><text x="820" y="390" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#7F8C8D">调用外部库</text><circle cx="1040" cy="345" r="22" fill="#27AE60" fill-opacity="0.15"/><circle cx="1040" cy="345" r="12" fill="#27AE60"/><text x="1040" y="350" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#FFFFFF" font-weight="bold">Us</text><text x="1040" y="380" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#27AE60" font-weight="bold">EdgeThemis</text><text x="1040" y="395" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#27AE60">Neuro-Symbolic</text></g>
  <g id="positioning" filter="url(#cs)"><rect x="60" y="415" width="1160" height="250" rx="10" fill="#FFFFFF"/><rect x="60" y="415" width="1160" height="6" rx="3" fill="#1A3C6E"/><text x="80" y="450" font-family="Georgia, SimHei, serif" font-size="20" font-weight="bold" fill="#1A3C6E">EdgeThemis 的破局之道：用数学枷锁取代软性评估</text><rect x="80" y="468" width="520" height="36" rx="6" fill="#E74C3C" fill-opacity="0.06"/><text x="340" y="491" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#E74C3C" font-weight="bold">传统方案：软性 Evaluator → 语言判断，无数学保障</text><text x="620" y="491" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#7F8C8D">→</text><rect x="650" y="468" width="520" height="36" rx="6" fill="#27AE60" fill-opacity="0.06"/><text x="910" y="491" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#27AE60" font-weight="bold">EdgeThemis：Rust 确定性测谎仪 → 编译期数学保证</text><text x="100" y="525" font-family="Arial, sans-serif" font-size="13" fill="#2C3E50">• Reflexion: 用自然语言判断对错（软性）</text><text x="100" y="548" font-family="Arial, sans-serif" font-size="13" fill="#2C3E50">• CRAwDAD: 两个 LLM 互相辩论（Token 浪费）</text><text x="100" y="571" font-family="Arial, sans-serif" font-size="13" fill="#2C3E50">• Causal Agent: 调用 Python 因果库（延迟高）</text><text x="100" y="594" font-family="Arial, sans-serif" font-size="13" fill="#E74C3C">→ 本质都是"文科生思维"，无法保证数学绝对正确</text><text x="660" y="525" font-family="Arial, sans-serif" font-size="13" fill="#2C3E50">• Kahn 算法：<tspan font-weight="bold" fill="#1A3C6E">O(V+E)</tspan> 拓扑环路检测</text><text x="660" y="548" font-family="Arial, sans-serif" font-size="13" fill="#2C3E50">• Bayesian Ball：<tspan font-weight="bold" fill="#1A3C6E">O(V³)</tspan> d-分离断言提取</text><text x="660" y="571" font-family="Arial, sans-serif" font-size="13" fill="#2C3E50">• FMEA RPN：<tspan font-weight="bold" fill="#1A3C6E">100×S+10×O+D</tspan> 风险量化</text><text x="660" y="594" font-family="Arial, sans-serif" font-size="13" fill="#27AE60">→ 编译期确定性，微秒级拦截，零 GC 开销</text><line x1="80" y1="612" x2="1200" y2="612" stroke="#D5D8DC" stroke-width="1"/><text x="640" y="635" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#1A3C6E" font-weight="bold">核心创新：用 Rust 图论算子取代 Reflexion 的软性 Evaluator，将确定性拉满</text><text x="640" y="655" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">本质上是将形式化验证的确定性与 LLM 的生成式直觉在数学层面上完成暴力缝合</text></g>
  <text x="60" y="695" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">02</text><text x="1220" y="695" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">EdgeThemis</text>
</svg>'''

# ============================================================
# P03: Problem
# ============================================================
def gen_p03():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <defs><filter id="cs" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur in="SourceAlpha" stdDeviation="4"/><feOffset dx="0" dy="2" result="ob"/><feFlood flood-color="#000" flood-opacity="0.06" result="sc"/><feComposite in="sc" in2="ob" operator="in" result="s"/><feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  <rect width="1280" height="720" fill="#FFFFFF"/>
  <g id="header"><rect x="60" y="40" width="5" height="36" rx="2" fill="#1A3C6E"/><text x="78" y="67" font-family="Georgia, SimHei, serif" font-size="34" font-weight="bold" fill="#1A3C6E">LLM 因果推理缺乏形式化保障</text><text x="78" y="90" font-family="Arial, sans-serif" font-size="14" fill="#7F8C8D">LLM Causal Reasoning Lacks Formal Guarantees</text><line x1="60" y1="104" x2="1220" y2="104" stroke="#D5D8DC" stroke-width="1"/></g>
{stage_indicator("input")}
  <g id="context"><text x="60" y="145" font-family="Arial, sans-serif" font-size="18" fill="#2C3E50">因果推理在<tspan font-weight="bold" fill="#1A3C6E">医疗诊断</tspan>、<tspan font-weight="bold" fill="#1A3C6E">工业故障分析</tspan>、<tspan font-weight="bold" fill="#1A3C6E">政策评估</tspan>等领域至关重要。LLM 虽能从文本中提取因果关系，</text><text x="60" y="172" font-family="Arial, sans-serif" font-size="18" fill="#2C3E50">但输出<tspan font-weight="bold" fill="#E74C3C">缺乏可验证性</tspan>，无法保证逻辑一致性。</text><text x="60" y="205" font-family="Arial, sans-serif" font-size="14" fill="#7F8C8D" font-style="italic">现有方法缺少对 LLM 因果推理输出的形式化验证闭环</text></g>
  <g id="painpoints">
    <g id="pain-1" filter="url(#cs)"><rect x="60" y="240" width="370" height="180" rx="10" fill="#FFFFFF"/><rect x="60" y="240" width="5" height="180" rx="2" fill="#E74C3C"/><circle cx="100" cy="278" r="20" fill="#E74C3C" fill-opacity="0.1"/><text x="100" y="283" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" fill="#E74C3C">🧠</text><text x="130" y="283" font-family="Georgia, SimHei, serif" font-size="20" font-weight="bold" fill="#2C3E50">因果幻觉</text><text x="80" y="315" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D">Causal Hallucination</text><text x="80" y="345" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">LLM 生成的因果关系缺乏逻辑一致性，</text><text x="80" y="365" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">可能包含<tspan fill="#E74C3C" font-weight="bold">无中生有</tspan>的因果链</text><text x="80" y="395" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">如："穿黑衣服"导致"发生车祸"</text></g>
    <g id="pain-2" filter="url(#cs)"><rect x="455" y="240" width="370" height="180" rx="10" fill="#FFFFFF"/><rect x="455" y="240" width="5" height="180" rx="2" fill="#E8B931"/><circle cx="495" cy="278" r="20" fill="#E8B931" fill-opacity="0.1"/><text x="495" y="283" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" fill="#E8B931">🔄</text><text x="525" y="283" font-family="Georgia, SimHei, serif" font-size="20" font-weight="bold" fill="#2C3E50">环路隐患</text><text x="475" y="315" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D">Cycle Hazard</text><text x="475" y="345" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">有向图中出现 A→B→C→A 循环，</text><text x="475" y="365" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">违反<tspan fill="#E8B931" font-weight="bold">DAG 基本约束</tspan></text><text x="475" y="395" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">因果推断的数学基石瞬间坍塌</text></g>
    <g id="pain-3" filter="url(#cs)"><rect x="850" y="240" width="370" height="180" rx="10" fill="#FFFFFF"/><rect x="850" y="240" width="5" height="180" rx="2" fill="#2E86DE"/><circle cx="890" cy="278" r="20" fill="#2E86DE" fill-opacity="0.1"/><text x="890" y="283" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" fill="#2E86DE">⚠️</text><text x="920" y="283" font-family="Georgia, SimHei, serif" font-size="20" font-weight="bold" fill="#2C3E50">风险盲区</text><text x="870" y="315" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D">Risk Blind Spot</text><text x="870" y="345" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">提取出的因果边<tspan fill="#2E86DE" font-weight="bold">无量化风险评估</tspan>，</text><text x="870" y="365" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">无法区分高危与低危路径</text><text x="870" y="395" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">无法指导实际决策优先级</text></g>
  </g>
  <g id="broken-dag" transform="translate(440, 480)"><circle cx="0" cy="0" r="24" fill="none" stroke="#E74C3C" stroke-width="2.5" stroke-dasharray="4,3"/><text x="0" y="6" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#E74C3C" font-weight="bold">A</text><line x1="24" y1="-12" x2="72" y2="-36" stroke="#E74C3C" stroke-width="2.5"/><polygon points="72,-36 64,-30 68,-40" fill="#E74C3C"/><circle cx="96" cy="-36" r="24" fill="none" stroke="#E74C3C" stroke-width="2.5" stroke-dasharray="4,3"/><text x="96" y="-30" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#E74C3C" font-weight="bold">B</text><line x1="120" y1="-24" x2="168" y2="0" stroke="#E74C3C" stroke-width="2.5"/><polygon points="168,0 160,-6 164,8" fill="#E74C3C"/><circle cx="192" cy="0" r="24" fill="none" stroke="#E74C3C" stroke-width="2.5" stroke-dasharray="4,3"/><text x="192" y="6" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#E74C3C" font-weight="bold">C</text><path d="M 168,16 Q 96,56 24,16" fill="none" stroke="#E74C3C" stroke-width="3" stroke-dasharray="8,4"/><polygon points="26,14 18,22 30,22" fill="#E74C3C"/><text x="96" y="60" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#E74C3C" font-weight="bold">环路! DAG 约束违反</text></g>
  <text x="60" y="695" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">03</text><text x="1220" y="695" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">EdgeThemis</text>
</svg>'''

# ============================================================
# Helper: Generate a d-separation case page
# ============================================================
def gen_dsep_page(page_num, case_name, structure_formula, z_status, verdict, verdict_color,
                  rule_num, real_world_title, real_world_desc, ball_trace_lines,
                  explanation, dag_svg):
    """Generate a single d-separation case page."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <defs><filter id="cs" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur in="SourceAlpha" stdDeviation="4"/><feOffset dx="0" dy="2" result="ob"/><feFlood flood-color="#000" flood-opacity="0.06" result="sc"/><feComposite in="sc" in2="ob" operator="in" result="s"/><feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  <rect width="1280" height="720" fill="#FFFFFF"/>
  <g id="header"><rect x="60" y="30" width="5" height="32" rx="2" fill="#1A3C6E"/><text x="78" y="56" font-family="Georgia, SimHei, serif" font-size="28" font-weight="bold" fill="#1A3C6E">d-分离 Case {page_num-7}: {case_name}</text><text x="78" y="76" font-family="Consolas, monospace" font-size="14" fill="#7F8C8D">{structure_formula} · {z_status}</text><line x1="60" y1="88" x2="1220" y2="88" stroke="#D5D8DC" stroke-width="1"/></g>
{stage_indicator("dsep")}
  <!-- DAG Diagram -->
  <g id="dag-diagram" transform="translate(80, 120)">
    {dag_svg}
  </g>
  <!-- Ball Trace -->
  <g id="ball-trace" transform="translate(500, 110)">
    <rect x="0" y="0" width="320" height="250" rx="10" fill="#F5F7FA" stroke="#D5D8DC" stroke-width="1"/>
    <text x="160" y="28" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#1A3C6E" font-weight="bold">贝叶斯球移动轨迹</text>
    <line x1="20" y1="38" x2="300" y2="38" stroke="#D5D8DC" stroke-width="1"/>
    {chr(10).join(f'    <text x="20" y="{60+i*22}" font-family="Consolas, monospace" font-size="13" fill="#2C3E50">{line}</text>' for i, line in enumerate(ball_trace_lines))}
  </g>
  <!-- Verdict -->
  <g id="verdict" transform="translate(850, 110)">
    <rect x="0" y="0" width="370" height="100" rx="10" fill="{verdict_color}" fill-opacity="0.08" stroke="{verdict_color}" stroke-width="1.5"/>
    <text x="185" y="35" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="{verdict_color}" font-weight="bold">判定结果</text>
    <text x="185" y="65" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" fill="{verdict_color}" font-weight="bold">{verdict}</text>
    <text x="185" y="90" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D">对应规则 {rule_num}</text>
  </g>
  <!-- Real World Example -->
  <g id="real-world" filter="url(#cs)">
    <rect x="850" y="230" width="370" height="200" rx="10" fill="#FFFFFF"/>
    <rect x="850" y="230" width="370" height="6" rx="3" fill="{verdict_color}"/>
    <text x="870" y="260" font-family="Georgia, SimHei, serif" font-size="16" fill="{verdict_color}" font-weight="bold">现实案例</text>
    <text x="870" y="285" font-family="Arial, sans-serif" font-size="15" fill="#2C3E50" font-weight="bold">{real_world_title}</text>
    {chr(10).join(f'    <text x="870" y={315+i*24} font-family="Arial, sans-serif" font-size="13" fill="#2C3E50">{line}</text>' for i, line in enumerate(real_world_desc))}
  </g>
  <!-- Explanation -->
  <g id="explanation">
    <rect x="60" y="450" width="1160" height="220" rx="10" fill="#FFFFFF" stroke="#D5D8DC" stroke-width="1"/>
    <rect x="60" y="450" width="1160" height="6" rx="3" fill="#1A3C6E"/>
    <text x="80" y="480" font-family="Georgia, SimHei, serif" font-size="16" fill="#1A3C6E" font-weight="bold">深入理解</text>
    {chr(10).join(f'    <text x="80" y={510+i*24} font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">{line}</text>' for i, line in enumerate(explanation))}
  </g>
  <text x="60" y="695" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">{page_num:02d}</text><text x="1220" y="695" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">EdgeThemis</text>
</svg>'''

# ============================================================
# Generate all pages
# ============================================================
print("Generating EdgeThemis SVG pages...")

# P01
write_svg("01_cover.svg", gen_p01())
# P02
write_svg("02_motivation.svg", gen_p02())
# P03
write_svg("03_problem.svg", gen_p03())

# P04: Contributions (reuse existing with stage indicator)
# Read existing and add stage indicator
import shutil

# For pages 04-14, we'll add stage indicators to existing files
# Let me define the stage for each page
page_stages = {
    "04_contributions.svg": "overview",
    "05_architecture.svg": "overview",
    "06_bayesian_ball.svg": "dsep",
    "07_dsep_cases.svg": "dsep",
    "08_fmea.svg": "fmea",
    "09_reflection.svg": "reflector",
    "10_experiment.svg": "overview",
    "11_ablation.svg": "overview",
    "12_case_study.svg": "overview",
    "13_conclusion.svg": "overview",
    "14_qa.svg": "overview",
}

# For now, let me generate the 6 d-separation case pages (P08-P13)
# and shift existing pages accordingly

# Actually, let me restructure completely. New page order:
# P01: Cover
# P02: Motivation
# P03: Problem
# P04: Contributions
# P05: Architecture
# P06: Bayes Ball overview
# P07: Case 1 - Chain + observed
# P08: Case 2 - Chain + unobserved
# P09: Case 3 - Fork + observed
# P10: Case 4 - Fork + unobserved
# P11: Case 5 - Collider + observed
# P12: Case 6 - Collider + unobserved
# P13: FMEA
# P14: Reflection
# P15: Experiment
# P16: Ablation
# P17: Case Study
# P18: Conclusion
# P19: Q&A

# That's 19 pages. Let me just define them all.

print("Done! (P01-P03 generated, remaining pages need manual SVG creation)")
print("Total pages: 19")
