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
    你是一个通用因果推理引擎。你的任务是从文本中提取完整的因果拓扑图。因果图由以下三种基本结构组成：

    结构一（链 Chain）：A 导致 B，B 导致 C。提取时不可合并跳跃——文本中描述了几个传导步骤，你就必须输出几条边。禁止跳过中间环节直接从 A 画到 C。

    结构二（共同原因 Confounder）：同一个原因 C 同时导致了多个结果。当多个事件在文本中被描述为同时发生或紧密关联时，考察它们是否共享一个隐藏的共同原因。

    结构三（对撞 Collider）：多个独立原因分别汇聚到同一个结果。当文本描述多个看似无关的因素共同促成了某一结果时，分别提取每条汇聚路径。

    一个完整的因果图通常同时包含以上三种结构。你需要提取文本中存在的所有结构。

    【提取规则】
    1. 只提取文本中明确描述的因果关系，不可凭空推测。
    2. 每个节点必须代表一个事件或状态变化，不能是静态的实体名称或人名。实体只有在执行动作或发生状态改变时才构成节点。
    3. 每条边的 description 字段用一句话解释传导机制。
    4. 因果链必须包含从初始原因到中间传导再到最终结果的全部环节，不能跳过中间步骤。

    【FMEA 评分标准（S/O/D 各为 1-10 整数，禁止集中在中间段）】

    严重度 S（该边的后果有多严重）：
    1 = 几乎无影响的微小扰动
    2 = 极轻微的不便或异常
    3 = 轻微的局部影响
    4 = 明显的局部影响，可快速恢复
    5 = 局部功能降级或明显报错
    6 = 部分功能丧失，需外部干预才能恢复
    7 = 关键功能严重受损
    8 = 系统接近瘫痪，造成重大损失
    9 = 系统性的严重灾难，不可逆的重大损失
    10 = 危及生命或组织彻底崩溃

    频度 O（在给定前置条件下，该边发生的可能性）：
    1 = 极端罕见，几乎不可能发生
    2 = 非常罕见，需要极端巧合
    3 = 罕见，需要多种条件同时满足
    4 = 较少发生，仅在特定场景下出现
    5 = 偶发，在特定条件下会反复出现
    6 = 较频繁，在常见条件下就可能出现
    7 = 频繁发生
    8 = 非常频繁，几乎常态化
    9 = 在给定条件下几乎必然发生
    10 = 只要前置条件满足就绝对发生

    探测度 D（该边代表的因果传导在发生前或发生时能否被察觉）：
    1 = 可被现有监控或感知手段瞬间明确捕捉
    2 = 通过常规检查即可发现
    3 = 需要通过专项检查才能发现
    4 = 有一定滞后性，需事后排查才能确认
    5 = 需要专门排查分析才能发现
    6 = 较难发现，需要深入调查
    7 = 很难发现，需要专业工具或专业知识
    8 = 极难发现，需要特殊手段
    9 = 几乎无法在事前探测
    10 = 完全无法预知或探测
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
            max_tokens=2048,
            temperature=0.1
        )

        raw_json_str = response.choices[0].message.content

        # 尝试直接解析
        try:
            extracted_data = ExtractedGraph.model_validate_json(raw_json_str)
        except ValidationError:
            # 常见失败模式：模型在 JSON 外包了 markdown 代码块 ```json ... ```
            if "```" in raw_json_str:
                cleaned = raw_json_str.split("```json")[-1].split("```")[0].strip()
                if cleaned:
                    extracted_data = ExtractedGraph.model_validate_json(cleaned)
                else:
                    raise
            else:
                raise

        # 去重：3B 等小模型可能重复生成同一条边
        seen = set()
        unique_edges = []
        for edge in extracted_data.edges:
            key = (edge.source, edge.target)
            if key not in seen:
                seen.add(key)
                unique_edges.append(edge)
        extracted_data.edges = unique_edges

        return {
            "current_phase": "generate_graph",
            "extracted_graph": extracted_data
        }

    except ValidationError as e:
        print(f"💥 [解析崩溃] Pydantic 校验失败：{str(e)[:200]}")
        print(f"📄 [原始输出（前300字符）] {raw_json_str[:300]}")
        return {
            "rust_interception_report": f"JSON 格式不符，请严格遵循 schema。错误：{str(e)[:150]}",
            "interception_count": interception_count + 1
        }
    except Exception as e:
        print(f"💥 [网络异常] 无法连接到底层 C++ 引擎：{str(e)}")
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
            "current_phase": "validate_graph",
            "interception_count": state.get("interception_count", 0) + 1
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
            return {
                "is_safe": False,
                "d_separation_claims": [],
                "rust_interception_report": "🚨 [拓扑错误] Rust 底层引擎检测到逻辑死循环！",
                "current_phase": "validate_graph",
                "interception_count": state.get("interception_count", 0) + 1
            }
        elif real_claims:
            print(f"⚠️ [逻辑破绽] 检测到因果图涉嫌伪独立，移交 Reflector 车间执行常识盘问！")
            return {
                "is_safe": False,
                "d_separation_claims": real_claims,
                "rust_interception_report": "⚠️ [逻辑破绽] 检测到因果图涉嫌伪独立，移交 Reflector 车间执行常识盘问！",
                "current_phase": "validate_graph",
                "interception_count": state.get("interception_count", 0)
            }
        else:
            return {
                "is_safe": True,
                "d_separation_claims": [],
                "rust_interception_report": "",
                "current_phase": "validate_graph",
                "interception_count": state.get("interception_count", 0)
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

    print(f"🕵️ [前额叶重塑] 赋予 Qwen 2.5 铁面审查官人格，开始终极质问（共 {len(claims)} 条断言）...")

    claims_text = "\n".join([f"断言 {i+1}: {claim}" for i, claim in enumerate(claims)])

    system_prompt = """
    你是一个理智、宽容且客观的因果审查员。
    现在有一些基于因果图推导出的统计推断，每条推断末尾都带有一个问句。请逐一判断：这条推断在现实世界中是否合理？

    【判决标准】
    1. 如果这条推断在现实中明显荒谬（例如要求你相信两件显然相关的事在统计上独立），REJECT。
    2. 如果这条推断在现实中存在争议、但至少有一面说得通，PASS。
    3. 不要因为"现实中很少有绝对独立的事"这种泛泛理由而 REJECT——你必须找到这条推断中具体的、不合理的点才能 REJECT。

    你必须输出标准的 JSON 格式：
    {
      "verdict": "REJECT" 或 "PASS",
      "reason": "言简意赅的判决理由"
    }
    """

    user_prompt = f"【待审查的图结构推断】\n{claims_text}\n\n请逐一回答每条推断末尾的问句。如果所有推断在现实中都合理，给出 PASS；只要有一条明显不合理，给出 REJECT 并说明哪条触犯了什么常识。"

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
            print(f"🔴 [逻辑自爆] 大模型无法说服自己的常识！反思反驳理由：{res_json.get('reason')}")
            return {
                "is_safe": False,
                "rust_interception_report": f"你的因果图推导出了荒谬的物理断言！反思结论：{res_json.get('reason')}",
                "current_phase": "reflector",
                "interception_count": interception_count + 1
            }

        print(f"🟢 [反思通过] 大模型的图谱成功说服了自己的常识神经！")
        return {"is_safe": True, "current_phase": "reflector"}

    except Exception as e:
        print(f"💥 [审讯室暴乱] 法官异常：{str(e)}")
        return {
            "is_safe": False,
            "rust_interception_report": "你在反思阶段输出了不符合规范的格式或连接失败，请严格按照要求重新提取！",
            "current_phase": "reflector",
            "interception_count": interception_count + 1
        }