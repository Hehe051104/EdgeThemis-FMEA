import causal_fmea_core

# 案例 1：传统的高频小毛病 (比如：每天漏水，但毫无影响，极易发现)
# S=2 (不严重), O=9 (天天发生), D=1 (一眼看到)
minor_issue = causal_fmea_core.FmeaScore(2, 9, 1)
print(f"小毛病 EdgeThemis 风险值: {minor_issue.calculate_rpn()}") 
# 预期：(100*2) + (10*9) + 1 = 291分 (安全通过)

# 案例 2：致命的黑天鹅事件 (比如：反应堆熔毁，百年一次，极难探测)
# S=10 (死局), O=1 (罕见), D=9 (神不知鬼不觉)
lethal_issue = causal_fmea_core.FmeaScore(10, 1, 9)
print(f"致命黑天鹅 EdgeThemis 风险值: {lethal_issue.calculate_rpn()}") 
# 预期：(100*10) + (10*1) + 9 = 1019分 (直接触发 600 分以上的死神拦截线！)

exit()