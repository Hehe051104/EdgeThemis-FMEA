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
    5. 文本中若存在多个独立的致因因素，必须分别提取为独立的因果路径。禁止将并行的独立原因强行串联成单一链条。例如：若A和B各自独立导致C，应输出 A→C 和 B→C 两条边（Collider结构），而非 A→B→C。
    6. 完整的因果图应同时包含 Chain（链）、Confounder（共同原因）、Collider（对撞）三种结构。如果提取结果只有一条线性链，大概率遗漏了并行路径或汇聚节点。
    7. 每个节点必须是具体的、可验证的事件或决策，禁止使用笼统的概括性描述（如"未进行风险控制"、"管理失误"、"系统性问题"）。差的节点："安全管理失效"；好的节点："消防通道被货物堵塞"。差的节点："成本削减导致问题"；好的节点："管理层驳回紧急采购申请"。

    【FMEA 评分标准（S/O/D 各为 1-10 整数）】
    评分必须严格区分各边的差异性。不同传导环节的严重度、发生频率和可探测度必然不同，禁止所有边使用相同或相近的分数。一条因果链中，至少应出现 3 种不同的 S 值、3 种不同的 O 值、3 种不同的 D 值。评分是对每条边独立思考的结果，不是批量赋值。

    严重度 S（该因果传导步骤的直接后果有多严重）：
    1-2 = 微小偏差或轻微不便，不影响核心功能（如：数据格式微调、界面显示偏差）
    3-4 = 局部异常，可自动恢复或快速修复（如：单次日志错误、临时性能波动）
    5-6 = 明显功能受损，需要人工干预才能恢复（如：部分服务降级、数据质量下降）
    7-8 = 关键功能严重受损，造成实质损失（如：业务中断、大规模数据错误、合规违规）
    9-10 = 灾难性后果，不可逆的重大损失（如：人员伤亡、组织崩溃、系统性安全失效）

    频度 O（在前置条件已满足的情况下，该传导步骤实际发生的可能性）：
    1-2 = 极罕见，需要极端巧合才会触发（如：多个独立低概率事件同时发生）
    3-4 = 少见，仅在特定不利条件下出现（如：特定配置错误 + 特定负载）
    5-6 = 偶发至较频繁，在正常运营中会周期性出现（如：每月数次的人为疏忽）
    7-8 = 高频，在给定条件下几乎常态化（如：每天都会触发的系统性偏差）
    9-10 = 确定性事件，前置条件满足后必然发生（如：物理定律、确定性逻辑错误）

    探测度 D（该传导步骤在后果发生前或发生时被察觉的难度）：
    1-2 = 明显异常，常规监控或肉眼即可发现（如：大面积报错、用户直接投诉）
    3-4 = 需要关注才能发现，但通过常规检查可捕获（如：日志中的异常模式、周期性报表）
    5-6 = 需要专项排查或深入分析才能发现（如：需要对比历史数据、需要专业领域知识）
    7-8 = 极难发现，需要特殊工具或事后复盘（如：隐性算法偏差、跨系统级联效应）
    9-10 = 事前几乎无法探测（如：从未被定义过的新型风险模式、无先验知识的黑箱行为）
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
            max_tokens=8192,
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
            "extracted_graph": extracted_data,
            "best_graph": extracted_data  # 每次成功生成都保留一份，熔断时兜底返回
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
    你是一个严谨的因果审查员。你的职责是审查因果图推导出的统计推断是否在现实中成立。

    现在有一些基于因果图推导出的统计推断，每条推断末尾都带有一个问句。请审查：这条推断在现实世界中是否成立？

    【判决标准】
    REJECT 条件——只在以下结构性错误时拒绝：
    1. 推断声称两件现实中明显相关的事件独立（例如：同一事故的两个直接原因被声称互不影响）。
    2. 推断遗漏了文本中明确描述的因果关联（例如：文本说 A 和 B 共同导致 C，但推断声称 A 和 B 独立）。
    3. 推断中的独立性违背该领域的基本常识。

    PASS 条件——以下情况应放行：
    1. 推断在现实中可能成立，即使你无法完全确认。
    2. 你的质疑仅涉及"描述不够详细"或"因果机制不够具体"——这不是结构性错误，应放行。
    3. 你找不到基于具体事实的反驳理由。

    注意："因果机制描述模糊"不是拒绝理由。只关注图结构层面的逻辑错误。

    你必须输出标准的 JSON 格式：
    {
      "verdict": "REJECT" 或 "PASS",
      "reason": "言简意赅的判决理由"
    }
    """

    user_prompt = f"【待审查的图结构推断】\n{claims_text}\n\n请严格审查每条推断。你的默认立场是 REJECT——只有当你找不到任何具体反驳理由时才给出 PASS。如果所有推断都经得起审查，给出 PASS；只要有一条存在疑点，给出 REJECT 并指出具体是哪条、违背了什么事实或常识。"

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