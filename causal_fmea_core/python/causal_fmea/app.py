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

    # 结局 A：物理熔断，返回当前最佳图谱
    if interception_count >= 5:
        print(f"🔴 [熔断] 已尝试 {interception_count} 次，返回当前最佳图谱。")
        return END

    # 结局 B：拓扑死循环，当场踢回重写
    if not is_safe and not claims:
        print(f"🟡 [路由决策] 拓扑死循环！踹回 Generator 进行第 {interception_count + 1} 次重试！")
        return "generate_graph"

    # 结局 C：拓扑没问题，但 Rust 查出了伪独立破绽，押送审讯室！
    if claims:
        print(f"🟠 [路由决策] 拓扑正常，发现 {len(claims)} 条 d-分离破绽！押送至 Reflector！")
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

    # 结局 A：物理熔断，返回当前最佳图谱
    if interception_count >= 5:
        print(f"🔴 [熔断] 已尝试 {interception_count} 次，返回当前最佳图谱。")
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
    案件背景：
    某互联网金融科技公司于2024年3月上线了一套名为"睿聘通"的AI智能招聘筛选系统。该系统使用一个基于深度学习的自然语言处理模型，自动对海量求职者的简历进行打分和排序。系统上线后，公司的人力资源部门将初筛环节完全交由AI处理，HR仅对AI推荐的前百分之五的候选人进行人工面试。

    事件经过：
    2024年9月，一位未被录用的女性求职者张某向当地人力资源和社会保障局投诉，称该公司在招聘过程中存在性别歧视。张某拥有计算机科学硕士学位和五年相关工作经验，其简历在"睿聘通"系统中的得分为三十一分，远低于公司设定的八十分面试阈值。然而，一位与她背景高度相似的男性求职者（同校同专业、同年毕业、工作经历类似）的简历得分却高达八十五分，并顺利进入了面试环节。

    人力资源和社会保障局接到投诉后，依据《中华人民共和国就业促进法》第二十七条（用人单位不得以性别为由拒绝录用妇女或提高录用标准）和《中华人民共和国妇女权益保障法》第四十三条（用人单位在招聘过程中不得有性别歧视行为），对该公司启动了行政调查。

    调查中的关键发现：
    第一，技术层面。调查组委托的第三方算法审计机构发现，"睿聘通"系统的训练数据全部来自该公司过去十年积累的招聘历史记录。在历史记录中，该公司技术岗位的最终录用者中女性仅占百分之十二。由于训练数据中存在严重的性别比例失衡，模型在学习过程中将"性别相关特征"（如简历中出现的特定社团名称、选修课程偏好等）内化为负向权重，导致女性求职者的评分被系统性地压低。这构成了《个人信息保护法》第二十四条所禁止的"利用个人信息进行自动化决策时，对个人实行不合理的差别待遇"。

    第二，组织层面。调查组查阅内部邮件发现，公司CTO在2023年12月（系统开发初期）曾向CEO发送邮件，明确指出训练数据存在性别偏差问题，建议额外采购外部平衡数据集进行校正，预算约为四十万元。CEO以"项目已严重超支，尽快上线是第一优先级"为由驳回了申请。此外，公司在系统上线前没有按照《生成式人工智能服务管理暂行办法》第十七条的要求进行算法备案和安全评估。

    第三，业务流程层面。HR部门在接到多起女性求职者的评分质疑后，未启动人工复核流程，而是以"AI评分是客观的"为由拒绝申诉。直到张某投诉至人社局，公司内部已有累计十七起类似的性别偏差投诉被搁置。

    第四，行业背景。在2024年，多家头部互联网公司均因AI招聘系统存在歧视性偏差而遭到行政处罚。行业媒体在2024年3月至6月期间密集报道了三起类似的AI招聘歧视案，但该公司管理层未对此做出任何风险响应。

    第五，法律后果。人社局调查结束后，依据《就业促进法》第六十二条，对该公司处以罚款。同时，张某和其他十一名女性求职者联合向法院提起了民事诉讼，主张该公司违反了《民法典》第一千零一十条（性骚扰防治条款的扩张解释）和《妇女权益保障法》的相关规定，要求赔偿精神损害抚慰金和实际经济损失。

    公司法务部在内部答辩策略中主张，AI系统的偏差是"技术不可预见的结果"，公司没有主观歧视意图，因此不应承担法律责任。

    """
    
    # 初始化一本极其干净、带有最新字段的病历本
    initial_state = {
        "scenario_description": test_scenario,
        "current_phase": "start",
        "extracted_graph": None,
        "best_graph": None,
        "rust_interception_report": "",
        "d_separation_claims": [],
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
            if "best_graph" in state_update and state_update["best_graph"] is not None:
                final_extracted_graph = state_update["best_graph"]

    print("\n🎉 [推演结束] EdgeThemis 引擎最终提取的因果图谱：")

    if final_extracted_graph:
        pprint(final_extracted_graph.model_dump())
    else:
        print("🚨 提取失败：大模型未生成任何图谱。")