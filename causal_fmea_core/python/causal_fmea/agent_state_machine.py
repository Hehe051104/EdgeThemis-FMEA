# 文件：python/causal_fmea/agent_state_machine.py
from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field

# ==========================================
# 枷锁 1：强类型 JSON 输出约束 (管住大模型的嘴)
# 绝对通用：没有任何法条字眼，只有纯粹的因果拓扑
# ==========================================
class CausalEdge(BaseModel):  # 代表一条因果关系的边
    source: str = Field(description="因果边的起点名词")
    target: str = Field(description="因果边的终点名词")
    S: int = Field(ge=1, le=10, description="严重度 (1-10)")
    O: int = Field(ge=1, le=10, description="频度 (1-10)")
    D: int = Field(ge=1, le=10, description="探测度 (1-10)")

class ExtractedGraph(BaseModel):  # 代表大模型输出的整个因果图
    # ══════ 假设-验证范式：先下判断，再画图 ══════
    causal_verdict: str = Field(
        description="对用户因果疑问的最终判决：Yes 或 No。必须最先给出！"
    )
    hypothesized_cause: str = Field(
        description="用户问题中询问的起因实体（Cause）。"
    )
    hypothesized_effect: str = Field(
        description="用户问题中询问的结果实体（Effect）。"
    )
    reasoning_process: str = Field(
        description="详细的案情推理过程。必须拆解出幕后黑手(C)以及中间物理传导过程(Z)。"
    )
    edges: List[CausalEdge] = Field(description="基于上一步的推理，严格提取出的因果拓扑边。")

# -----------------------------------------------------------------------------------------------------------------
# 限制reflector的输出格式
class ReflectorVerdict(BaseModel):
    verdict: str = Field(description="必须严格输出 PASS 或 REJECT")
    reason: str = Field(description="言简意赅的反驳或赞同理由")


# ==========================================
# 枷锁 2：LangGraph 的纯因果状态栈 (State)
# 剥离一切业务逻辑，只保留推演和物理拦截状态
# ==========================================
class CausalAgentState(TypedDict):
    """
    通用因果推演流水线的全局数据包
    """
    scenario_description: str                    # 原始场景文本 (不论是车祸、断电还是案件)
    current_phase: str                           # 当前阶段 (generate_graph, validate_graph, refine_graph)
    extracted_graph: Optional[ExtractedGraph]    # 大模型吐出的拓扑图
    rust_interception_report: str                # Rust 测谎仪返回的物理诊断书
    interception_count: int                      # 物理拦截计数器 (防止大模型无限卡死)
    is_safe: bool                                # 最终是否通过了 Rust 的 d-分离和环路测谎
    d_separation_claims: list[str]               # 新增：存放 Rust 从当前图中榨取出的 d-分离物理断言