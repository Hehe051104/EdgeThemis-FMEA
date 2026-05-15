# 文件：python/causal_fmea/agent_state_machine.py
from typing import TypedDict, List, Optional
from pydantic import BaseModel, Field

# ==========================================
# 枷锁 1：强类型 JSON 输出约束 (管住大模型的嘴)
# 绝对通用：没有任何法条字眼，只有纯粹的因果拓扑
# ==========================================
class CausalEdge(BaseModel):  # 代表一条因果关系的边
    source: str = Field(description="原因节点")
    target: str = Field(description="结果节点")
    S: int = Field(ge=1, le=10, description="严重度 (1-10)")
    O: int = Field(ge=1, le=10, description="频度 (1-10)")
    D: int = Field(ge=1, le=10, description="探测度 (1-10)")

class ExtractedGraph(BaseModel):  # 代表大模型输出的整个因果图
    edges: List[CausalEdge] = Field(description="提取出的所有因果边集合")

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