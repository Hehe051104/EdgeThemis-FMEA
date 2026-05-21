#!/bin/bash
MODEL_PATH="../../qwen2.5-3b-q4.gguf"

echo " [核心引擎] 正在启动纯 C++ 底层推理服务..."
echo " [物理护甲] 开启 Q8_0 KV 缓存量化，保护 8GB VRAM..."

# 换上了最新版引擎的缓存压缩指令：-ctk 和 -ctv
llama-server \
  -m $MODEL_PATH \
  -c 4096 \
  --ctx-size 4096 \
  --override-kv tokenizer.ggml.context_length=int:4096 \
  -ngl 99 \
  -ctk q8_0 \
  -ctv q8_0 \
  --host 127.0.0.1 \
  --port 8080