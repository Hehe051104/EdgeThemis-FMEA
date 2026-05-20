# nodes.py — EdgeThemis: Generator(画图) → Validator(图论判 verdict) → Reflector(常识审断言)
import json
from typing import Dict, Any
from pydantic import ValidationError
from openai import OpenAI

from agent_state_machine import CausalAgentState, ExtractedGraph, ReflectorVerdict
from context_guard import AgentContext
from causal_fmea_core import FmeaScore

print("[EdgeThemis] 连接 llama-server...")
client = OpenAI(base_url="http://127.0.0.1:8080/v1", api_key="edge_themis_key")


# ==========================================
# GENERATOR — 只负责：识别实体 + 推理 + 画图。不做判决！
# ==========================================
def generate_graph_node(state: CausalAgentState) -> Dict[str, Any]:
    scenario = state.get("scenario_description", "")
    rust_report = state.get("rust_interception_report", "")
    interception_count = state.get("interception_count", 0)

    system_prompt = """You are a causal graph extraction engine. Given a scenario or question, extract the TRUE causal structure.

CRITICAL: The input may be a QUESTION (e.g. "Does X cause Y?"), not a statement of fact. Do NOT assume X causes Y just because the question asks about it. If X does NOT cause Y, draw the real structure (e.g. both X and Y are effects of a common cause Z). Draw what IS true, not what the question implies.

STEP 1 — Identify entities:
- hypothesized_cause: the entity being asked about as the potential CAUSE.
- hypothesized_effect: the entity being asked about as the potential EFFECT. If the question asks about MULTIPLE effects (e.g. "Does Z cause X and Y?"), include ALL of them separated by " and " (e.g. "X and Y").
- Identify ALL other entities/conditions mentioned. Every noun phrase is a node.

STEP 2 — Reason and draw the causal graph:
- Write your reasoning in reasoning_process.
- Draw causal edges. Include ALL identified entities as nodes. Do NOT treat any entity as "background".
- Causal structures: Chain (A→B→C), Fork (A←B→C), Collider (A→B←C).
- Only draw A→B if A truly causes B. Correlation is NOT causation.

RULES:
- Use the SAME LANGUAGE as the input text. Do not translate entity names.
- FMEA scores (S, O, D) are 1-10 integers. Vary them based on semantics."""

    user_prompt = f"Input:\n{scenario}\n\nIdentify hypothesized_cause and hypothesized_effect, then draw the causal graph."

    if rust_report:
        user_prompt += f"\n\n*** REJECTION FEEDBACK ***\n{rust_report}\nPlease fix and resubmit."
        print(f"[Generator] 重试 #{interception_count}")

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

        print(f"[Generator] cause={extracted_data.hypothesized_cause[:50]} | effect={extracted_data.hypothesized_effect[:50]}")
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
            "rust_interception_report": f"API error: {str(e)[:200]}",
            "interception_count": interception_count + 1
        }


# ==========================================
# VALIDATOR — 图论算法计算 verdict + Rust Kahn + d-分离
# ==========================================
def validate_graph_node(state: CausalAgentState) -> Dict[str, Any]:
    print("[Validator] ===== 开始 =====")

    graph_data = state.get("extracted_graph")
    interception_count = state.get("interception_count", 0)

    if not graph_data or not graph_data.edges:
        print("[Validator] 图为空")
        return {
            "rust_interception_report": "Graph is empty.",
            "is_safe": False,
            "current_phase": "validate_graph",
            "interception_count": interception_count + 1
        }

    py_edges = [(e.source, e.target) for e in graph_data.edges]
    cause = (getattr(graph_data, "hypothesized_cause", "") or "").strip()
    effect_raw = (getattr(graph_data, "hypothesized_effect", "") or "").strip()

    print(f"[Validator] cause='{cause[:60]}' | effect='{effect_raw[:60]}'")
    print(f"[Validator] edges={py_edges}")

    # ---- Step 1: Compute verdict from graph structure (NetworkX) ----
    import networkx as nx
    import re

    G = nx.DiGraph()
    for s, t in py_edges:
        G.add_edge(s.strip().lower(), t.strip().lower())
    nodes_lower = list(G.nodes)

    def fuzzy_match(target, candidates):
        t = target.strip().lower()
        if not t: return None
        for c in candidates:
            if t == c or t in c or c in t:
                return c
        t_tokens = set(t.split())
        best, best_score = None, 0
        for c in candidates:
            c_tokens = set(c.split())
            if not c_tokens: continue
            score = len(t_tokens & c_tokens) / len(t_tokens) if t_tokens else 0
            if score > best_score: best_score, best = score, c
        return best if best_score >= 0.5 else None

    # Split effect on " and " / " or " for compound questions (e.g., "X and Y")
    effect_parts = re.split(r'\s+and\s+|\s+or\s+', effect_raw)
    effect_parts = [e.strip() for e in effect_parts if e.strip()]

    cause_node = fuzzy_match(cause, nodes_lower)
    effect_nodes = [fuzzy_match(e, nodes_lower) for e in effect_parts]
    effect_nodes = [n for n in effect_nodes if n is not None]

    print(f"[Validator] cause_node={cause_node} | effect_nodes={effect_nodes}")

    # ---- Verdict: pure graph-based, language-agnostic, no keyword heuristics ----
    # Chain:  X→Z→Y → has_path(X,Y)=True  → Yes (X causes Y through Z)
    # Fork:   Z→X, Z→Y → has_path(X,Y)=False → No  (X does not cause Y)
    # Collider: X→Z←Y → has_path(X,Y)=False → No  (X and Y are independent causes)
    if cause_node and effect_nodes:
        all_paths_exist = all(nx.has_path(G, cause_node, en) for en in effect_nodes)
        computed_verdict = "yes" if all_paths_exist else "no"
    else:
        computed_verdict = "no"
        print("[Validator] 实体匹配失败, verdict默认为no")

    print(f"[Validator] VERDICT={computed_verdict} | has_path")

    # ---- FMEA scan ----
    for edge in graph_data.edges:
        scorer = FmeaScore(edge.S, edge.O, edge.D)
        rpn = scorer.calculate_rpn()
        if rpn > 500:
            print(f"[Validator] FMEA高危: {edge.source}->{edge.target} RPN={rpn}")

    # ---- Rust: Kahn + d-separation ----
    with AgentContext() as rust_engine:
        rust_engine.inject_edges(py_edges)
        topology_safe = rust_engine.check_graph_health()
        print(f"[Validator] Kahn: {'OK' if topology_safe else 'FAIL(环路)'}")

        if not topology_safe:
            return {
                "causal_verdict": computed_verdict,
                "rust_interception_report": "Cycle detected. Fix the loop.",
                "is_safe": False,
                "d_separation_claims": [],
                "current_phase": "validate_graph",
                "interception_count": interception_count + 1
            }

        real_claims = rust_engine.extract_testable_claims()
        print(f"[Validator] d-分离断言数={len(real_claims)}")
        for c in real_claims:
            print(f"  -> {c[:150]}")

        if real_claims:
            report_msg = "D-separation claims extracted. Forwarding to Reflector."
            is_finally_safe = False
        else:
            report_msg = ""
            is_finally_safe = True

        return {
            "causal_verdict": computed_verdict,
            "is_safe": is_finally_safe,
            "d_separation_claims": real_claims,
            "rust_interception_report": report_msg,
            "current_phase": "validate_graph",
            "interception_count": interception_count
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
    print(f"[Reflector] 审查 {len(claims)} 条断言...")

    system_prompt = """You are a common-sense judge. The system extracted a causal graph and derived d-separation claims. Judge: are any of these claims ABSURD?

- "X and Y are completely independent" — REJECT only if the real world clearly links them.
- "Controlling Z, X has no effect on Y" — this is a CONDITIONAL statement. If Z is a common cause of X and Y, this is MATHEMATICALLY VALID → PASS.
- Only REJECT claims that violate basic common sense (e.g., "rooster crowing causes sunrise").
- When in doubt, PASS.

Output JSON: {"verdict": "REJECT or PASS", "reason": "brief reason"}"""

    user_prompt = f"D-Separation Claims:\n{claims_text}\n\nAny absurd claims? If not, PASS."

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
