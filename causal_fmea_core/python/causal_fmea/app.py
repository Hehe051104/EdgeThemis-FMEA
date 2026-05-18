from langgraph.graph import StateGraph, START, END
from pprint import pprint

# 引入我们在前线打磨好的装甲和弹药
from agent_state_machine import CausalAgentState
from nodes import generate_graph_node, validate_graph_node, reflector_node

# ==========================================
# ⚡️ 核心算子 1：Validator (验伤车间) 出口路由
# ==========================================
def route_from_validator(state: CausalAgentState):
    """
    第一道防爆门：检查拓扑环路和 Rust d-分离破绽
    """
    is_safe = state.get("is_safe", False)
    claims = state.get("d_separation_claims", [])
    interception_count = state.get("interception_count", 0)

    # 结局 A：物理熔断 (保护 4060 显存免遭无限死循环)
    if interception_count >= 3:
        print(f"🔴 [致命熔断] 大模型在 Validator 连续发癫 {interception_count} 次！强制拔电源，结束推演！")
        return END

    # 结局 B：拓扑死循环，当场踢回重写
    if not is_safe and not claims:
        print(f"🟡 [路由决策] 拓扑死循环！开启时光倒流，踹回 Generator 进行第 {interception_count + 1} 次重试！")
        return "generate_graph"
    
    # 结局 C：拓扑没问题，但 Rust 查出了伪独立破绽，押送审讯室！
    if claims:
        print(f"🟠 [路由决策] 拓扑正常，但发现 {len(claims)} 条 d-分离破绽！押送至 Reflector 接受常识审判！")
        return "reflector"

    # 结局 D：既没死循环，也没逻辑破绽，完美通关
    print("🟢 [路由决策] 测谎仪放行！因果图完美无瑕，直接结案！")
    return END

# ==========================================
# ⚡️ 核心算子 2：Reflector (审讯车间) 出口路由
# ==========================================
def route_from_reflector(state: CausalAgentState):
    """
    第二道防爆门：检查大模型在常识审判中的认罪态度
    """
    is_safe = state.get("is_safe", False)
    interception_count = state.get("interception_count", 0)

    # 结局 A：物理熔断
    if interception_count >= 3:
        print(f"🔴 [致命熔断] 审讯超时！大模型连续发癫 {interception_count} 次！强制拔电源！")
        return END

    # 结局 B：嫌疑犯防线崩溃，承认画的图违背常识
    if not is_safe:
        print(f"🟡 [路由决策] 嫌疑犯防线崩溃！带着反思报告踹回 Generator 进行第 {interception_count + 1} 次重写！")
        return "generate_graph"

    # 结局 C：嫌疑犯说服了自己（或断言确实合理），结案
    print("🟢 [路由决策] 嫌疑犯通过了常识审判！结案！")
    return END


# ==========================================
# 🛠️ 开始焊接：组装 LangGraph 多体状态机
# ==========================================
print("⚙️ [系统组装] 正在焊接因果推理双重防爆流水线...")

builder = StateGraph(CausalAgentState)

# 1. 挂载三大物理车间
builder.add_node("generate_graph", generate_graph_node)
builder.add_node("validate_graph", validate_graph_node)
builder.add_node("reflector", reflector_node)

# 2. 焊接绝对单行道
builder.add_edge(START, "generate_graph")               # 起点 -> Generator
builder.add_edge("generate_graph", "validate_graph")    # Generator -> Validator

# 3. 🌟 焊接第一道分流阀门 (Validator 出口)
builder.add_conditional_edges(
    "validate_graph",
    route_from_validator,
    {
        "generate_graph": "generate_graph",
        "reflector": "reflector",
        END: END
    }
)

# 4. 🌟 焊接第二道分流阀门 (Reflector 出口)
builder.add_conditional_edges(
    "reflector",
    route_from_reflector,
    {
        "generate_graph": "generate_graph",
        END: END
    }
)

# 5. 浇筑成型！
causal_agent = builder.compile()
print("✅ [系统就绪] EdgeThemis 引擎组装完毕！双重防爆舱门已锁死！")


# ==========================================
# 🚀 实战点火：高危场景推演测试
# ==========================================
if __name__ == "__main__":
    test_scenario = """
    案发现场报告（Legal RAG 边缘微服务节点级联雪崩事件）：
    在昨天下午的业务晚高峰期间，我们的 Legal RAG 法律咨询边缘节点发生了灾难性的级联崩溃。
    监控日志显示，起因是机房空调宕机导致【环境温度极速飙升】。环境温度的飙升不仅让大楼的【烟雾火情报警器】发生误报，同时也让机柜内的【GPU 核心温度】撞破了 95 度的红线。
    GPU 温度撞线后，底层驱动强制触发了【GPU 降频与功耗墙限制】。
    由于算力突然骤降，llama-server 内部的【KV Cache 显存调度】出现严重阻塞，导致正在处理的超长【法律案卷上下文发生静默截断】。
    这种可怕的上下文截断，直接导致 Qwen 2.5 产生了严重的【法理逻辑幻觉】，向多名企业客户输出了【严重违法的税务建议】。
    最终，这些违法的建议不仅引发了潮水般的【客户维权投诉】，还直接导致公司收到了监管部门的【行政处罚巨额罚单】。
    
    请提取这起跨界灾难的因果拓扑图。你必须剥离出环境的混淆干扰，推演出从物理硬件到软件内存，再到最终商业灾难的完整夺命链条！
    """
    
    # 初始化一本极其干净、带有最新字段的病历本
    initial_state = {
        "scenario_description": test_scenario,
        "current_phase": "start",
        "extracted_graph": None,
        "rust_interception_report": "",
        "d_separation_claims": [],  # 🌟 必须初始化这个口袋，用来装 Rust 吐出的破绽
        "interception_count": 0,
        "is_safe": False
    }

    print("\n" + "="*50)
    print("🚀 开始注入测试数据，启动大模型与 Rust 跨界联合审判...")
    print("="*50 + "\n")

    final_extracted_graph = None

    for output in causal_agent.stream(initial_state):
        for node_name, state_update in output.items():
            print(f"📦 [流水线进度] 当前刚刚跑完车间: {node_name}")
            
            if "extracted_graph" in state_update and state_update["extracted_graph"] is not None:
                final_extracted_graph = state_update["extracted_graph"]

    print("\n🎉 [推演结束] EdgeThemis 引擎最终提取的因果图谱：")
    
    if final_extracted_graph:
        pprint(final_extracted_graph.model_dump())
    else:
        print("🚨 提取失败：大模型未生成图谱，或因触发底层物理熔断被强制终止。")