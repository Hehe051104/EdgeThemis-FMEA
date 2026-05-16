# 文件：python/causal_fmea/nodes.py
import json
from typing import Dict, Any
from llama_cpp import Llama
from llama_cpp.llama_grammar import LlamaGrammar
from pydantic import ValidationError

from agent_state_machine import CausalAgentState, ExtractedGraph
from context_guard import AgentContext

from causal_fmea_core import FmeaScore

# ==========================================
# 物理动作 0：在 4060 上点火 (单例加载，防止重复爆显存)
# ==========================================
print("🔥 [硬件预热] 正在将 4-bit 模型权重载入 8GB VRAM...")
# 这里的模型路径请替换为你下载的 GGUF 模型文件
llm = Llama(
    model_path="../../../qwen2.5.gguf",
    n_gpu_layers=-1,       # 绝对指令：把所有层强制塞进 4060 显存！
    n_ctx=2048,            # 锁死上下文窗口，防止 KV Cache 膨胀导致 OOM
    verbose=False          # 关闭底层 C++ 的啰嗦日志
)

# 1. 把 Pydantic 对象降维成标准的 JSON Schema 字典，再转成字符串
schema_json_str = json.dumps(ExtractedGraph.model_json_schema())

# 2. 将字符串狠狠砸进底层的 C++ 语法树编译器！
graph_grammar = LlamaGrammar.from_json_schema(schema_json_str)


def generate_graph_node(state: CausalAgentState) -> Dict[str, Any]:    # 用模型
    """
    LangGraph 的 Generator 节点：负责暴力榨取因果图
    """
    scenario = state.get("scenario_description", "")
    rust_report = state.get("rust_interception_report", "")
    interception_count = state.get("interception_count", 0)

    # 1. 构造冷酷无情的系统人格
    system_prompt = """
    你是一个极其严苛的工业级因果推理引擎（EdgeThemis）。你的任务是从案发现场提取绝对的因果拓扑图。
    
    【绝对法则：寻找隐藏的混淆因子】
    当看到事件 A 和事件 B 同时发生时，绝不能轻易得出 A -> B。
    你必须找出隐藏在幕后的共同原因（例如：环境温度、物理常数、系统前置状态），把它作为源头！

    【格式输出的铁血禁令（绝对遵守）】
    1. 你必须先在 reasoning_process 字段里进行“大声思考（Chain of Thought）”，推演出幕后黑手和所有的中间传导齿轮！
    2. 基于你的思考，再在 edges 字段里提取出源头和目标。source 和 target 必须是具体的中文名词！
    3. 节点名称里绝对禁止出现 "->" 符号！
    4. FMEA 评分 (S, O, D) 必须是 1-10 的整数。

    【FMEA 评分绝对物理标尺（严禁夸大，必须符合真实物理常识）】
    - S (严重度): 1=毫无物理影响(如正常的商业活动/买冰激凌)；5=系统性能降级(如设备发热)；10=车毁人亡/致命灾难(如溺水死亡/爆炸)。
    - O (频度): 1=百年一遇；5=偶发事件；10=每次必然发生。
    - D (探测度): 1=监控雷达瞬间锁定(如温度计测温/销量数据随时可查)；5=有一定滞后；10=隐形刺客/完全盲区。

    【正确的数据格式示范（注意逻辑模式，非当前案件）】
    假如案发现场是“某小学里，学生的鞋码越大，阅读能力越强”。你绝不能说鞋码导致了阅读能力，你找出了幕后黑手“年龄增长”。你应该这样输出：
    边1:
      source: "学生的年龄增长"
      target: "脚部发育导致鞋码变大"
      S: 1, O: 9, D: 1
    边2:
      source: "学生的年龄增长"
      target: "受教育时间长导致阅读能力变强"
      S: 1, O: 8, D: 1
    """

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
            "current_phase": "generate_graph", # 流水线推向下一步：验伤！
            "extracted_graph": extracted_data
        }
        
    except ValidationError as e:
        # 极小概率下，如果模型依然发癫（通常是量化过狠导致语法崩溃）
        print("💥 [解析崩溃] 模型输出了乱码，强制要求重试。")
        return {
            "rust_interception_report": f"JSON 语法损坏，请严格遵守格式：{str(e)}",
            "interception_count": interception_count + 1
        }
    
# -------------------------------------------------------------------------------------------

def validate_graph_node(state: CausalAgentState) -> Dict[str, Any]:   # 用rust
    """
    LangGraph 的 Validator 节点：将数据押送进 Rust 底层进行生死审判
    """
    print("⚖️ [死神审判] 数据正在通过 FFI 虫洞，进入 Rust 物理测谎仪...")
    
    graph_data = state.get("extracted_graph")
    interception_count = state.get("interception_count", 0)

    if not graph_data or not graph_data.edges:
        return {
            "rust_interception_report": "大模型吐出的图谱为空，涉嫌逃避推演！",
            "is_safe": False,
            "current_phase": "validate_graph"
        }

    # 物理动作 1：把 Pydantic 对象降维成极其轻量的 Tuple 列表 [(source, target), ...]
    py_edges = [(edge.source, edge.target) for edge in graph_data.edges]

    fmea_alerts = []
    print("📡 [FMEA 雷达] 正在跨界调用 Rust 算力计算边缘 RPN 指数...")
    
    for edge in graph_data.edges:
        # 召唤 Rust 底层算子，传入大模型给的 S, O, D
        scorer = FmeaScore(edge.S, edge.O, edge.D)
        rpn = scorer.calculate_rpn()  # Rust 极速算出结果
        
        # 铁血规则 1：RPN 爆炸 (比如 > 100)
        if rpn > 500:
            fmea_alerts.append(f"【高危 RPN】{edge.source} -> {edge.target} (RPN={rpn})")
        
        # 铁血规则 2：单点致命 (严重度 S >= 9)
        if edge.S >= 9:
            fmea_alerts.append(f"【致命单点】{edge.source} -> {edge.target} (S={edge.S})")

    # 如果抓到高危边，立刻在终端拉响刺耳的警报！
    if fmea_alerts:
        print(f"\n⚠️ ⚠️ ⚠️ [高危警报] 发现 {len(fmea_alerts)} 处极高风险因果链路！")
        for alert in fmea_alerts:
            print(f"  -> {alert}")
        print("="*50 + "\n")

    # ==========================================
    # 🛡️ 开启绝对物理沙盒！
    # ==========================================
    with AgentContext() as rust_engine:
        rust_engine.inject_edges(py_edges)
        topology_safe = rust_engine.check_graph_health()
    
    # ==========================================
    # 🌟 战术核心：联合绞杀机制！
    # 必须满足两个条件：拓扑无死循环 且 没有任何 FMEA 警报
    # ==========================================
    is_safe = topology_safe 

    # 大模型只有在画出“死循环”时，才会被踹回去重写
    report_lines = []
    if not topology_safe:
        report_lines.append("🚨 [拓扑错误] Rust 底层引擎检测到逻辑死循环（A导致B，B又导致A）！请严谨反思！")
        
    interception_report = "\n".join(report_lines) if not is_safe else ""
    
    # 打印给人类指挥官看
    if not is_safe:
        print(f"🔴 [拒绝放行] 发现致命错误，已生成拦截报告，准备触发时光倒流！")

    # 返回给 LangGraph 状态机
    return {
        "is_safe": is_safe,
        "rust_interception_report": interception_report,
        "current_phase": "validate_graph",
        "interception_count": state.get("interception_count", 0) + 1
    }
    
    # 💥💥💥 缩进结束！这里是全场最爽的一幕：
    # AgentContext 的 __exit__ 瞬间触发！
    # 刚刚还在运转的 Rust 测谎仪被当场销毁，驻留池清空，底层 4060 显存里的垃圾被扫荡一空！
    # 绝不给大模型的下一次重试留下任何内存隐患！

