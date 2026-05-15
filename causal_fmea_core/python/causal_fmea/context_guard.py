# 文件：python/causal_fmea/context_guard.py
import gc
import torch
from contextlib import ContextDecorator  # 同时用作上下文管理器和装饰器。你只需要实现 __enter__ 和 __exit__ 即可
#  这里导入我们亲手在 Rust 里焊死的底层引擎！
from causal_fmea_core import CausalParadigmEngine

class AgentContext(ContextDecorator):
    """
    4060 显存绝对防爆门与底层图引擎挂载舱
    """
    def __init__(self):
        self.rust_engine = None

    def __enter__(self):
        print("🛡️ [物理沙盒开启] 正在分配 VRAM，挂载 Rust 测谎仪...")
        # 物理动作 1：实例化底层的 Rust 引擎 (此时 Rust 的 Drop 死神进入待命状态)
        self.rust_engine = CausalParadigmEngine()
        return self.rust_engine

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("💥 [物理沙盒崩塌] 推演结束，强制执行 VRAM 湮灭...")
        
        # 物理动作 2：手动销毁 Rust 引擎引用，瞬间触发底层的 Drop 特征！
        del self.rust_engine
        
        # 物理动作 3：用 Python 最暴力的垃圾回收和 CUDA 清理来扫尾
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            
        if exc_type:
            print(f"🚨 侦测到内部异常: {exc_val}，但显存已被成功锁死保护！")
        return False # 不吞咽异常，让上层知道发生了什么