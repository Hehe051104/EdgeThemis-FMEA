# 文件：python/causal_fmea/nodes.py
import json
from typing import Dict, Any
from pydantic import ValidationError
from openai import OpenAI  # 🌟 全新雷达：标准的 OpenAI 客户端！再见，沉重的 llama_cpp！

from agent_state_machine import CausalAgentState, ExtractedGraph, ReflectorVerdict
from context_guard import AgentContext
from causal_fmea_core import FmeaScore

# ==========================================
# 🌟 物理动作 0：建立与底层 C++ 引擎的 HTTP 通讯虫洞
# ==========================================
print("📡 [雷达校准] 正在连接本地 8080 端口的 llama-server...")
# 这里的 base_url 必须对齐 run_llama_server.sh 暴露的端口
client = OpenAI(
    base_url="http://127.0.0.1:8080/v1", 
    api_key="edge_themis_key" # 本地部署，随便填，但不可为空
)

# 注意：我们彻底删除了 llm = Llama(...) 和 LlamaGrammar 的编译代码！
# 现在 4060 的 8GB 显存是纯净的，全权交给后台的 C++ 进程管理！


def generate_graph_node(state: CausalAgentState) -> Dict[str, Any]:
    """
    LangGraph 的 Generator 节点：负责暴力榨取因果图
    """
    scenario = state.get("scenario_description", "")
    rust_report = state.get("rust_interception_report", "")
    interception_count = state.get("interception_count", 0)

    system_prompt = """
    你是一个极其严苛的通用工业因果推理引擎（EdgeThemis）。你的任务是从案发现场提取绝对的因果拓扑图，适用于任何领域（医疗、机械、软件、金融等）。
    
    【绝对法则：打破单线思维，寻找拓扑分叉】
    当发现事件 A 和事件 B 同时发生或紧密相连时，必须采取怀疑态度！
    绝大多数情况下，真实世界不是简单的单向链条。你必须寻找隐藏的【共同原因 (Confounder) C】，并构建分叉网络：[C -> A] 且 [C -> B]。

    【格式输出的铁血禁令（绝对遵守）】
    1. 你必须先在 reasoning_process 里进行强制的结构化思考，必须包含以下两段：
       - "结构排查：" 明确说明是否存在导致多个并发症状的幕后环境/前置条件。
       - "传导分析：" 明确说明物理/逻辑的传导链条是如何一步步崩溃的。
    2. edges 字段里提取出的 source 和 target 必须是具体的中文名词！绝对禁止出现 "->" 符号！
    3. FMEA 评分 (S, O, D) 必须是 1-10 的整数，严禁所有边给出相同的敷衍分数！

    【通用 FMEA 绝对物理标尺（跨越一切领域的相对刻度）】
    - S (严重度): 1=微小的扰动或异常，不影响全局；5=局部系统降级或明显报错；10=系统性的毁灭、生命危险或灾难级的商业崩溃。
    - O (频度): 1=极端罕见（黑天鹅事件）；5=在特定条件下偶发；10=只要前置条件满足，就必然发生（物理定律级的确定性）。
    - D (探测度): 1=被自动化监控或人类感官瞬间且明确地捕捉；5=有滞后性，需专门排查才能发现；10=彻底的盲区，完全无法被现有手段提前预警。
    """

    user_prompt = f"【待分析场景】\n{scenario}\n\n请提取因果图谱。"
    
    if rust_report:
        user_prompt += (
            f"\n\n🚨【系统严重警告】🚨\n"
            f"你上一次提交的因果图被底层的 Rust d-分离测谎仪拦截！\n"
            f"拦截报告：{rust_report}\n"
            f"请仔细反思并修正上述虚假的混淆因子或环路，重新输出！"
        )
        print(f"🔄 [动态纠错] 大模型正在进行第 {interception_count} 次强制反思...")

    try:
        # ⚡️ 致命重构：向后台 C++ 引擎发射网络请求！
        response = client.chat.completions.create(
            model="qwen2.5", # llama-server 不看名字，但标准 API 必须传
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            # 🌟 原生支持！直接将 Pydantic 转换为 JSON Schema 枷锁传给服务器！
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
        
        # 获取返回的字符串 (注意 openai 客户端的数据结构变了，用 .属性 访问)
        raw_json_str = response.choices[0].message.content
        
        extracted_data = ExtractedGraph.model_validate_json(raw_json_str)
        
        return {
            "current_phase": "generate_graph", 
            "extracted_graph": extracted_data
        }
        
    except ValidationError as e:
        print("💥 [解析崩溃] 模型输出了乱码，强制要求重试。")
        return {
            "rust_interception_report": f"JSON 语法损坏，请严格遵守格式：{str(e)}",
            "interception_count": interception_count + 1
        }
    except Exception as e:
        print(f"💥 [网络异常] 无法连接到底层 C++ 引擎：{str(e)}")
        # 假设服务器没开，或者超时，直接报错
        return {
            "rust_interception_report": "无法连接到 llama-server，请检查底层进程！",
            "interception_count": interception_count + 1
        }
    

# -------------------------------------------------------------------------------------------
# validate_graph_node 没有任何大模型调用，纯粹是 Rust FFI，所以【一行代码都不需要改】！
# 为节省篇幅，这里保留你原有的 validate_graph_node 完整代码。
# 你直接保留原来的 validate_graph_node 即可，它依然完美工作。
# -------------------------------------------------------------------------------------------
def validate_graph_node(state: CausalAgentState) -> Dict[str, Any]:
    print("⚖️ [死神审判] 数据正在通过 FFI 虫洞，进入 Rust 物理测谎仪...")
    
    graph_data = state.get("extracted_graph")
    interception_count = state.get("interception_count", 0)

    if not graph_data or not graph_data.edges:
        return {
            "rust_interception_report": "大模型吐出的图谱为空，涉嫌逃避推演！",
            "is_safe": False,
            "current_phase": "validate_graph"
        }

    py_edges = [(edge.source, edge.target) for edge in graph_data.edges]
    fmea_alerts = []
    print("📡 [FMEA 雷达] 正在跨界调用 Rust 算力计算边缘 RPN 指数...")
    
    for edge in graph_data.edges:
        scorer = FmeaScore(edge.S, edge.O, edge.D)
        rpn = scorer.calculate_rpn() 
        if rpn > 500:
            fmea_alerts.append(f"【高危 RPN】{edge.source} -> {edge.target} (RPN={rpn})")
        if edge.S >= 9:
            fmea_alerts.append(f"【致命单点】{edge.source} -> {edge.target} (S={edge.S})")

    if fmea_alerts:
        print(f"\n⚠️ ⚠️ ⚠️ [高危警报] 发现 {len(fmea_alerts)} 处极高风险因果链路！")
        for alert in fmea_alerts:
            print(f"  -> {alert}")
        print("="*50 + "\n")

    with AgentContext() as rust_engine:
        rust_engine.inject_edges(py_edges)
        topology_safe = rust_engine.check_graph_health()
    
        is_safe = topology_safe 

        report_lines = []
        if not topology_safe:
            report_lines.append("🚨 [拓扑错误] Rust 底层引擎检测到逻辑死循环（A导致B，B又导致A）！请严谨反思！")
            
        interception_report = "\n".join(report_lines) if not is_safe else ""
        
        if not is_safe:
            print(f"🔴 [拒绝放行] 发现致命错误，已生成拦截报告，准备触发时光倒流！")

        real_claims = []
        if topology_safe:
            print("🔬 [测谎仪启动] Rust 正在执行 O(N^3) 贝叶斯球探测，试图提取常识破绽...")
            real_claims = rust_engine.extract_testable_claims()
            if real_claims:
                print(f"🎯 [破绽锁定] Rust 成功提取出 {len(real_claims)} 条物理断言！")

        if not topology_safe:
            report_msg = "🚨 [拓扑错误] Rust 底层引擎检测到逻辑死循环！"
            is_finally_safe = False
        elif real_claims:
            report_msg = "⚠️ [逻辑破绽] 检测到因果图涉嫌伪独立，移交 Reflector 车间执行常识盘问！"
            is_finally_safe = False
        else:
            report_msg = ""
            is_finally_safe = True

        return {
            "is_safe": is_finally_safe,
            "d_separation_claims": real_claims,
            "rust_interception_report": report_msg,
            "current_phase": "validate_graph",
            "interception_count": state.get("interception_count", 0) + (1 if not is_finally_safe else 0) 
        }

# -------------------------------------------------------------------------------------------

def reflector_node(state: CausalAgentState) -> Dict[str, Any]:
    """
    LangGraph 的 Reflector 节点：
    用大模型脆弱的常识，去审判它自己用图论画出的伪命题
    """
    claims = state.get("d_separation_claims", [])
    interception_count = state.get("interception_count", 0)
    
    if not claims:
        return {"is_safe": True, "current_phase": "reflector"}

    print(f"🕵️ [前额叶重塑] 赋予 Qwen 2.5 铁面审查官人格，开始终极质问...")
    
    claims_text = "\n".join([f"断言 {i+1}: {claim}" for i, claim in enumerate(claims)])
    
    system_prompt = """
    你是一个理智、宽容且极其客观的现实世界审查法官。
    现在有系统基于拓扑图提取了几条物理因果断言。请判断这些断言是否违背现实常识。
    
    【核心判决铁律 - 绝对遵守】
    1. 除非该断言包含了极其荒谬、严重违背地球基本物理法则的陈述（例如“公鸡打鸣导致太阳升起”、“求神拜佛导致疾病痊愈”这类绝对的伪科学），否则你必须给出 PASS！
    2. 不要过度发散思维！绝对禁止脑补微小的、间接的蝴蝶效应！
    3. 如果该断言是探讨“控制某个共同变量（环境/背景）后，另外两个表面相关的变量互不干涉”，这在统计学和常识上是合理的，必须无条件 PASS！
    
    你必须输出标准的 JSON 格式：
    {
      "verdict": "REJECT" 或 "PASS",
      "reason": "言简意赅的反驳或赞同理由"
    }
    """
    
    user_prompt = f"【待审判的物理断言列表】\n{claims_text}\n\n请问上述断言在真实世界中能站得住脚吗？请给出你的判决。"

    try:
        # ⚡️ 致命重构：同样转换为网络请求！
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
            print(f"🔴 [逻辑自爆] 大模型无法说服自己的常识！反思反驳理由：{res_json.get('reason')}")
            return {
                "is_safe": False,
                "rust_interception_report": f"你的因果图推导出了荒谬的物理断言！反思结论：{res_json.get('reason')}",
                "current_phase": "reflector"
            }
        
        print(f"🟢 [反思通过] 大模型的图谱成功说服了自己的常识神经！")
        return {"is_safe": True, "current_phase": "reflector"}

    except Exception as e:
        # 补全了上一轮讨论的安全机制！绝不让模型裸奔！
        print(f"💥 [审讯室暴乱] 法官输出乱码或网络断开，强制要求重新审判：{str(e)}")
        return {
            "is_safe": False,
            "rust_interception_report": "你在反思阶段输出了不符合规范的格式或连接失败，请严格按照要求重新提取！",
            "current_phase": "reflector",
            "interception_count": interception_count + 1
        }