# .devcontainer/Dockerfile
FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# 1. 基础系统弹药库 (🌟 新增 python3-venv)
RUN apt-get update && apt-get install -y \
    build-essential cmake git curl wget sudo \
    python3 python3-pip python3-dev python3-venv \
    && rm -rf /var/lib/apt/lists/*

# 2. 权限隔离：创建非 root 专属账户
ARG USERNAME=hehe
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash $USERNAME \
    && echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME

# 3. 挂载 Rust 底座
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/home/${USERNAME}/.cargo/bin:${PATH}"

# ==========================================
# 🛡️ 战术升级：在镜像层直接焊死 Python 隔离沙盒
# 必须放在 /home 下，绝不能放在工作区，防止被挂载动作物理抹除！
# ==========================================
ENV VIRTUAL_ENV=/home/$USERNAME/.venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYO3_PYTHON="$VIRTUAL_ENV/bin/python3"

# ==========================================
# ⚙️ 编译期防爆衣：双重变量齐下，彻底镇压链接器
# ==========================================
ARG CUDA_ARCH=89
ENV LIBRARY_PATH=/usr/local/cuda/lib64/stubs:$LIBRARY_PATH
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64/stubs:$LD_LIBRARY_PATH
RUN sudo ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1 || true

# 4. 编译原生的 llama.cpp 玩具 (保留底层 C++ 测试能力)
RUN sudo mkdir -p /opt/llama.cpp \
    && sudo chown -R $USERNAME:$USERNAME /opt \
    && export http_proxy="" && export https_proxy="" && export HTTP_PROXY="" && export HTTPS_PROXY="" \
    && git clone https://github.com/ggml-org/llama.cpp.git /opt/llama.cpp \
    && cd /opt/llama.cpp \
    && cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=${CUDA_ARCH} \
    && cmake --build build --config Release -j $(nproc)

# 5. 注入高层推演组件 (自动装入刚刚建好的 .venv 中)
RUN pip install --upgrade pip --no-cache-dir \
    && pip install --no-cache-dir maturin pytest pydantic langgraph

# 6. 🌟 全场核心：在构建期硬刚编译带 CUDA 加速的 llama-cpp-python
# 让 Docker 引擎替你承担长达几分钟的 C++ 编译痛苦！
RUN CMAKE_ARGS="-DGGML_CUDA=on" pip install llama-cpp-python --upgrade --force-reinstall --no-cache-dir

# 7. [终极清洗] 卸磨杀驴，抹除骗编译器的假驱动
RUN sudo rm -rf /usr/local/cuda/lib64/stubs