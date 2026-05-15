# 文件：python/causal_fmea/nodes.py
import json
from typing import Dict, Any
from llama_cpp import Llama
from llama_cpp.llama_grammar import LlamaGrammar
from pydantic import ValidationError

from .agent_state_machine import CausalAgentState, ExtractedGraph

# ==========================================
# 物理动作 0：在 4060 上点火 (单例加载，防止重复爆显存)
# ==========================================
print("🔥 [硬件预热] 正在将 4-bit 模型权重载入 8GB VRAM...")
# 这里的模型路径请替换为你下载的 GGUF 模型文件
llm = Llama(
    model_path="../../qwen2.5.gguf",
    n_gpu_layers=-1,       # 绝对指令：把所有层强制塞进 4060 显存！
    n_ctx=2048,            # 锁死上下文窗口，防止 KV Cache 膨胀导致 OOM
    verbose=False          # 关闭底层 C++ 的啰嗦日志
)

#  祭出物理枷锁：将 Pydantic 结构直接编译为底层 C++ 的 GBNF 语法树
graph_grammar = LlamaGrammar.from_pydantic(ExtractedGraph)


def generate_graph_node(state: CausalAgentState) -> Dict[str, Any]:
    """
    LangGraph 的 Generator 节点：负责暴力榨取因果图
    """
    scenario = state.get("scenario_description", "")
    rust_report = state.get("rust_interception_report", "")
    interception_count = state.get("interception_count", 0)

    # 1. 构造冷酷无情的系统人格
    system_prompt = (
        "你是一个冷酷、没有感情的物理因果关系抽取引擎。"
        "你的唯一任务是阅读场景描述，提取出所有隐藏的因果边（A导致B），并对严重度(S)、频度(O)、探测度(D)进行1-10的评估。"
        "严格遵守 JSON 格式输出，绝对禁止输出任何解释性文字！"
    )

    # 2. 动态组装用户指令 (完美融合 Generator 与 Reflector 逻辑)
    user_prompt = f"【待分析场景】\n{scenario}\n\n请提取因果图谱。"
    
    if rust_report:
        # 如果病历本里有 Rust 测谎仪的报错，直接把这巴掌拍在模型脸上！
        user_prompt += (
            f"\n\n🚨【系统严重警告】🚨\n"
            f"你上一次提交的因果图被底层的 Rust d-分离测谎仪拦截！\n"
            f"拦截报告：{rust_report}\n"
            f"请仔细反思并修正上述虚假的混淆因子或环路，重新输出！"
        )
        print(f"🔄 [动态纠错] 大模型正在进行第 {interception_count} 次强制反思...")

    # 3. 执行物理级推理 (戴着口罩说话)
    try:
        response = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            grammar=graph_grammar,  # ⚡️ 致命枷锁：不符合 JSON 结构的概率当场清零！
            max_tokens=512,
            temperature=0.1         # 极限降温，剥夺模型的创造力，只求稳定
        )
        
        raw_json_str = response["choices"][0]["message"]["content"]
        
        # 4. 验证并装入病历本
        extracted_data = ExtractedGraph.model_validate_json(raw_json_str)
        
        return {
            "current_phase": "validate_graph", # 流水线推向下一步：验伤！
            "extracted_graph": extracted_data
        }
        
    except ValidationError as e:
        # 极小概率下，如果模型依然发癫（通常是量化过狠导致语法崩溃）
        print("💥 [解析崩溃] 模型输出了乱码，强制要求重试。")
        return {
            "rust_interception_report": f"JSON 语法损坏，请严格遵守格式：{str(e)}",
            "interception_count": interception_count + 1
        }