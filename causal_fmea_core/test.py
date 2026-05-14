import causal_fmea_core

engine = causal_fmea_core.CausalParadigmEngine()

id1 = engine.register_node("冷却系统异常")
print(f"新节点 -> ID: {id1}")

id2 = engine.register_node("反应堆熔毁")
print(f"新节点 -> ID: {id2}")

id3 = engine.register_node("冷却系统异常")
print(f"重复节点拦截测试 -> ID: {id3}") 

exit()