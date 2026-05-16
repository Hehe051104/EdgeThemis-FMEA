# 文件：python/causal_fmea/context_guard.py
import gc
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
        print("💥 [物理沙盒崩塌] 推演结束，强制执行 VRAM 与内存湮灭...")
        
        # 物理动作 1：斩断 Rust 指针，唤醒底层的 Drop 死神
        del self.rust_engine
        
        # 物理动作 2：极其暴力的 Python 垃圾回收
        # 只要这里的临时变量被清理，底层的 llama_free 就会自动释放显存，根本不需要 Torch！
        gc.collect()
            
        if exc_type:
            print(f"🚨 侦测到内部异常: {exc_val}，但底层引擎已安全卸载！")
        return False