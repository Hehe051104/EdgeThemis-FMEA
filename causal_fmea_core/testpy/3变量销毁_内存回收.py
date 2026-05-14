import causal_fmea_core

print("--- 1. 实例化引擎 ---")
engine = causal_fmea_core.CausalParadigmEngine()

print("--- 2. 引擎工作中 ---")
id1 = engine.register_node("测试节点")

print("--- 3. 准备拔掉引擎的呼吸机！ ---")
# 物理动作：强制命令 Python 的垃圾回收器立刻销毁 engine 对象
del engine 

print("--- 4. 引擎已被彻底摧毁 ---")