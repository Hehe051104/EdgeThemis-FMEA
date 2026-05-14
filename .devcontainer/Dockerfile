FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential cmake git curl wget sudo \
    python3 python3-pip python3-dev \
    && rm -rf /var/lib/apt/lists/*

ARG USERNAME=hehe
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash $USERNAME \
    && echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/home/${USERNAME}/.cargo/bin:${PATH}"
ENV PYO3_PYTHON=/usr/bin/python3

ARG CUDA_ARCH=89

# --- 终极物理防弹衣：双重变量齐下，彻底镇压链接器 ---
# 1. 编译期直接依赖寻址
ENV LIBRARY_PATH=/usr/local/cuda/lib64/stubs:$LIBRARY_PATH
# 2. 编译期传递依赖验证 & 运行期寻址
ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64/stubs:$LD_LIBRARY_PATH
# 3. 欺骗系统，伪造驱动
RUN sudo ln -s /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/stubs/libcuda.so.1 || true

# 执行编译（斩断网络代理，多核全开，保留全部官方测试玩具！）
RUN sudo mkdir -p /opt/llama.cpp \
    && sudo chown -R $USERNAME:$USERNAME /opt \
    && export http_proxy="" && export https_proxy="" && export HTTP_PROXY="" && export HTTPS_PROXY="" \
    && git clone https://github.com/ggml-org/llama.cpp.git /opt/llama.cpp \
    && cd /opt/llama.cpp \
    && cmake -B build -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=${CUDA_ARCH} \
    && cmake --build build --config Release -j $(nproc)

# [终极清洗] 编译全部结束后，卸磨杀驴，抹除骗编译器的假驱动，把运行期的路让给宿主机的真实 4060 驱动
RUN rm -rf /usr/local/cuda/lib64/stubs