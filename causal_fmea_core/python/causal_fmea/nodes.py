# nodes.py — EdgeThemis LangGraph 节点
import json
from typing import Dict, Any
from pydantic import ValidationError
from openai import OpenAI

from agent_state_machine import CausalAgentState, ExtractedGraph, ReflectorVerdict
from context_guard import AgentContext
from causal_fmea_core import FmeaScore

print("[EdgeThemis] 连接 llama-server (127.0.0.1:8080)...")
client = OpenAI(
    base_url="http://127.0.0.1:8080/v1",
    api_key="edge_themis_key"
)


# ==========================================
# GENERATOR — LLM 先下判断，再画图
# ==========================================
def generate_graph_node(state: CausalAgentState) -> Dict[str, Any]:
    scenario = state.get("scenario_description", "")
    rust_report = state.get("rust_interception_report", "")
    interception_count = state.get("interception_count", 0)

    system_prompt = """
You are a causal reasoning engine (EdgeThemis). Given a scenario or causal question, you must:

STEP 1 — State your verdict FIRST:
- Output causal_verdict: "yes" or "no" — your final judgment on the causal question.
- Output hypothesized_cause: the entity being asked about as the potential cause.
- Output hypothesized_effect: the entity being asked about as the potential effect.

STEP 2 — Reason and draw the graph:
- Write your reasoning in reasoning_process.
- Draw causal edges that SUPPORT your verdict.
  * If verdict is "yes": there MUST be a causal path from hypothesized_cause to hypothesized_effect in your edges.
  * If verdict is "no": there MUST NOT be a direct edge from hypothesized_cause to hypothesized_effect.
- Every entity mentioned in the text MUST appear as a node. Do NOT treat any entity as mere "background".

STEP 3 — Causal structures:
- Chain (A -> B -> C): B mediates A's effect on C
- Fork (A <- B -> C): B is a common cause of A and C
- Collider (A -> B <- C): A and C both cause B

RULES:
- Use the SAME LANGUAGE as the input text. Do not translate entity names.
- FMEA scores (S, O, D) are 1-10 integers. Vary them based on actual semantics.
- Correlation is NOT causation. Only draw A->B if A truly causes B.
"""

    user_prompt = f"Input:\n{scenario}\n\nFirst state your verdict (yes/no), identify hypothesized_cause and hypothesized_effect, then draw the causal graph."

    if rust_report:
        user_prompt += (
            f"\n\n*** SYSTEM REJECTION ***\n"
            f"Your previous submission was rejected:\n{rust_report}\n"
            f"Please fix the issues and resubmit."
        )
        print(f"[Generator] 重试 #{interception_count}...")

    try:
        response = client.chat.completions.create(
            model="qwen2.5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "extracted_graph",
                    "schema": ExtractedGraph.model_json_schema()
                }
            },
            max_tokens=512,
            temperature=0.1
        )

        raw_json_str = response.choices[0].message.content
        extracted_data = ExtractedGraph.model_validate_json(raw_json_str)

        print(f"[Generator] verdict={extracted_data.causal_verdict} | "
              f"cause={extracted_data.hypothesized_cause[:50]} | "
              f"effect={extracted_data.hypothesized_effect[:50]}")
        print(f"[Generator] edges={[(e.source, e.target) for e in extracted_data.edges]}")

        return {
            "current_phase": "generate_graph",
            "extracted_graph": extracted_data
        }

    except ValidationError as e:
        print(f"[Generator] JSON解析失败: {str(e)[:100]}")
        return {
            "rust_interception_report": f"JSON parse error: {str(e)[:200]}",
            "interception_count": interception_count + 1
        }
    except Exception as e:
        print(f"[Generator] 异常: {str(e)[:100]}")
        return {
            "rust_interception_report": f"Connection/API error: {str(e)[:200]}",
            "interception_count": interception_count + 1
        }


# ==========================================
# VALIDATOR — 三道拦截
#   1. 言行一致性 (NetworkX: verdict与图是否自洽)
#   2. Kahn 环路检测 (Rust)
#   3. d-分离断言提取 (Rust)
# ==========================================
def validate_graph_node(state: CausalAgentState) -> Dict[str, Any]:
    print("[Validator] ===== 开始验证 =====")

    graph_data = state.get("extracted_graph")
    interception_count = state.get("interception_count", 0)

    if not graph_data or not graph_data.edges:
        print("[Validator] 图为空，拒绝")
        return {
            "rust_interception_report": "Graph is empty — no edges extracted.",
            "is_safe": False,
            "current_phase": "validate_graph",
            "interception_count": interception_count + 1
        }

    py_edges = [(edge.source, edge.target) for edge in graph_data.edges]
    verdict = (getattr(graph_data, "causal_verdict", "") or "").strip().lower()
    cause = (getattr(graph_data, "hypothesized_cause", "") or "").strip()
    effect = (getattr(graph_data, "hypothesized_effect", "") or "").strip()

    print(f"[Validator] verdict={verdict} | cause='{cause[:60]}' | effect='{effect[:60]}'")
    print(f"[Validator] edges={py_edges}")

    # ---- 拦截 1: 言行一致性 (NetworkX) ----
    if verdict in ("yes", "no") and cause and effect:
        import networkx as nx
        G = nx.DiGraph()
        for s, t in py_edges:
            G.add_edge(s.strip().lower(), t.strip().lower())

        nodes_lower = list(G.nodes)

        def fuzzy_match(target, candidates):
            t = target.strip().lower()
            for c in candidates:
                if t == c or t in c or c in t:
                    return c
            t_tokens = set(t.split())
            best, best_score = None, 0
            for c in candidates:
                c_tokens = set(c.split())
                if not c_tokens:
                    continue
                score = len(t_tokens & c_tokens) / len(t_tokens) if t_tokens else 0
                if score > best_score:
                    best_score, best = score, c
            return best if best_score >= 0.5 else None

        cause_node = fuzzy_match(cause, nodes_lower)
        effect_node = fuzzy_match(effect, nodes_lower)
        print(f"[Validator] 实体匹配: cause -> [{cause_node}] | effect -> [{effect_node}]")

        if cause_node and effect_node:
            path_exists = nx.has_path(G, cause_node, effect_node)

            if verdict == "yes" and not path_exists:
                print("[Validator] REJECT: verdict=Yes but no path in graph!")
                return {
                    "rust_interception_report": f"Verdict is YES but no causal path from '{cause}' to '{effect}' exists in your graph. Add edges or change verdict to No.",
                    "is_safe": False, "d_separation_claims": [],
                    "current_phase": "validate_graph",
                    "interception_count": interception_count + 1
                }

            if verdict == "no" and path_exists:
                print("[Validator] REJECT: verdict=No but path exists in graph!")
                return {
                    "rust_interception_report": f"Verdict is NO but a causal path from '{cause}' to '{effect}' exists in your graph. Remove the path or change verdict to Yes.",
                    "is_safe": False, "d_separation_claims": [],
                    "current_phase": "validate_graph",
                    "interception_count": interception_count + 1
                }

            print(f"[Validator] 言行一致: verdict={verdict}, path_exists={path_exists} [OK]")

    # ---- FMEA 扫描 ----
    for edge in graph_data.edges:
        scorer = FmeaScore(edge.S, edge.O, edge.D)
        rpn = scorer.calculate_rpn()
        if rpn > 500:
            print(f"[Validator] FMEA高危: {edge.source}->{edge.target} RPN={rpn}")

    # ---- 拦截 2+3: Rust Kahn + d-分离 ----
    with AgentContext() as rust_engine:
        rust_engine.inject_edges(py_edges)
        topology_safe = rust_engine.check_graph_health()
        print(f"[Validator] Kahn环路: {'OK' if topology_safe else 'FAIL(有环)'}")

        if not topology_safe:
            print("[Validator] REJECT: 环路!")
            return {
                "rust_interception_report": "Cycle detected: A->B and B->A cannot both be true. Fix the loop.",
                "is_safe": False, "d_separation_claims": [],
                "current_phase": "validate_graph",
                "interception_count": interception_count + 1
            }

        real_claims = rust_engine.extract_testable_claims()
        print(f"[Validator] d-分离断言数={len(real_claims)}")
        for c in real_claims:
            print(f"  -> {c[:150]}")

        if real_claims:
            report_msg = "D-separation claims extracted — forwarding to Reflector."
            is_finally_safe = False
        else:
            report_msg = ""
            is_finally_safe = True

        return {
            "is_safe": is_finally_safe,
            "d_separation_claims": real_claims,
            "rust_interception_report": report_msg,
            "current_phase": "validate_graph",
            "interception_count": interception_count  # claims are normal, not errors
        }


# ==========================================
# REFLECTOR — LLM 常识审判 d-分离断言
# ==========================================
def reflector_node(state: CausalAgentState) -> Dict[str, Any]:
    claims = state.get("d_separation_claims", [])
    interception_count = state.get("interception_count", 0)

    if not claims:
        return {"is_safe": True, "current_phase": "reflector"}

    claims_text = "\n".join([f"Claim {i+1}: {claim}" for i, claim in enumerate(claims)])
    print(f"[Reflector] 审查 {len(claims)} 条d-分离断言...")

    system_prompt = """You are a common-sense judge. The system extracted a causal graph and derived d-separation claims from it. Your ONLY job: judge whether these claims are ABSURD based on human common sense.

A d-separation claim is a conditional independence statement like:
- "X and Y are completely independent (no causal link at all)"
- "If we hold Z constant, then X has no effect on Y"

Judgment criteria:
- If the claim clearly VIOLATES basic common sense or physical laws (e.g., "rooster crowing causes the sun to rise", "prayer cures terminal cancer") -> REJECT
- If the claim is about "controlling a common factor Z makes two things independent" — this is STATISTICALLY VALID and should PASS
- If the claim seems plausible or you are unsure -> PASS

Only REJECT truly absurd claims. Do NOT overthink. When in doubt, PASS.

Output JSON: {"verdict": "REJECT or PASS", "reason": "brief reason"}"""

    user_prompt = f"D-Separation Claims to Judge:\n{claims_text}\n\nAre any of these claims absurd or physically impossible? If not, PASS."

    try:
        response = client.chat.completions.create(
            model="qwen2.5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "reflector_verdict",
                    "schema": ReflectorVerdict.model_json_schema()
                }
            },
            max_tokens=256,
            temperature=0.0
        )

        raw_content = response.choices[0].message.content
        res_json = json.loads(raw_content)

        if res_json.get("verdict") == "REJECT":
            print(f"[Reflector] REJECT: {res_json.get('reason')[:150]}")
            return {
                "is_safe": False,
                "rust_interception_report": f"Common-sense REJECT: {res_json.get('reason')}",
                "current_phase": "reflector",
                "interception_count": interception_count + 1
            }

        print(f"[Reflector] PASS")
        return {"is_safe": True, "current_phase": "reflector"}

    except Exception as e:
        print(f"[Reflector] 异常: {str(e)[:100]}")
        return {
            "is_safe": False,
            "rust_interception_report": f"Reflector error: {str(e)[:200]}",
            "current_phase": "reflector",
            "interception_count": interception_count + 1
        }
