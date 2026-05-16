# 文件：python/causal_fmea/app.py
from langgraph.graph import StateGraph, START, END
from pprint import pprint

# 引入我们在前线打磨好的装甲和弹药
from agent_state_machine import CausalAgentState
from nodes import generate_graph_node, validate_graph_node

# ==========================================
# ⚡️ 核心算子：上帝视角的“铁面路由” (Conditional Router)
# 它决定了 Validator 验伤完毕后，数据该往哪走！
# ==========================================
def should_continue(state: CausalAgentState) -> str:
    """
    检查病历本，决定是完美结案、强制熔断，还是时光倒流！
    """
    is_safe = state.get("is_safe", False)
    interception_count = state.get("interception_count", 0)

    # 结局 1：完美通关
    if is_safe:
        print("🟢 [路由决策] 测谎仪放行！因果图完美无瑕，直接结案！")
        return "finish"
    
    # 结局 2：物理熔断 (保护 4060 显存免遭无限死循环)
    if interception_count >= 3:
        print(f"🔴 [致命熔断] 大模型已连续发癫 {interception_count} 次！强制拔电源，结束推演！")
        return "finish"

    # 结局 3：时光倒流 (踹回起点重做)
    print(f"🟡 [路由决策] 测谎仪拦截！开启时光倒流，将大模型踹回 Generator 进行第 {interception_count + 1} 次重试！")
    return "generate_graph"

# ==========================================
# 🛠️ 开始焊接：组装 LangGraph 状态机
# ==========================================
print("⚙️ [系统组装] 正在焊接因果推理流水线...")

# 1. 创建基于我们病历本的空图纸
builder = StateGraph(CausalAgentState)

# 2. 挂载两个干活的车间 (Nodes)
builder.add_node("generate_graph", generate_graph_node)
builder.add_node("validate_graph", validate_graph_node)

# 3. 焊接正向单行道 (Edges)
builder.add_edge(START, "generate_graph")               # 起点 -> Generator
builder.add_edge("generate_graph", "validate_graph")    # Generator -> Validator

# 4. 🌟 焊接反向齿轮与出口 (Conditional Edges)
builder.add_conditional_edges(
    "validate_graph",  # 从 Validator 出来后...
    should_continue,   # 交给路由函数去判断...
    {
        "generate_graph": "generate_graph", # 如果返回这个，踹回起点
        "finish": END                       # 如果返回 finish，流水线彻底终止！
    }
)

# 5. 浇筑成型：把图纸编译成可执行的图引擎！
causal_agent = builder.compile()
print("✅ [系统就绪] EdgeThemis 引擎组装完毕！防爆舱舱门已锁死！")


# ==========================================
# 🚀 实战点火：高危场景推演测试
# ==========================================
if __name__ == "__main__":
    # 这是一个极其容易诱发大模型产生“伪相关 (Confounder)”的经典测试用例
    test_scenario = """
    案发现场报告：
    昨天晚上发生了一起离奇的事件。记录显示，市区的冰激凌销量突然暴增。
    与此同时，水库发生了多起市民溺水事件。
    请提取这其中的因果关系。
    """
    
    # 初始化一本干净的病历本
    initial_state = {
        "scenario_description": test_scenario,
        "current_phase": "start",
        "extracted_graph": None,
        "rust_interception_report": "",
        "interception_count": 0,
        "is_safe": False
    }

    print("\n" + "="*50)
    print("🚀 开始注入测试数据，启动大模型与 Rust 跨界审判...")
    print("="*50 + "\n")

    # 启动履带！用 stream 模式可以看到数据流转的每一步

    final_state_data = None

    for output in causal_agent.stream(initial_state):
        for key, value in output.items():
            print(f"📦 [流水线进度] 当前刚刚跑完车间: {key}")
            # print(f"当前病历本状态: {value}")

    print("\n🎉 [推演结束] 最终的病历本状态：")
    # 打印被我们拦截下来的最终数据
    pprint(final_state_data)