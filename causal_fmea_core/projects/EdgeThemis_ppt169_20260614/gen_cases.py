#!/usr/bin/env python3
"""Generate 6 d-separation case pages with stage indicators."""
import os

OUT = "svg_output"

def indicator(active="dsep"):
    stages = [
        ("input","Input",None,30),("generator","Generator","Python",100),
        ("cycle","Cycle","Rust",175),("dsep","d-Sep","Rust",250),
        ("fmea","FMEA","Rust",325),("reflector","Reflector","Python",400),
        ("output","Output",None,475),
    ]
    lines = ['<g id="stage-indicator" transform="translate(660, 14)">',
             '<rect x="0" y="0" width="560" height="42" rx="6" fill="#F5F7FA" stroke="#D5D8DC" stroke-width="1"/>']
    for sid,label,lang,cx in stages:
        act = (sid==active)
        r=9 if act else 6; fill="#1A3C6E" if act else "#D5D8DC"
        tf="#1A3C6E" if act else "#7F8C8D"; fw=' font-weight="bold"' if act else ''
        lines.append(f'<circle cx="{cx}" cy="15" r="{r}" fill="{fill}"/>')
        if act and sid=="dsep":
            lines.append(f'<text x="{cx}" y="19" text-anchor="middle" font-family="Arial, sans-serif" font-size="8" fill="#FFF" font-weight="bold">d</text>')
        lines.append(f'<text x="{cx}" y="36" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" fill="{tf}"{fw}>{label}</text>')
        if lang:
            lc="#E8B931" if lang=="Python" else "#2E86DE"
            op="0.7" if act else "0.3"; lw=36 if lang=="Python" else 28
            lines.append(f'<rect x="{cx-lw//2}" y="1" width="{lw}" height="5" rx="2" fill="{lc}" fill-opacity="{op}"/>')
            lines.append(f'<text x="{cx}" y="5" text-anchor="middle" font-family="Arial, sans-serif" font-size="6" fill="{lc}"{fw}>{lang}</text>')
    for i in range(5):
        x1=36+75*i; x2=x1+75
        lines.append(f'<line x1="{x1}" y1="15" x2="{x2}" y2="15" stroke="#D5D8DC" stroke-width="1.5"/>')
    lines.extend(['<rect x="490" y="5" width="60" height="30" rx="4" fill="#FFF" stroke="#D5D8DC" stroke-width="0.5"/>',
        '<circle cx="500" cy="14" r="3" fill="#E8B931"/><text x="508" y="17" font-family="Arial, sans-serif" font-size="7" fill="#7F8C8D">Python</text>',
        '<circle cx="500" cy="26" r="3" fill="#2E86DE"/><text x="508" y="29" font-family="Arial, sans-serif" font-size="7" fill="#7F8C8D">Rust</text>','</g>'])
    return "\n".join(lines)

def ftr(n):
    return f'<text x="60" y="695" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">{n}</text><text x="1220" y="695" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">EdgeThemis</text>'

def case_page(n, zh, en, struct, ztxt, zcol, verd, vcol, rule, ex_title, ex_lines, expl_lines, nodes, edges, trace):
    import math
    R = 26  # node radius
    dag = []
    # Build node lookup: label -> (cx, cy, observed)
    node_map = {}
    for cx,cy,lbl,obs in nodes:
        node_map[lbl] = (cx, cy, obs)

    # Helper: compute arrowhead polygon with tip at node boundary
    def arrow(from_lbl, to_lbl):
        """Draw line from node boundary to node boundary, arrowhead tip at target boundary."""
        fx, fy, _ = node_map[from_lbl]
        tx, ty, _ = node_map[to_lbl]
        dx, dy = tx-fx, ty-fy
        ln = math.sqrt(dx*dx + dy*dy)
        ux, uy = dx/ln, dy/ln
        # Line from boundary to boundary (with gap for arrowhead)
        line_x1 = fx + ux*(R+2)
        line_y1 = fy + uy*(R+2)
        tip_x = tx - ux*(R+2)
        tip_y = ty - uy*(R+2)
        # Arrowhead at target boundary, pointing toward target
        px, py = -uy*9, ux*9
        b1x = tip_x - ux*18 + px
        b1y = tip_y - uy*18 + py
        b2x = tip_x - ux*18 - px
        b2y = tip_y - uy*18 - py
        dag.append(f'<line x1="{line_x1:.1f}" y1="{line_y1:.1f}" x2="{tip_x:.1f}" y2="{tip_y:.1f}" stroke="{zcol}" stroke-width="3"/>')
        dag.append(f'<polygon points="{tip_x:.1f},{tip_y:.1f} {b1x:.1f},{b1y:.1f} {b2x:.1f},{b2y:.1f}" fill="{zcol}" stroke="#FFF" stroke-width="1.5"/>')

    # 1. Draw arrowheads (from edge definitions)
    for from_lbl, to_lbl in edges:
        arrow(from_lbl, to_lbl)

    # 2. Draw nodes ON TOP of arrowheads (so node circles don't cover arrows)
    for cx,cy,lbl,obs in nodes:
        if obs:
            dag.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="{zcol}" fill-opacity="0.15" stroke="{zcol}" stroke-width="2.5"/>')
            dag.append(f'<text x="{cx}" y="{cy+6}" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="{zcol}" font-weight="bold">{lbl}</text>')
            dag.append(f'<text x="{cx}" y="{cy+28}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="{zcol}" font-weight="bold">已观测 ✓</text>')
        else:
            dag.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="#FFF" stroke="{zcol}" stroke-width="2.5" stroke-dasharray="5,3"/>')
            dag.append(f'<text x="{cx}" y="{cy+6}" text-anchor="middle" font-family="Arial, sans-serif" font-size="15" fill="{zcol}" font-weight="bold">{lbl}</text>')

    dag_s = "\n    ".join(dag)
    trace_s = "\n".join(f'<text x="20" y="{60+i*22}" font-family="Consolas, monospace" font-size="13" fill="#2C3E50">{l}</text>' for i,l in enumerate(trace))
    ex_s = "\n".join(f'<text x="870" y="{310+i*24}" font-family="Arial, sans-serif" font-size="13" fill="#2C3E50">{l}</text>' for i,l in enumerate(ex_lines))
    expl_s = "\n".join(f'<text x="80" y="{505+i*26}" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50">{l}</text>' for i,l in enumerate(expl_lines))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720">
  <defs><filter id="cs" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur in="SourceAlpha" stdDeviation="4"/><feOffset dx="0" dy="2" result="ob"/><feFlood flood-color="#000" flood-opacity="0.06" result="sc"/><feComposite in="sc" in2="ob" operator="in" result="s"/><feMerge><feMergeNode in="s"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
  <rect width="1280" height="720" fill="#FFFFFF"/>
  <g id="header"><rect x="60" y="30" width="5" height="32" rx="2" fill="#1A3C6E"/>
  <text x="78" y="56" font-family="Georgia, SimHei, serif" font-size="28" font-weight="bold" fill="#1A3C6E">{zh}</text>
  <text x="78" y="76" font-family="Arial, sans-serif" font-size="14" fill="#7F8C8D">{en}</text>
  <line x1="60" y1="88" x2="1220" y2="88" stroke="#D5D8DC" stroke-width="1"/></g>
  {indicator()}
  <g id="dag" transform="translate(80, 120)">
    <rect x="-10" y="-10" width="400" height="280" rx="10" fill="#FFF" stroke="#D5D8DC" stroke-width="1"/>
    <text x="190" y="20" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#1A3C6E" font-weight="bold">{struct}</text>
    {dag_s}
  </g>
  <g id="trace" transform="translate(500, 110)">
    <rect x="0" y="0" width="320" height="260" rx="10" fill="#F5F7FA" stroke="#D5D8DC" stroke-width="1"/>
    <text x="160" y="28" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#1A3C6E" font-weight="bold">贝叶斯球移动轨迹</text>
    <line x1="20" y1="38" x2="300" y2="38" stroke="#D5D8DC" stroke-width="1"/>
    {trace_s}
  </g>
  <g id="verdict" transform="translate(850, 110)">
    <rect x="0" y="0" width="370" height="90" rx="10" fill="{vcol}" fill-opacity="0.08" stroke="{vcol}" stroke-width="1.5"/>
    <text x="185" y="30" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="{vcol}" font-weight="bold">判定: {rule}</text>
    <text x="185" y="60" text-anchor="middle" font-family="Arial, sans-serif" font-size="22" fill="{vcol}" font-weight="bold">{verd}</text>
    <text x="185" y="82" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#7F8C8D">Z 状态: {ztxt}</text>
  </g>
  <g id="example" filter="url(#cs)">
    <rect x="850" y="220" width="370" height="180" rx="10" fill="#FFF"/>
    <rect x="850" y="220" width="370" height="6" rx="3" fill="{vcol}"/>
    <text x="870" y="250" font-family="Georgia, SimHei, serif" font-size="16" fill="{vcol}" font-weight="bold">现实案例</text>
    <text x="870" y="278" font-family="Arial, sans-serif" font-size="14" fill="#2C3E50" font-weight="bold">{ex_title}</text>
    {ex_s}
  </g>
  <g id="explanation">
    <rect x="60" y="420" width="1160" height="250" rx="10" fill="#FFF" stroke="#D5D8DC" stroke-width="1"/>
    <rect x="60" y="420" width="1160" height="6" rx="3" fill="#1A3C6E"/>
    <text x="80" y="450" font-family="Georgia, SimHei, serif" font-size="16" fill="#1A3C6E" font-weight="bold">深入理解：球是怎么移动的</text>
    {expl_s}
  </g>
  {ftr(n)}
</svg>'''

# Generate 6 cases
cases = [
    ("07", "Case 1: 链式+已观测→阻断", "Chain X→M→Y · M observed → Blocked",
     "Chain: X→M→Y", "M已观测", "#27AE60", "X⊥Y 阻断", "#27AE60", "规则2",
     "药物→血压降低→头晕缓解",
     ["已知血压确实降低了(M被观测)","→ 在'血压已降'前提下","用药(X)对头晕缓解(Y)无额外预测力","→ 路径被阻断"],
     ["球从X出发→Up到M。M已观测→Rule2触发：两个方向都阻断。球卡死在M。","一旦知道中介M，起点X就无法给终点Y额外信息。","Chain的'安全模式'——中介被控制后，因果传导链被截断。"],
     [(60,100,"X",False),(200,40,"M",True),(340,100,"Y",False)],
     [("X","M"),("M","Y")],
     ["Step0: (X,Up)出发","Step1: X未观测→Rule1→Up到M","Step2: M已观测→Rule2","  → 两个方向都阻断!","  → 球卡死在M","<tspan fill='#27AE60' font-weight='bold'>→ return true (安全)</tspan>"]),

    ("08", "Case 2: 链式+未观测→连通", "Chain X→M→Y · M NOT observed → Connected",
     "Chain: X→M→Y", "M未观测", "#27AE60", "X¬⊥Y 连通", "#27AE60", "规则3",
     "用药→病情好转→恢复运动",
     ["不知道病情是否好转(M未观测)","→ 用药(X)的影响可通过","病情好转(M)传递到恢复运动(Y)","→ 唯一合法的因果通路"],
     ["球从X出发→Down到M。M未观测→Rule3：只允许Down。球到Y。","这是唯一合法通路——Chain就是真实因果链。","用药→好转→恢复运动，连通是正确的，不应报警。"],
     [(60,100,"X",False),(200,40,"M",False),(340,100,"Y",False)],
     [("X","M"),("M","Y")],
     ["Step0: (X,Up)出发","Step1: X未观测→Rule1→Down到M","Step2: M未观测→Rule3","  → 只允许Down→到Y","Step3: 球到达Y","<tspan fill='#27AE60' font-weight='bold'>→ return false (连通，但合法)</tspan>"]),

    ("09", "Case 3: 共因+已观测→阻断", "Fork X←M→Y · M observed → Blocked",
     "Fork: X←M→Y", "M已观测", "#27AE60", "X⊥Y 阻断", "#27AE60", "规则2",
     "暴雨→手术推迟+空气湿度高",
     ["已确认下暴雨(M被观测)","→ 在'已知暴雨'前提下","手术推迟(X)和湿度高(Y)","无虚假相关性，后门被堵死"],
     ["球从X出发→Up到M。M已观测→Rule2：两个方向都阻断。","暴雨同时解释了X和Y。在'已知暴雨'下，X和Y间无可传递的虚假相关。","后门准则的工程实现——观测混杂变量后，后门被物理切断。"],
     [(60,100,"X",False),(200,40,"M",True),(340,100,"Y",False)],
     [("M","X"),("M","Y")],
     ["Step0: (X,Up)出发","Step1: X未观测→Rule1→Up到M","Step2: M已观测→Rule2","  → 两个方向都阻断!","  → 球卡死在M","<tspan fill='#27AE60' font-weight='bold'>→ return true (安全)</tspan>"]),

    ("10", "Case 4: 共因+未观测→连通", "Fork X←M→Y · M NOT observed → Connected",
     "Fork: X←M→Y", "M未观测", "#E74C3C", "X¬⊥Y 连通", "#E74C3C", "规则1",
     "暴雨→手术推迟+空气湿度高",
     ["没记录天气(M未观测)","→ 暴雨同时导致手术推迟和湿度高","→ LLM可能误以为推迟导致湿度高","→ 后门大开，虚假相关泄露!"],
     ["球从X出发→Up到M。M未观测→Rule1：Up+Down都允许。球Down到Y。","球到达Y！X和Y间存在未阻断的后门路径。","LLM最常见错误——忘记控制混杂变量M，导致后门泄露。"],
     [(60,100,"X",False),(200,40,"M",False),(340,100,"Y",False)],
     [("M","X"),("M","Y")],
     ["Step0: (X,Up)出发","Step1: X未观测→Rule1→Up到M","Step2: M未观测→Rule1","  → Up+Down都允许→Down到Y","Step3: 球到达Y!","<tspan fill='#E74C3C' font-weight='bold'>→ return false (后门大开!)</tspan>"]),

    ("11", "Case 5: 对撞+已观测→激活!", "Collider X→M←Y · M observed → ACTIVATED",
     "Collider: X→M←Y", "M已观测", "#E74C3C", "X¬⊥Y 激活!", "#E74C3C", "规则4",
     "业务能力→合伙人←人脉关系",
     ["已知是合伙人(M被观测)","→ 如果发现业务能力不行(X为假)","→ 就能推断靠关系(Y为真)","→ explaining away! 虚假负相关激活!"],
     ["球从X出发→Down到Z。Z已观测→Rule4：只允许Up。球Up到Y。","业务能力和人脉本无关。但知道结果(是合伙人)后，两原因变相关。","explaining away/伯克森悖论——观测对撞节点反而激活虚假路径。"],
     [(60,100,"X",False),(200,40,"M",True),(340,100,"Y",False)],
     [("X","M"),("Y","M")],
     ["Step0: (X,Up)出发","Step1: X未观测→Rule1→Down到Z","Step2: Z已观测→Rule4","  → 只允许Up→到Y","Step3: 球到达Y!","<tspan fill='#E74C3C' font-weight='bold'>→ return false (对撞陷阱激活!)</tspan>"]),

    ("12", "Case 6: 对撞+未观测→天然阻断", "Collider X→M←Y · M NOT observed → Blocked",
     "Collider: X→M←Y", "M未观测", "#27AE60", "X⊥Y 阻断", "#27AE60", "天然阻断",
     "业务能力→合伙人←人脉关系",
     ["不知道是否是合伙人(M未观测)","→ 业务能力和人脉关系","本来就是两码事，互不影响","→ 不翻垃圾桶就安全"],
     ["球从X出发→Down到Z。Z未观测→Rule3：只允许Down。但Z无向下边，球卡死。","对撞节点'出厂设置'就是天然阻断——不翻垃圾桶，X和Y井水不犯河水。","Collider的安全模式。LLM正确保持M未观测时，系统不报警。"],
     [(60,100,"X",False),(200,40,"M",False),(340,100,"Y",False)],
     [("X","M"),("Y","M")],
     ["Step0: (X,Up)出发","Step1: X未观测→Rule1→Down到Z","Step2: Z未观测→Rule3","  → 只允许Down，但Z无向下边","  → 球卡死在Z","<tspan fill='#27AE60' font-weight='bold'>→ return true (天然阻断，安全)</tspan>"]),
]

for args in cases:
    fname = f"{args[0]}_case_{['chain_obs','chain_unobs','fork_obs','fork_unobs','collider_obs','collider_unobs'][int(args[0])-7]}.svg"
    with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
        f.write(case_page(*args))
    print(f"  [OK] {fname}")

print("\n[DONE] 6 d-separation case pages generated!")
