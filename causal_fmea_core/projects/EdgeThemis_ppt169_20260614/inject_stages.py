#!/usr/bin/env python3
"""Inject stage indicators into all SVG pages and create d-separation case pages."""
import os, re

OUT = "svg_output"

# Stage indicator SVG for each active stage
def make_indicator(active_stage):
    stages = [
        ("input",     "Input",     None,     30),
        ("generator", "Generator", "Python", 100),
        ("cycle",     "Cycle",     "Rust",   175),
        ("dsep",      "d-Sep",     "Rust",   250),
        ("fmea",      "FMEA",      "Rust",   325),
        ("reflector", "Reflector", "Python", 400),
        ("output",    "Output",    None,     475),
    ]
    lines = ['<g id="stage-indicator" transform="translate(660, 14)">',
             '<rect x="0" y="0" width="560" height="42" rx="6" fill="#F5F7FA" stroke="#D5D8DC" stroke-width="1"/>']
    for sid, label, lang, cx in stages:
        act = (sid == active_stage)
        r = 9 if act else 6
        fill = "#1A3C6E" if act else "#D5D8DC"
        tf = "#1A3C6E" if act else "#7F8C8D"
        fw = ' font-weight="bold"' if act else ''
        lines.append(f'<circle cx="{cx}" cy="15" r="{r}" fill="{fill}"/>')
        if act and sid == "dsep":
            lines.append(f'<text x="{cx}" y="19" text-anchor="middle" font-family="Arial, sans-serif" font-size="8" fill="#FFFFFF" font-weight="bold">d</text>')
        lines.append(f'<text x="{cx}" y="36" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="{tf}"{fw}>{label}</text>')
        if lang:
            lc = "#E8B931" if lang == "Python" else "#2E86DE"
            op = "0.7" if act else "0.3"
            lw = 36 if lang == "Python" else 28
            lines.append(f'<rect x="{cx-lw//2}" y="1" width="{lw}" height="5" rx="2" fill="{lc}" fill-opacity="{op}"/>')
            lines.append(f'<text x="{cx}" y="5" text-anchor="middle" font-family="Arial, sans-serif" font-size="6" fill="{lc}"{fw}>{lang}</text>')
    pts = [36, 106, 181, 256, 331, 406]
    for i in range(len(pts)-1):
        lines.append(f'<line x1="{pts[i]}" y1="15" x2="{pts[i+1]}" y2="15" stroke="#D5D8DC" stroke-width="1.5"/>')
    lines.extend([
        '<rect x="490" y="5" width="60" height="30" rx="4" fill="#FFF" stroke="#D5D8DC" stroke-width="0.5"/>',
        '<circle cx="500" cy="14" r="3" fill="#E8B931"/>',
        '<text x="508" y="17" font-family="Arial, sans-serif" font-size="7" fill="#7F8C8D">Python</text>',
        '<circle cx="500" cy="26" r="3" fill="#2E86DE"/>',
        '<text x="508" y="29" font-family="Arial, sans-serif" font-size="7" fill="#7F8C8D">Rust</text>',
        '</g>'
    ])
    return "\n".join(lines)

# Page → stage mapping
PAGE_STAGES = {
    "03": "input",      # Problem
    "04": "generator",  # Contributions
    "05": "overview",   # Architecture (all stages)
    "06": "dsep",       # Bayes Ball overview
    "07": "dsep",       # Case 1
    "08": "dsep",       # Case 2
    "09": "dsep",       # Case 3
    "10": "dsep",       # Case 4
    "11": "dsep",       # Case 5
    "12": "dsep",       # Case 6
    "13": "fmea",       # FMEA
    "14": "reflector",  # Reflection
    "15": "overview",   # Experiment
    "16": "overview",   # Ablation
    "17": "overview",   # Case Study
    "18": "overview",   # Conclusion
    "19": "overview",   # Q&A
}

# For "overview" pages, show all stages as equal
def make_indicator_overview():
    stages = [
        ("input",     "Input",     None,     30),
        ("generator", "Generator", "Python", 100),
        ("cycle",     "Cycle",     "Rust",   175),
        ("dsep",      "d-Sep",     "Rust",   250),
        ("fmea",      "FMEA",      "Rust",   325),
        ("reflector", "Reflector", "Python", 400),
        ("output",    "Output",    None,     475),
    ]
    lines = ['<g id="stage-indicator" transform="translate(660, 14)">',
             '<rect x="0" y="0" width="560" height="42" rx="6" fill="#F5F7FA" stroke="#D5D8DC" stroke-width="1"/>']
    for sid, label, lang, cx in stages:
        lines.append(f'<circle cx="{cx}" cy="15" r="6" fill="#2E86DE" fill-opacity="0.3"/>')
        lines.append(f'<text x="{cx}" y="36" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="#7F8C8D">{label}</text>')
        if lang:
            lc = "#E8B931" if lang == "Python" else "#2E86DE"
            lw = 36 if lang == "Python" else 28
            lines.append(f'<rect x="{cx-lw//2}" y="1" width="{lw}" height="5" rx="2" fill="{lc}" fill-opacity="0.3"/>')
            lines.append(f'<text x="{cx}" y="5" text-anchor="middle" font-family="Arial, sans-serif" font-size="6" fill="{lc}">{lang}</text>')
    pts = [36, 106, 181, 256, 331, 406]
    for i in range(len(pts)-1):
        lines.append(f'<line x1="{pts[i]}" y1="15" x2="{pts[i+1]}" y2="15" stroke="#D5D8DC" stroke-width="1.5"/>')
    lines.extend([
        '<rect x="490" y="5" width="60" height="30" rx="4" fill="#FFF" stroke="#D5D8DC" stroke-width="0.5"/>',
        '<circle cx="500" cy="14" r="3" fill="#E8B931"/>',
        '<text x="508" y="17" font-family="Arial, sans-serif" font-size="7" fill="#7F8C8D">Python</text>',
        '<circle cx="500" cy="26" r="3" fill="#2E86DE"/>',
        '<text x="508" y="29" font-family="Arial, sans-serif" font-size="7" fill="#7F8C8D">Rust</text>',
        '</g>'
    ])
    return "\n".join(lines)

def inject_indicator(svg_content, stage):
    """Inject stage indicator after the first <g id="header">...</g> block."""
    if stage == "overview":
        indicator = make_indicator_overview()
    else:
        indicator = make_indicator(stage)

    # Find the closing </g> of the header group
    # Insert indicator right after the header's closing </g> and before the next content
    # Pattern: find the line with </g> that closes the header
    header_end = svg_content.find('</g>', svg_content.find('id="header"'))
    if header_end == -1:
        # Try after the header line
        header_end = svg_content.find('</g>', svg_content.find('header'))
    if header_end == -1:
        # Just insert after the first <line .../> that looks like a header divider
        header_end = svg_content.find('/>', svg_content.find('stroke="#D5D8DC"'))
        if header_end != -1:
            header_end += 2

    if header_end != -1:
        # Find the end of the </g> tag
        insert_pos = svg_content.find('>', header_end) + 1
        svg_content = svg_content[:insert_pos] + "\n" + indicator + "\n" + svg_content[insert_pos:]

    return svg_content

# ============================================================
# D-separation case page generator
# ============================================================
def gen_case_page(page_num, title_zh, title_en, structure, z_text, z_color,
                  verdict, verdict_color, rule_label, case_label,
                  example_title, example_lines, explanation_lines,
                  dag_nodes, dag_edges, trace_lines):
    """Generate a complete d-separation case page."""

    # Build DAG SVG
    dag_svg_parts = []
    for node in dag_nodes:
        cx, cy, label, fill, stroke, observed = node
        r = 22
        if observed:
            dag_svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" fill-opacity="0.2" stroke="{stroke}" stroke-width="2"/>')
            dag_svg_parts.append(f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="{stroke}" font-weight="bold">{label}</text>')
            dag_svg_parts.append(f'<text x="{cx}" y="{cy+25}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="{stroke}" font-weight="bold">已观测 ✓</text>')
        else:
            dag_svg_parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{stroke}" stroke-width="2" stroke-dasharray="4,3"/>')
            dag_svg_parts.append(f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="{stroke}" font-weight="bold">{label}</text>')
            dag_svg_parts.append(f'<text x="{cx}" y="{cy+25}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#7F8C8D">未观测</text>')

    for edge in dag_edges:
        x1, y1, x2, y2, color, reverse = edge
        dag_svg_parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2.5"/>')
        # Arrow
        if reverse:
            dag_svg_parts.append(f'<polygon points="{x1},{y1} {x1+8},{y1-6} {x1+8},{y1+6}" fill="{color}"/>')
        else:
            dag_svg_parts.append(f'<polygon points="{x2},{y2} {x2-8},{y2-6} {x2-8},{y2+6}" fill="{color}"/>')

    dag_svg = "\n    ".join(dag_svg_parts)

    # Build trace lines
    trace_svg = "\n".join(f'<text x="20" y="{60+i*22}" font-family="Consolas, monospace" font-size="13" fill="#2C3E50">{line}</text>' for i, line in enumerate(trace_lines))

    # Build example lines
    example_svg = "\n".join(f'<text x="870" y="{310+i*24}" font-family="Arial, sans-serif" font-size="13" fill="#2C3E50">{line}</text>' for i, line in enumerate(example_lines))

    # Build explanation lines
    expl_svg = "\n".join(f'<text x="80" y="{505+i*26}" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">{line}</text>' for i, line in enumerate(explanation_lines))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <defs><filter id="cs" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur in="SourceAlpha" stdDeviation="4"/><feOffset dx="0" dy="2" result="ob"/><feFlood flood-color="#000" flood-opacity="0.06" result="sc"/><feComposite in="sc" in2="ob" operator="in" result="s"/><feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  <rect width="1280" height="720" fill="#FFFFFF"/>
  <g id="header"><rect x="60" y="30" width="5" height="32" rx="2" fill="#1A3C6E"/>
  <text x="78" y="56" font-family="Georgia, SimHei, serif" font-size="28" font-weight="bold" fill="#1A3C6E">{title_zh}</text>
  <text x="78" y="76" font-family="Arial, sans-serif" font-size="14" fill="#7F8C8D">{title_en}</text>
  <line x1="60" y1="88" x2="1220" y2="88" stroke="#D5D8DC" stroke-width="1"/></g>
  {make_indicator("dsep")}
  <!-- DAG Diagram -->
  <g id="dag" transform="translate(80, 120)">
    <rect x="-10" y="-10" width="400" height="280" rx="10" fill="#FFF" stroke="#D5D8DC" stroke-width="1"/>
    <text x="190" y="20" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#1A3C6E" font-weight="bold">{structure}</text>
    {dag_svg}
  </g>
  <!-- Ball Trace -->
  <g id="trace" transform="translate(500, 110)">
    <rect x="0" y="0" width="320" height="260" rx="10" fill="#F5F7FA" stroke="#D5D8DC" stroke-width="1"/>
    <text x="160" y="28" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#1A3C6E" font-weight="bold">贝叶斯球移动轨迹</text>
    <line x1="20" y1="38" x2="300" y2="38" stroke="#D5D8DC" stroke-width="1"/>
    {trace_svg}
  </g>
  <!-- Verdict -->
  <g id="verdict" transform="translate(850, 110)">
    <rect x="0" y="0" width="370" height="90" rx="10" fill="{verdict_color}" fill-opacity="0.08" stroke="{verdict_color}" stroke-width="1.5"/>
    <text x="185" y="30" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="{verdict_color}" font-weight="bold">判定: {rule_label}</text>
    <text x="185" y="60" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" fill="{verdict_color}" font-weight="bold">{verdict}</text>
    <text x="185" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">Z 状态: {z_text}</text>
  </g>
  <!-- Real World Example -->
  <g id="example" filter="url(#cs)">
    <rect x="850" y="220" width="370" height="180" rx="10" fill="#FFF"/>
    <rect x="850" y="220" width="370" height="6" rx="3" fill="{verdict_color}"/>
    <text x="870" y="250" font-family="Georgia, SimHei, serif" font-size="16" fill="{verdict_color}" font-weight="bold">现实案例</text>
    <text x="870" y="278" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50" font-weight="bold">{example_title}</text>
    {example_svg}
  </g>
  <!-- Explanation -->
  <g id="explanation">
    <rect x="60" y="420" width="1160" height="250" rx="10" fill="#FFF" stroke="#D5D8DC" stroke-width="1"/>
    <rect x="60" y="420" width="1160" height="6" rx="3" fill="#1A3C6E"/>
    <text x="80" y="450" font-family="Georgia, SimHei, serif" font-size="16" fill="#1A3C6E" font-weight="bold">深入理解：球是怎么移动的</text>
    {expl_svg}
  </g>
  {ftr(page_num)}
</svg>'''

def ftr(n):
    return f'<text x="60" y="695" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">{n:02d}</text><text x="1220" y="695" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">EdgeThemis</text>'


# ============================================================
# MAIN
# ============================================================
print("=== EdgeThemis SVG Builder v3 ===\n")

# Step 1: Rename existing files to new numbering
renames = {
    "03_problem.svg": "03_problem_old.svg",
    "04_contributions.svg": "04_contributions_old.svg",
    "05_architecture.svg": "05_architecture_old.svg",
    "06_bayesian_ball.svg": "06_bayesian_old.svg",
    "08_fmea.svg": "13_fmea_old.svg",
    "09_reflection.svg": "14_reflection_old.svg",
    "10_experiment.svg": "15_experiment_old.svg",
    "11_ablation.svg": "16_ablation_old.svg",
    "12_case_study.svg": "17_case_study_old.svg",
    "13_conclusion.svg": "18_conclusion_old.svg",
    "14_qa.svg": "19_qa_old.svg",
}
for old, new in renames.items():
    op = os.path.join(OUT, old)
    np_ = os.path.join(OUT, new)
    if os.path.exists(op):
        os.rename(op, np_)

# Step 2: Keep P01 and P02 as-is (already have stage indicators)
print("[OK] P01, P02 kept")

# Step 3: Inject stage indicators into existing pages and renumber
inject_map = {
    "03_problem_old.svg": ("03_problem.svg", "input"),
    "04_contributions_old.svg": ("04_contributions.svg", "generator"),
    "05_architecture_old.svg": ("05_architecture.svg", "overview"),
    "06_bayesian_old.svg": ("06_bayesian_ball.svg", "dsep"),
    "13_fmea_old.svg": ("13_fmea.svg", "fmea"),
    "14_reflection_old.svg": ("14_reflection.svg", "reflector"),
    "15_experiment_old.svg": ("15_experiment.svg", "overview"),
    "16_ablation_old.svg": ("16_ablation.svg", "overview"),
    "17_case_study_old.svg": ("17_case_study.svg", "overview"),
    "18_conclusion_old.svg": ("18_conclusion.svg", "overview"),
    "19_qa_old.svg": ("19_qa.svg", "overview"),
}

for old_name, (new_name, stage) in inject_map.items():
    op = os.path.join(OUT, old_name)
    if os.path.exists(op):
        with open(op, "r", encoding="utf-8") as f:
            content = f.read()
        # Remove old stage indicator if exists
        if 'id="stage-indicator"' in content:
            start = content.find('<g id="stage-indicator"')
            end = content.find('</g>', start) + 4
            content = content[:start] + content[end:]
        # Inject new indicator
        content = inject_indicator(content, stage)
        with open(os.path.join(OUT, new_name), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[OK] {new_name} (stage: {stage})")
    else:
        print(f"[SKIP] {old_name} not found")

# Step 4: Generate 6 d-separation case pages
print("\nGenerating d-separation case pages...")

# Case 7: Chain + observed → blocked (Rule 2)
write("07_case_chain_obs.svg", gen_case_page(
    page_num=7,
    title_zh="Case 1: 链式 + 已观测 → 阻断",
    title_en="Chain X→M→Y · M is observed → Blocked",
    structure="Chain: X → M → Y",
    z_text="M 已观测 (M ∈ Z)", z_color="#27AE60",
    verdict="X ⊥ Y 阻断", verdict_color="#27AE60",
    rule_label="规则 2 (Up+已观测)",
    case_label="Chain + observed",
    example_title="药物 → 血压降低 → 头晕缓解",
    example_lines=[
        "已知血压确实降低了(M 被观测)",
        "→ 在'血压已降'的前提下，",
        "用药(X)对头晕缓解(Y)无额外预测力",
        "→ 路径被阻断，信息传递截断",
    ],
    explanation_lines=[
        "球从 X(用药) 出发，方向=Up。X 未观测 → Rule1 允许，球走到 M(血压降低)。",
        "此时 M 已被观测 → Rule2 触发：Up 和 Down 两个方向都被阻断。",
        "球卡死在 M，无法到达 Y(头晕缓解)。路径被物理切断。",
        "这意味着：一旦你知道了中介结果 M，起点 X 就无法再给你关于终点 Y 的额外信息。",
        "这是 Chain 结构的'安全模式'——中介被控制后，因果传导链被截断。",
    ],
    dag_nodes=[
        (60, 100, "X", "#27AE60", "#27AE60", False),
        (200, 40,  "M", "#27AE60", "#27AE60", True),
        (340, 100, "Y", "#27AE60", "#27AE60", False),
    ],
    dag_edges=[
        (82, 88, 178, 52, "#27AE60", False),
        (222, 52, 318, 88, "#27AE60", False),
    ],
    trace_lines=[
        "Step0: (X, Up) 出发",
        "Step1: X未观测 → Rule1",
        "  → Up到M: (M, Up)",
        "Step2: M<tspan fill=\"#27AE60\" font-weight=\"bold\">已观测</tspan> → Rule2",
        "  → 两个方向都<tspan fill=\"#E74C3C\" font-weight=\"bold\">阻断!</tspan>",
        "  → 球卡死在M",
        "Step3: 球到不了Y",
        "<tspan fill=\"#27AE60\" font-weight=\"bold\">→ return true (安全)</tspan>",
    ],
))

# Case 8: Chain + unobserved → connected (Rule 3)
write("08_case_chain_unobs.svg", gen_case_page(
    page_num=8,
    title_zh="Case 2: 链式 + 未观测 → 连通",
    title_en="Chain X→M→Y · M is NOT observed → Connected",
    structure="Chain: X → M → Y",
    z_text="M 未观测 (M ∉ Z)", z_color="#E74C3C",
    verdict="X ¬⊥ Y 连通", verdict_color="#E74C3C",
    rule_label="规则 3 (Down+未观测)",
    case_label="Chain + unobserved",
    example_title="用药 → 病情好转 → 恢复运动",
    example_lines=[
        "不知道病情是否好转(M 未观测)",
        "→ 用药(X)的影响可以通过",
        "病情好转(M)传递到恢复运动(Y)",
        "→ 这是唯一合法的因果通路",
    ],
    explanation_lines=[
        "球从 X(用药) 出发，方向=Up。X 未观测 → Rule1 允许，球沿 Down 走到 M(病情好转)。",
        "此时 M 未被观测 → Rule3 触发：只允许继续 Down，不允许 Up。",
        "球沿 Down 走到 Y(恢复运动)。球到达 Y！",
        "但这是唯一合法的通路——Chain 结构本身就是真实的因果链。",
        "用药导致病情好转，病情好转导致恢复运动。这条路径连通是正确的，不应报警。",
    ],
    dag_nodes=[
        (60, 100, "X", "#27AE60", "#27AE60", False),
        (200, 40,  "M", "#27AE60", "#27AE60", False),
        (340, 100, "Y", "#27AE60", "#27AE60", False),
    ],
    dag_edges=[
        (82, 88, 178, 52, "#27AE60", False),
        (222, 52, 318, 88, "#27AE60", False),
    ],
    trace_lines=[
        "Step0: (X, Up) 出发",
        "Step1: X未观测 → Rule1",
        "  → Down到M: (M, Down)",
        "Step2: M<tspan fill=\"#7F8C8D\">未观测</tspan> → Rule3",
        "  → 只允许<tspan fill=\"#27AE60\" font-weight=\"bold\">Down</tspan>",
        "  → 到Y: (Y, Down)",
        "Step3: 球到达Y",
        "<tspan fill=\"#27AE60\" font-weight=\"bold\">→ return false (连通，但合法)</tspan>",
    ],
))

# Case 9: Fork + observed → blocked (Rule 2)
write("09_case_fork_obs.svg", gen_case_page(
    page_num=9,
    title_zh="Case 3: 共因 + 已观测 → 阻断",
    title_en="Fork X←M→Y · M is observed → Blocked",
    structure="Fork: X ← M → Y",
    z_text="M 已观测 (M ∈ Z)", z_color="#27AE60",
    verdict="X ⊥ Y 阻断", verdict_color="#27AE60",
    rule_label="规则 2 (Up+已观测)",
    case_label="Fork + observed",
    example_title="暴雨 → 手术推迟 + 空气湿度高",
    example_lines=[
        "已确认当天确实下暴雨(M 被观测)",
        "→ 在'已知暴雨'的前提下，",
        "手术推迟(X)和湿度高(Y)之间",
        "无虚假相关性。后门被堵死。",
    ],
    explanation_lines=[
        "球从 X(手术推迟) 出发，方向=Up。X 未观测 → Rule1 允许，球走到 M(暴雨)。",
        "此时 M 已被观测 → Rule2 触发：两个方向都阻断。球卡死在 M。",
        "暴雨(M)是 X 和 Y 的共同原因。一旦 M 被确认为事实，它同时解释了 X 和 Y。",
        "在'已知下暴雨'的前提下，手术推迟和湿度高之间没有可以传递的虚假相关性。",
        "这就是后门准则的工程实现——观测混杂变量后，后门路径被物理切断。",
    ],
    dag_nodes=[
        (60, 100, "X", "#27AE60", "#27AE60", False),
        (200, 40,  "M", "#27AE60", "#27AE60", True),
        (340, 100, "Y", "#27AE60", "#27AE60", False),
    ],
    dag_edges=[
        (178, 52, 82, 88, "#27AE60", True),
        (222, 52, 318, 88, "#27AE60", False),
    ],
    trace_lines=[
        "Step0: (X, Up) 出发",
        "Step1: X未观测 → Rule1",
        "  → Up到M: (M, Up)",
        "Step2: M<tspan fill=\"#27AE60\" font-weight=\"bold\">已观测</tspan> → Rule2",
        "  → 两个方向都<tspan fill=\"#E74C3C\" font-weight=\"bold\">阻断!</tspan>",
        "  → 球卡死在M",
        "Step3: 球到不了Y",
        "<tspan fill=\"#27AE60\" font-weight=\"bold\">→ return true (安全)</tspan>",
    ],
))

# Case 10: Fork + unobserved → connected (Rule 1)
write("10_case_fork_unobs.svg", gen_case_page(
    page_num=10,
    title_zh="Case 4: 共因 + 未观测 → 连通",
    title_en="Fork X←M→Y · M is NOT observed → Connected",
    structure="Fork: X ← M → Y",
    z_text="M 未观测 (M ∉ Z)", z_color="#E74C3C",
    verdict="X ¬⊥ Y 连通", verdict_color="#E74C3C",
    rule_label="规则 1 (Up+未观测)",
    case_label="Fork + unobserved",
    example_title="暴雨 → 手术推迟 + 空气湿度高",
    example_lines=[
        "没记录天气(M 未观测)",
        "→ 暴雨同时导致了手术推迟和湿度高",
        "→ LLM 可能误以为手术推迟导致湿度高",
        "→ 后门大开，虚假相关性泄露!",
    ],
    explanation_lines=[
        "球从 X(手术推迟) 出发，方向=Up。X 未观测 → Rule1 允许，球走到 M(暴雨)。",
        "此时 M 未被观测 → Rule1 触发：Up 和 Down 都允许。球沿 Down 走到 Y(湿度高)。",
        "球到达 Y！这意味着 X 和 Y 之间存在一条未被阻断的后门路径。",
        "LLM 如果说'手术推迟导致空气湿度高'，就是在利用这条后门产生虚假因果。",
        "这是 LLM 最常见的错误——忘记控制混杂变量(M)，导致后门路径泄露。",
    ],
    dag_nodes=[
        (60, 100, "X", "#E74C3C", "#E74C3C", False),
        (200, 40,  "M", "#E74C3C", "#E74C3C", False),
        (340, 100, "Y", "#E74C3C", "#E74C3C", False),
    ],
    dag_edges=[
        (178, 52, 82, 88, "#E74C3C", True),
        (222, 52, 318, 88, "#E74C3C", False),
    ],
    trace_lines=[
        "Step0: (X, Up) 出发",
        "Step1: X未观测 → Rule1",
        "  → Up到M: (M, Up)",
        "Step2: M<tspan fill=\"#7F8C8D\">未观测</tspan> → Rule1",
        "  → Up+Down<tspan fill=\"#27AE60\" font-weight=\"bold\">都允许</tspan>",
        "  → Down到Y: (Y, Down)",
        "Step3: 球到达Y!",
        "<tspan fill=\"#E74C3C\" font-weight=\"bold\">→ return false (后门大开!)</tspan>",
    ],
))

# Case 11: Collider + observed → ACTIVATED (Rule 4)
write("11_case_collider_obs.svg", gen_case_page(
    page_num=11,
    title_zh="Case 5: 对撞 + 已观测 → 激活!",
    title_en="Collider X→M←Y · M is observed → ACTIVATED (Explaining Away)",
    structure="Collider: X → M ← Y",
    z_text="M 已观测 (M ∈ Z)", z_color="#E74C3C",
    verdict="X ¬⊥ Y 激活!", verdict_color="#E74C3C",
    rule_label="规则 4 (Down+已观测)",
    case_label="Collider + observed",
    example_title="业务能力 → 合伙人 ← 人脉关系",
    example_lines=[
        "已知此人是合伙人(Z 被观测)",
        "→ 如果发现他业务能力不行(X 为假)",
        "→ 就能推断他靠关系(Y 为真)",
        "→ explaining away: 虚假负相关被激活!",
    ],
    explanation_lines=[
        "球从 X(业务能力) 出发，方向=Up。X 未观测 → Rule1 允许，球沿 Down 走到 Z(合伙人)。",
        "此时 Z 已被观测 → Rule4 触发：只允许 Up，不允许 Down。",
        "球沿 Up 走到 Y(人脉关系)。球到达 Y！这是最反直觉的情况。",
        "业务能力和人脉关系本来毫无关系。但一旦知道结果(是合伙人)，两个原因就变得相关了。",
        "这就是 explaining away / 伯克森悖论——观测对撞节点反而激活了虚假路径。LLM 最容易在这里犯错。",
    ],
    dag_nodes=[
        (60, 100, "X", "#E74C3C", "#E74C3C", False),
        (200, 40,  "M", "#E74C3C", "#E74C3C", True),
        (340, 100, "Y", "#E74C3C", "#E74C3C", False),
    ],
    dag_edges=[
        (82, 88, 178, 52, "#E74C3C", False),
        (318, 88, 222, 52, "#E74C3C", True),
    ],
    trace_lines=[
        "Step0: (X, Up) 出发",
        "Step1: X未观测 → Rule1",
        "  → Down到Z: (Z, Down)",
        "Step2: Z<tspan fill=\"#E74C3C\" font-weight=\"bold\">已观测</tspan> → Rule4",
        "  → 只允许<tspan fill=\"#E74C3C\" font-weight=\"bold\">Up</tspan>",
        "  → Up到Y: (Y, Up)",
        "Step3: 球到达Y!",
        "<tspan fill=\"#E74C3C\" font-weight=\"bold\">→ return false (对撞陷阱激活!)</tspan>",
    ],
))

# Case 12: Collider + unobserved → blocked (natural)
write("12_case_collider_unobs.svg", gen_case_page(
    page_num=12,
    title_zh="Case 6: 对撞 + 未观测 → 天然阻断",
    title_en="Collider X→M←Y · M is NOT observed → Naturally Blocked",
    structure="Collider: X → M ← Y",
    z_text="M 未观测 (M ∉ Z)", z_color="#27AE60",
    verdict="X ⊥ Y 阻断", verdict_color="#27AE60",
    rule_label="天然阻断",
    case_label="Collider + unobserved",
    example_title="业务能力 → 合伙人 ← 人脉关系",
    example_lines=[
        "不知道此人是否是合伙人(M 未观测)",
        "→ 业务能力和人脉关系",
        "本来就是两码事，互不影响",
        "→ 不翻垃圾桶就安全，天然绝缘",
    ],
    explanation_lines=[
        "球从 X(业务能力) 出发，方向=Up。X 未观测 → Rule1 允许，球沿 Down 走到 Z(合伙人)。",
        "此时 Z 未被观测 → Rule3 触发：只允许 Down。但 Z 是对撞节点，没有向下的边。",
        "球无路可走，卡死在 Z。无法到达 Y(人脉关系)。",
        "对撞节点的'出厂设置'就是天然阻断——只要不去翻垃圾桶，X 和 Y 就井水不犯河水。",
        "这是 Collider 结构的安全模式。LLM 正确保持 M 未观测时，系统不会报警。",
    ],
    dag_nodes=[
        (60, 100, "X", "#27AE60", "#27AE60", False),
        (200, 40,  "M", "#27AE60", "#27AE60", False),
        (340, 100, "Y", "#27AE60", "#27AE60", False),
    ],
    dag_edges=[
        (82, 88, 178, 52, "#27AE60", False),
        (318, 88, 222, 52, "#27AE60", True),
    ],
    trace_lines=[
        "Step0: (X, Up) 出发",
        "Step1: X未观测 → Rule1",
        "  → Down到Z: (Z, Down)",
        "Step2: Z<tspan fill=\"#7F8C8D\">未观测</tspan> → Rule3",
        "  → 只允许Down，但Z无向下的边",
        "  → 球卡死在Z",
        "Step3: 球到不了Y",
        "<tspan fill=\"#27AE60\" font-weight=\"bold\">→ return true (天然阻断，安全)</tspan>",
    ],
))

# Clean up old files
for old_name in renames.values():
    op = os.path.join(OUT, old_name)
    if os.path.exists(op):
        os.remove(op)

print("\n[DONE] All 19 SVG pages generated!")
print("Next: run finalize_svg.py and svg_to_pptx.py")
