import pandas as pd
from openai import OpenAI
import re
from app import run_edgethemis_pipeline

# ==========================================
# 裸跑 Baseline：直接问 LLM
# ==========================================
client = OpenAI(base_url="http://127.0.0.1:8080/v1", api_key="sk-no-key")

def ask_barebone_llm(question: str) -> str:
    prompt = (
        f"Question: {question}\n"
        "Output exactly one line: <FINAL_ANSWER> Yes or <FINAL_ANSWER> No"
    )
    try:
        response = client.chat.completions.create(
            model="qwen2.5",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0, max_tokens=16
        )
        text = response.choices[0].message.content.lower().strip()
        match = re.search(r"<final_answer>\s*(yes|no)", text)
        return match.group(1) if match else "no"
    except:
        return "no"

# ==========================================
# EdgeThemis 评测：极简 — 只看 is_safe + causal_verdict
# ==========================================
def ask_edgethemis(question: str) -> str:
    try:
        final_state = run_edgethemis_pipeline(question)

        # If pipeline rejected or melted down → conservative "no"
        if not final_state.get("is_safe", False):
            print(f"  [EdgeThemis] 流水线拒绝/熔断 → no")
            return "no"

        # Use the Validator's computed verdict from the state
        verdict = final_state.get("causal_verdict", "").strip().lower()
        if verdict in ("yes", "no"):
            print(f"  [EdgeThemis] Validator判决={verdict}")
            return verdict
        return "no"
    except Exception as e:
        print(f"  [EdgeThemis] 异常: {e}")
        return "no"

# ==========================================
# 主评测循环
# ==========================================
def evaluate_csv(csv_path: str):
    print(f"\n{'='*60}\n评测: {csv_path}\n{'='*60}")
    df = pd.read_csv(csv_path)
    total = len(df) * 2
    bare_correct, edge_correct, processed = 0, 0, 0

    for idx, row in df.iterrows():
        for q_col, gold_col, label in [
            ("Causal_Relation_1", "Conclusion_1", "A"),
            ("Causal_Relation_2", "Conclusion_2", "B")
        ]:
            q = str(row[q_col])
            gold = str(row[gold_col]).strip().lower()
            print(f"\n[#{idx+1}-{label}] {q[:100]}...")

            b = ask_barebone_llm(q)
            e = ask_edgethemis(q)

            if b == gold: bare_correct += 1
            if e == gold: edge_correct += 1
            processed += 1

            print(f"  裸跑: {b.upper()} | EdgeThemis: {e.upper()} | 标准: {gold.upper()}")
            print(f"  进度 [{processed}/{total}] | 裸跑={bare_correct} | EdgeThemis={edge_correct}")

    return (bare_correct / total) * 100, (edge_correct / total) * 100

if __name__ == "__main__":
    for csv_file in [
        "../../../test_data/Causal_Pairs_Confounder.csv",
        "../../../test_data/Causal_Pairs_Chain.csv",
        "../../../test_data/Causal_Pairs_Collider.csv",
    ]:
        try:
            b_acc, e_acc = evaluate_csv(csv_file)
            print(f"\n{'='*60}")
            print(f"成绩: 裸跑={b_acc:.1f}% | EdgeThemis={e_acc:.1f}%")
            print(f"{'='*60}")
        except Exception as e:
            print(f"评测中断: {e}")
