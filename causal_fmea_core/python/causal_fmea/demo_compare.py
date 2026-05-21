"""
demo_compare.py — EdgeThemis 消融对比演示
同一场景 × 三种配置，展示每一层防御的增量价值
配置 A: 纯 LLM（无 Schema、无验证）
配置 B: LLM + Schema + Rust 拓扑验证（无 Reflector）
配置 C: 完整 EdgeThemis（全闭环）
"""

import json
from openai import OpenAI
from langgraph.graph import StateGraph, START, END

from agent_state_machine import CausalAgentState
from nodes import generate_graph_node, validate_graph_node, reflector_node

# ── 公用 LLM 客户端 ──────────────────────────────────
client = OpenAI(base_url="http://127.0.0.1:8080/v1", api_key="edge_themis_key")

# ── 测试场景 ──────────────────────────────────────
SCENARIO = """
某市第三人民医院2024年第一季度的手术感染率从往年的百分之零点三突然飙升至百分之五点七，导致三位患者因术后败血症死亡，医院被卫健委立案调查。

医院管理层迅速将矛头指向了手术室护士长张姐——她在2023年12月因为与科室主任发生激烈争吵后被调离了手术室管理岗位，由刚毕业两年的年轻护士小李接替。院长在内部会议上说："手术室管理经验不足是唯一的原因。"

然而，卫健委的深度调查揭露了更复杂的原因链。第一，医院在2023年11月为削减成本，将手术器械消毒外包给了一家报价最低的第三方消毒公司。抽检发现该公司使用的环氧乙烷灭菌浓度仅为行业标准的三分之一，导致手术器械上的芽孢残留量超标十二倍。

第二，手术室的两台层流净化空调在2024年1月相继故障，维修申请交上去后，分管后勤的副院长以"预算已用完"为由驳回了紧急采购申请，直到3月底才走完重新审批流程。在此期间手术室空气洁净度从ISO 5级跌落到了ISO 8级，空气中的菌落数增加了四十倍。

第三，新护士长小李实际上在2024年2月就发现了器械包存在湿包现象（灭菌失败的标志），她三次向医务科提交了书面风险报告。医务科长的回复是"消毒公司有正规资质，你们的操作问题不要推给别人"。这三份报告后来在医院档案柜的最底层被发现，上面已经积了灰。

第四，三位死亡的败血症患者均为高龄糖尿病患者，本身属于术后感染高风险人群。但他们被安排在了同一间未经过滤的备用手术室里集中手术——这是后勤部为了"提高手术室周转率"而做的调度决定。

最终被递交到卫健委的调查总结中，专家组写道："将事故简单归因于年轻护士长缺乏经验，掩盖了消毒外包失效、层流净化系统停摆、风险报告被压制以及高风险患者集中调度这四条真实的因果链条。管理层的反复决策失误和成本削减导向，才是事故系统性发生的共同根源。"
"""

# ── 路由函数（同 app.py） ──────────────────────────────
def route_from_validator(state: CausalAgentState):
    is_safe = state.get("is_safe", False)
    claims = state.get("d_separation_claims", [])
    if state.get("interception_count", 0) >= 3:
        return END
    if not is_safe and not claims:
        return "generate_graph"
    if claims:
        return "reflector"
    return END

def route_from_reflector(state: CausalAgentState):
    if state.get("interception_count", 0) >= 3:
        return END
    if not state.get("is_safe", False):
        return "generate_graph"
    return END

# ── 分隔线 ────────────────────────────────────────────
def section(title):
    print(f"\n{'═'*65}")
    print(f"  {title}")
    print(f"{'═'*65}")

def sep():
    print(f"{'─'*65}")

# ══════════════════════════════════════════════════════
#  配置 A：纯 LLM，无任何约束
# ══════════════════════════════════════════════════════
def run_config_a():
    section("配置 A：纯 LLM（无 Schema、无验证、无反思）")

    prompt = """你是一个因果推理专家。请仔细阅读下面的事故报告，分析其中的因果关系。

请列出所有相关的因果链条，说明每个原因导致了什么结果，以及传导机制是什么。

【事故报告】
""" + SCENARIO

    try:
        resp = client.chat.completions.create(
            model="qwen2.5",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.1
        )
        text = resp.choices[0].message.content
        print(text)
        sep()
        print(f"  自由文本 · 无结构 · 无 FMEA · 无验证 · 无纠错")

    except Exception as e:
        print(f"  异常: {e}")

# ══════════════════════════════════════════════════════
#  配置 B：LLM + Schema + Rust 拓扑验证（跳过 Reflector）
# ══════════════════════════════════════════════════════
def run_config_b():
    section("配置 B：+ JSON Schema + Rust 验证（无 Reflector 常识审判）")

    state = {
        "scenario_description": SCENARIO,
        "current_phase": "start",
        "extracted_graph": None,
        "rust_interception_report": "",
        "d_separation_claims": [],
        "interception_count": 0,
        "is_safe": False,
    }

    result = generate_graph_node(state)
    graph = result.get("extracted_graph")

    if not graph:
        print("  ✗ Generator 未提取到因果图")
        return

    print(f"  Generator → {len(graph.edges)} 条结构化因果边（含 FMEA 评分）")

    state["extracted_graph"] = graph
    val = validate_graph_node(state)

    claims = val.get("d_separation_claims", [])
    report = val.get("rust_interception_report", "")

    is_cycle = "拓扑错误" in report
    if is_cycle:
        print(f"  Rust 引擎 → Kahn 拓扑检测: ✗ 发现死循环！")
    elif claims:
        print(f"  Rust 引擎 → Kahn 拓扑检测: ✓ 无环路")
        print(f"            → 贝叶斯 d-分离: 发现 {len(claims)} 条逻辑破绽")
    else:
        print(f"  Rust 引擎 → Kahn 拓扑检测: ✓ 无环路")
        print(f"            → 贝叶斯 d-分离: 无破绽，图内完全自洽")

    # 打印全部 claim
    if claims:
        print(f"\n  ⚠ {len(claims)} 条 d-分离断言（未经常识审判）：")
        for i, c in enumerate(claims):
            print(f"     [{i+1}] {c}")
        sep()
        print(f"  缺 Reflector → 只要是图推导出的断言就照单全收")

    print(f"\n  因果图 ({len(graph.edges)} 条边):")
    for i, e in enumerate(graph.edges):
        desc = getattr(e, 'description', '')
        print(f"  [{i+1}] {e.source} → {e.target}  (S={e.S} O={e.O} D={e.D})")
        if desc:
            print(f"       {desc}")

# ══════════════════════════════════════════════════════
#  配置 C：完整 EdgeThemis
# ══════════════════════════════════════════════════════
def run_config_c():
    section("配置 C：完整 EdgeThemis（Schema + Rust + Reflector 全闭环）")

    initial_state = {
        "scenario_description": SCENARIO,
        "current_phase": "start",
        "extracted_graph": None,
        "rust_interception_report": "",
        "d_separation_claims": [],
        "interception_count": 0,
        "is_safe": False,
    }

    builder = StateGraph(CausalAgentState)
    builder.add_node("generate_graph", generate_graph_node)
    builder.add_node("validate_graph", validate_graph_node)
    builder.add_node("reflector", reflector_node)
    builder.add_edge(START, "generate_graph")
    builder.add_edge("generate_graph", "validate_graph")
    builder.add_conditional_edges(
        "validate_graph", route_from_validator,
        {"generate_graph": "generate_graph", "reflector": "reflector", END: END}
    )
    builder.add_conditional_edges(
        "reflector", route_from_reflector,
        {"generate_graph": "generate_graph", END: END}
    )

    agent = builder.compile()
    final_graph = None
    retries = 0
    claims_to_reflector = []
    reflector_verdict = None

    for output in agent.stream(initial_state):
        for node_name, state_update in output.items():
            if "extracted_graph" in state_update and state_update["extracted_graph"] is not None:
                final_graph = state_update["extracted_graph"]
            claims = state_update.get("d_separation_claims", [])
            is_safe = state_update.get("is_safe", False)

            if node_name == "validate_graph" and claims:
                claims_to_reflector = claims
                print(f"  Validator → 提取 {len(claims)} 条 d-分离断言，移交 Reflector")
            elif node_name == "reflector":
                reflector_verdict = "REJECT" if not is_safe else "PASS"
                if not is_safe:
                    retries += 1
                print(f"  Reflector → 常识审判: {reflector_verdict}")

    # 打印全部提交给 Reflector 的 claim
    if claims_to_reflector:
        print(f"\n  [{reflector_verdict}] Reflector 审判了以下 {len(claims_to_reflector)} 条断言：")
        for i, c in enumerate(claims_to_reflector):
            print(f"     [{i+1}] {c}")

    if final_graph:
        print(f"\n  最终因果图 ({len(final_graph.edges)} 条边，Reflector={reflector_verdict}，重写={retries}次):")
        for i, e in enumerate(final_graph.edges):
            desc = getattr(e, 'description', '')
            print(f"  [{i+1}] {e.source} → {e.target}  (S={e.S} O={e.O} D={e.D})")
            if desc:
                print(f"       {desc}")
        sep()
    else:
        print(f"  ✗ 推演未通过验证")

# ══════════════════════════════════════════════════════
#  总结
# ══════════════════════════════════════════════════════
def print_summary():
    section("消融对比总结")
    print("""
┌──────────────────────────────┬──────────┬──────────┬──────────┐
│          防御能力              │  配置 A  │  配置 B  │  配置 C  │
├──────────────────────────────┼──────────┼──────────┼──────────┤
│ 结构化因果图 (JSON Schema)     │    ✗     │    ✓     │    ✓     │
│ FMEA 风险评分 (S/O/D)         │    ✗     │    ✓     │    ✓     │
│ Kahn 环路拓扑检测              │    ✗     │    ✓     │    ✓     │
│ 贝叶斯 d-分离破绽提取          │    ✗     │    ✓     │    ✓     │
│ 常识审判 (Reflector)          │    ✗     │    ✗     │    ✓     │
├──────────────────────────────┼──────────┼──────────┼──────────┤
│ d-分离破绽处理方式             │    —     │ 照单全收  │ 逐条审判  │
│ 触发纠错重写                  │    —     │    —     │  REJECT时 │
│ 可审计 (每边有 causal reason)  │    ✗     │    ✓     │    ✓     │
└──────────────────────────────┴──────────┴──────────┴──────────┘
""")

# ══════════════════════════════════════════════════════
if __name__ == "__main__":
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║   EdgeThemis 消融对比实验                                  ║")
    print("║   同一场景 × 三种配置 → 展示每一层防御的增量价值             ║")
    print("╚═══════════════════════════════════════════════════════════╝")

    run_config_a()
    run_config_b()
    run_config_c()
    print_summary()
