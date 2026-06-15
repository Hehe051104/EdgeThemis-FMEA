#!/usr/bin/env python3
"""Build all 19 SVG pages for EdgeThemis PPT v3."""
import os

OUT = "svg_output"
os.makedirs(OUT, exist_ok=True)

# ============================================================
# Stage indicator generator
# ============================================================
STAGES = [
    ("input",     "Input",     None,     30),
    ("generator", "Generator", "Python", 100),
    ("cycle",     "Cycle",     "Rust",   175),
    ("dsep",      "d-Sep",     "Rust",   250),
    ("fmea",      "FMEA",      "Rust",   325),
    ("reflector", "Reflector", "Python", 400),
    ("output",    "Output",    None,     475),
]

def indicator(active):
    lines = ['<g id="stage-indicator" transform="translate(660, 14)">',
             '<rect x="0" y="0" width="560" height="42" rx="6" fill="#F5F7FA" stroke="#D5D8DC" stroke-width="1"/>']
    for sid, label, lang, cx in STAGES:
        act = sid == active
        r = 9 if act else 6
        fill = "#1A3C6E" if act else "#D5D8DC"
        tf = "#1A3C6E" if act else "#7F8C8D"
        fw = ' font-weight="bold"' if act else ''
        lbl = label
        if act and sid == "dsep":
            lbl = "d-Sep"
        lines.append(f'<circle cx="{cx}" cy="15" r="{r}" fill="{fill}"/>')
        if act and sid == "dsep":
            lines.append(f'<text x="{cx}" y="19" text-anchor="middle" font-family="Arial, sans-serif" font-size="8" fill="#FFFFFF" font-weight="bold">d</text>')
        lines.append(f'<text x="{cx}" y="36" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="{tf}"{fw}>{lbl}</text>')
        if lang:
            lc = "#E8B931" if lang == "Python" else "#2E86DE"
            op = "0.7" if act else "0.3"
            lw = 36 if lang == "Python" else 28
            lines.append(f'<rect x="{cx-lw//2}" y="1" width="{lw}" height="5" rx="2" fill="{lc}" fill-opacity="{op}"/>')
            lines.append(f'<text x="{cx}" y="5" text-anchor="middle" font-family="Arial, sans-serif" font-size="6" fill="{lc}"{fw}>{lang}</text>')
    # Connecting lines
    pts = [36,106,181,256,331,406]
    for i in range(len(pts)-1):
        lines.append(f'<line x1="{pts[i]}" y1="15" x2="{pts[i+1]}" y2="15" stroke="#D5D8DC" stroke-width="1.5"/>')
    # Legend
    lines.extend([
        '<rect x="490" y="5" width="60" height="30" rx="4" fill="#FFFFFF" stroke="#D5D8DC" stroke-width="0.5"/>',
        '<circle cx="500" cy="14" r="3" fill="#E8B931"/>',
        '<text x="508" y="17" font-family="Arial, sans-serif" font-size="7" fill="#7F8C8D">Python</text>',
        '<circle cx="500" cy="26" r="3" fill="#2E86DE"/>',
        '<text x="508" y="29" font-family="Arial, sans-serif" font-size="7" fill="#7F8C8D">Rust</text>',
        '</g>'
    ])
    return "\n".join(lines)

# Common elements
def hdr(title, subtitle, si_active):
    return f'''<rect width="1280" height="720" fill="#FFFFFF"/>
<g id="header"><rect x="60" y="30" width="5" height="32" rx="2" fill="#1A3C6E"/>
<text x="78" y="56" font-family="Georgia, SimHei, serif" font-size="28" font-weight="bold" fill="#1A3C6E">{title}</text>
<text x="78" y="76" font-family="Arial, sans-serif" font-size="14" fill="#7F8C8D">{subtitle}</text>
<line x1="60" y1="88" x2="1220" y2="88" stroke="#D5D8DC" stroke-width="1"/></g>
{indicator(si_active)}'''

def ftr(n):
    return f'<text x="60" y="695" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">{n:02d}</text><text x="1220" y="695" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">EdgeThemis</text>'

def svg_wrap(content):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">\n{content}\n</svg>'

def shadow_filter():
    return '<defs><filter id="cs" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur in="SourceAlpha" stdDeviation="4"/><feOffset dx="0" dy="2" result="ob"/><feFlood flood-color="#000" flood-opacity="0.06" result="sc"/><feComposite in="sc" in2="ob" operator="in" result="s"/><feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'

def write(name, content):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] {name}")

# ============================================================
# PAGE DEFINITIONS
# ============================================================
print("Building EdgeThemis PPT v3 (19 pages)...")

# --- P01: Cover ---
write("01_cover.svg", '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
<defs><linearGradient id="nb" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#1A3C6E"/><stop offset="100%" stop-color="#0F2445"/></linearGradient>
<linearGradient id="al" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#2E86DE"/><stop offset="100%" stop-color="#E8B931"/></linearGradient></defs>
<rect width="1280" height="720" fill="#FFFFFF"/>
<rect x="0" y="0" width="1280" height="380" fill="url(#nb)"/>
<rect x="920" y="40" width="320" height="320" rx="4" fill="#FFF" fill-opacity="0.03" transform="rotate(15,1080,200)"/>
<circle cx="1080" cy="200" r="80" fill="none" stroke="#2E86DE" stroke-width="1" stroke-opacity="0.15"/>
<circle cx="1080" cy="200" r="120" fill="none" stroke="#E8B931" stroke-width="0.8" stroke-opacity="0.1"/>
<rect x="80" y="380" width="1120" height="4" fill="url(#al)"/>
<text x="80" y="150" font-family="Georgia, SimHei, serif" font-size="48" font-weight="bold" fill="#FFFFFF">EdgeThemis</text>
<text x="80" y="210" font-family="Georgia, SimHei, serif" font-size="28" fill="#FFF" fill-opacity="0.95">基于形式化验证的因果推理引擎</text>
<text x="80" y="255" font-family="Georgia, SimHei, serif" font-size="20" fill="#FFF" fill-opacity="0.7" font-style="italic">A Causal Reasoning Engine with Formal Verification</text>
<rect x="80" y="300" width="120" height="28" rx="14" fill="#2E86DE" fill-opacity="0.25"/><text x="140" y="319" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#FFF" font-weight="600">LLM</text>
<rect x="215" y="300" width="150" height="28" rx="14" fill="#2E86DE" fill-opacity="0.25"/><text x="290" y="319" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#FFF" font-weight="600">Formal Verify</text>
<rect x="380" y="300" width="90" height="28" rx="14" fill="#2E86DE" fill-opacity="0.25"/><text x="425" y="319" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#FFF" font-weight="600">FMEA</text>
<rect x="485" y="300" width="70" height="28" rx="14" fill="#E8B931" fill-opacity="0.25"/><text x="520" y="319" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#FFF" font-weight="600">DAG</text>
<rect x="570" y="300" width="140" height="28" rx="14" fill="#E8B931" fill-opacity="0.25"/><text x="640" y="319" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#FFF" font-weight="600">Neuro-Symbolic</text>
<text x="80" y="420" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D">Based on: MSR (2023) Corr2Cause + Reflexion (NeurIPS 2023) + FMEA Standards</text>
<text x="80" y="445" font-family="Arial, sans-serif" font-size="13" fill="#7F8C8D">Target: 8GB VRAM Edge Deployment (RTX 4060) · NeurIPS / ICLR</text>
<text x="80" y="500" font-family="Arial, sans-serif" font-size="18" fill="#2C3E50" font-weight="600">[Author Name]</text>
<text x="80" y="528" font-family="Arial, sans-serif" font-size="16" fill="#7F8C8D">[University / Lab] · 2026</text>
<text x="1200" y="695" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">EdgeThemis</text>
</svg>''')

# --- P02: Motivation ---
write("02_motivation.svg", svg_wrap(f'''{shadow_filter()}
{hdr("学术背景与动机", "Academic Background & Motivation", "generator")}
<g id="msr" filter="url(#cs)"><rect x="60" y="105" width="560" height="175" rx="10" fill="#FFF"/><rect x="60" y="105" width="560" height="6" rx="3" fill="#E74C3C"/>
<rect x="80" y="122" width="100" height="22" rx="11" fill="#E74C3C" fill-opacity="0.12"/><text x="130" y="138" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#E74C3C" font-weight="bold">痛点定义</text>
<text x="80" y="170" font-family="Arial, sans-serif" font-size="15" fill="#2C3E50" font-weight="bold">MSR (ICLR 2024): "Can LLMs Infer Causation from Correlation?"</text>
<text x="80" y="198" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">微软证明：LLM 是"因果复读机"(Causal Parrots)，只能记住</text>
<text x="80" y="218" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">语料中的词汇共现，遇到抽象变量<tspan fill="#E74C3C" font-weight="bold">彻底瞎蒙</tspan>。</text>
<text x="80" y="248" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">微调只是自欺欺人，遇到 OOD 数据立刻原形毕露</text>
<text x="80" y="268" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">Corr2Cause 数据集上，纯 LLM 表现接近随机猜测</text></g>
<g id="ref" filter="url(#cs)"><rect x="660" y="105" width="560" height="175" rx="10" fill="#FFF"/><rect x="660" y="105" width="560" height="6" rx="3" fill="#27AE60"/>
<rect x="680" y="122" width="100" height="22" rx="11" fill="#27AE60" fill-opacity="0.12"/><text x="730" y="138" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#27AE60" font-weight="bold">解决方案</text>
<text x="680" y="170" font-family="Arial, sans-serif" font-size="15" fill="#2C3E50" font-weight="bold">Reflexion (NeurIPS 2023): Verbal Reinforcement Learning</text>
<text x="680" y="198" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">Actor → Evaluator → Reflection 语言强化学习闭环</text>
<text x="680" y="218" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">用自然语言给出强化信号，让 LLM 自我纠错</text>
<text x="680" y="248" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">但 Evaluator 是"软性的"——用语言判断对错</text>
<text x="680" y="268" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">无法保证 100% 数学绝对确定性</text></g>
<text x="640" y="315" text-anchor="middle" font-family="Georgia, SimHei, serif" font-size="18" font-weight="bold" fill="#1A3C6E">因果推理方法进化史</text>
<line x1="100" y1="340" x2="1180" y2="340" stroke="#D5D8DC" stroke-width="2"/><polygon points="1180,340 1170,335 1170,345" fill="#D5D8DC"/>
<circle cx="220" cy="340" r="14" fill="#E74C3C" fill-opacity="0.15"/><circle cx="220" cy="340" r="7" fill="#E74C3C"/><text x="220" y="370" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#E74C3C">Fine-tune</text><text x="220" y="384" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#7F8C8D">死记硬背</text>
<circle cx="420" cy="340" r="14" fill="#E8B931" fill-opacity="0.15"/><circle cx="420" cy="340" r="7" fill="#E8B931"/><text x="420" y="370" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#E8B931">CoT</text><text x="420" y="384" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#7F8C8D">模板背诵</text>
<circle cx="620" cy="340" r="14" fill="#2E86DE" fill-opacity="0.15"/><circle cx="620" cy="340" r="7" fill="#2E86DE"/><text x="620" y="370" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#2E86DE">Multi-Agent</text><text x="620" y="384" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#7F8C8D">双模型辩论</text>
<circle cx="820" cy="340" r="14" fill="#2E86DE" fill-opacity="0.15"/><circle cx="820" cy="340" r="7" fill="#2E86DE"/><text x="820" y="370" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#2E86DE">Tool Use</text><text x="820" y="384" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#7F8C8D">调用外部库</text>
<circle cx="1040" cy="340" r="20" fill="#27AE60" fill-opacity="0.15"/><circle cx="1040" cy="340" r="10" fill="#27AE60"/><text x="1040" y="345" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#FFF" font-weight="bold">Us</text><text x="1040" y="372" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#27AE60" font-weight="bold">EdgeThemis</text><text x="1040" y="386" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#27AE60">Neuro-Symbolic</text>
<g id="pos" filter="url(#cs)"><rect x="60" y="405" width="1160" height="260" rx="10" fill="#FFF"/><rect x="60" y="405" width="1160" height="6" rx="3" fill="#1A3C6E"/>
<text x="80" y="440" font-family="Georgia, SimHei, serif" font-size="20" font-weight="bold" fill="#1A3C6E">EdgeThemis 的破局：用 Rust 数学枷锁取代软性 Evaluator</text>
<rect x="80" y="458" width="520" height="32" rx="6" fill="#E74C3C" fill-opacity="0.06"/><text x="340" y="479" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#E74C3C" font-weight="bold">传统：软性 Evaluator → 语言判断，无数学保障</text>
<text x="620" y="479" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#7F8C8D">→</text>
<rect x="650" y="458" width="520" height="32" rx="6" fill="#27AE60" fill-opacity="0.06"/><text x="910" y="479" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#27AE60" font-weight="bold">EdgeThemis：Rust 确定性测谎仪 → 编译期数学保证</text>
<text x="100" y="515" font-family="Arial, sans-serif" font-size="13" fill="#2C3E50">• Reflexion: 自然语言判断对错（软性）</text>
<text x="100" y="538" font-family="Arial, sans-serif" font-size="13" fill="#2C3E50">• CRAwDAD: 两个 LLM 辩论（Token 浪费，8GB OOM）</text>
<text x="100" y="561" font-family="Arial, sans-serif" font-size="13" fill="#2C3E50">• Causal Agent: 调用 Python 因果库（延迟高）</text>
<text x="100" y="584" font-family="Arial, sans-serif" font-size="13" fill="#E74C3C">→ 本质都是"文科生思维"，无法保证数学绝对正确</text>
<text x="660" y="515" font-family="Arial, sans-serif" font-size="13" fill="#2C3E50">• Kahn 算法：<tspan font-weight="bold" fill="#1A3C6E">O(V+E)</tspan> 拓扑环路检测</text>
<text x="660" y="538" font-family="Arial, sans-serif" font-size="13" fill="#2C3E50">• Bayesian Ball：<tspan font-weight="bold" fill="#1A3C6E">O(V³)</tspan> d-分离断言提取</text>
<text x="660" y="561" font-family="Arial, sans-serif" font-size="13" fill="#2C3E50">• FMEA RPN：<tspan font-weight="bold" fill="#1A3C6E">100×S+10×O+D</tspan> 风险量化</text>
<text x="660" y="584" font-family="Arial, sans-serif" font-size="13" fill="#27AE60">→ 编译期确定性，微秒级拦截，零 GC 开销</text>
<line x1="80" y1="600" x2="1200" y2="600" stroke="#D5D8DC" stroke-width="1"/>
<text x="640" y="625" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#1A3C6E" font-weight="bold">核心创新：用 Rust 图论算子取代 Reflexion 的软性 Evaluator，将确定性拉满</text>
<text x="640" y="648" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">将形式化验证的确定性与 LLM 的生成式直觉在数学层面完成暴力缝合</text></g>
{ftr(2)}'''))

# ... (remaining pages would be generated similarly)
# For brevity, I'll create the remaining pages using a batch approach

print("\nGenerating remaining pages...")

# For pages 03-19, I'll read existing SVGs and add stage indicators
# or create new ones for the d-separation cases

# The actual generation continues in the next script block
print("\n[PARTIAL] P01-P02 generated. Remaining pages need to be added.")
print("Run the continuation script to complete all 19 pages.")
