# -*- coding: utf-8 -*-
"""
资产打包工具脚本 (Resource Packer)
目标: 将离散资产高压缩并封装为带有索引头的单一二进制包。
"""

import gzip
import json
import os
import struct
from hashlib import sha256
from io import BytesIO
from typing import Optional, Any

# ==================== 常量定义 (Constants) ====================
FILL_SIZE: int = 512
FIX_DLL: str = "E93D03FC58F6E70BBFAD2B2F89326FC9C4697D4C8C83F9182EDCA7F43EF3F282"
SOURCE_DLL: str = 'E6ED56C611F475CC895B469F65856F5E8F2C199693C3AD86A87D19CA4986C9D9'

# ==================== 核心逻辑 (Core Logic) ====================
def get_hash(file_path: Optional[str] = None) -> str:
    """分块读取并获取文件 SHA256 哈希值 (大写)"""
    if not file_path or not os.path.isfile(file_path):
        return ""
    sha256_hash = sha256()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    hash_result: str = sha256_hash.hexdigest().upper()
    return hash_result

def clean_previous_build() -> bool:
    """
    清理上次打包遗留的二进制缓存文件与最终包。
    Returns:
        bool: 如果所有文件都成功清理（或本就不存在），返回 True；
              如果遇到文件被占用等致命错误，返回 False。
    """
    print("正在清理上次构建的残留文件...")

    # 定义所有可能生成的构建产物路径
    target_files: list[str] = [
        "./musync_data/Icon.bin",
        "./musync_data/Font.bin",
        "./musync_data/SongName.bin",
        "./musync_data/Assembly-CSharp.bin",
        "./musync_data/mscorlib.bin",
        "./musync_data/LICENSE.bin",
        "./musync_data/Resources.bin"
    ]

    has_error: bool = False
    for relative_path in target_files:
        abs_path: str = os.path.abspath(relative_path)
        if os.path.exists(abs_path):
            try:
                os.remove(abs_path)
                print(f"已删除缓存文件: {abs_path}")
            except PermissionError:
                print(f"❌ 权限被拒绝 (文件可能被占用): {abs_path}")
                has_error = True
            except OSError as e:
                print(f"❌ 删除文件时发生未知系统错误 {abs_path}: {e}")
                has_error = True
    if has_error:
        print("清理过程中遇到错误，请关闭占用文件的软件后重试。")
        return False
    print("清理完成，环境已就绪。")
    return True


def compress_file(file_path: str) -> bytes:
    """
    读取并压缩文件，全程在内存中进行二进制流转。
    """
    with open(file_path, 'rb') as file:
        file_data: bytes = file.read()

    # 使用 BytesIO 避免落盘，提升 IO 效率
    buffer = BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode='wb') as gzip_file:
        gzip_file.write(file_data)

    return buffer.getvalue()


def compress_and_save(read_path: str, write_path: str) -> Optional[bytes]:
    """
    读取、压缩并保存单个文件的压缩缓存副本。
    """
    if not os.path.isfile(read_path):
        print(f"File not found, skipped: {read_path}")
        return None

    compressed_data: bytes = compress_file(read_path)

    with open(write_path, 'wb') as out_file:
        out_file.write(compressed_data)

    return compressed_data


def get_song_version() -> int:
    """安全读取版本号，避免顶层 IO 异常"""
    try:
        with open("./musync_data/songname.ver", 'r', encoding="ascii") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        print("Failed to read songname.ver, defaulting to 0")
        return 0


def build_resource_pack() -> None:
    """构建打包主控流程"""
    # 打包前进行清理环境校验
    if not clean_previous_build():
        print("环境清理失败，打包流程已终止。")
        return  # 直接退出，避免后续步骤产生脏数据

    json_path: str = "./musync_data/songname.json"
    ver_path: str = "./musync_data/songname.ver"
    # 读取和写入songname版本 (如果文件不在或格式错，直接抛出原生异常停止打包)
    with open(json_path, 'r', encoding='utf-8') as fi:
        ver_str: str = str(json.load(fi)["version"])
    with open(ver_path, 'w', encoding='ascii') as fo:
        fo.write(ver_str)

    file_list: list[dict[str, str]] = [
        {"source": "./musync_data/MUSYNC.ico",
         "target": "./musync_data/Icon.bin",
         "tag": "icon"},
        {"source": "./musync_data/LXGW.ttf",
         "target": "./musync_data/Font.bin",
         "tag": "font"},
        {"source": "./musync_data/songname.json",
         "target": "./musync_data/SongName.bin",
         "tag": "song_name"},
        {"source": "./musync_data/Assembly-CSharp.dll",
         "target": "./musync_data/Assembly-CSharp.bin",
         "tag": "game_lib"},
        {"source": "./mscorlib.dll",
         "target":"./musync_data/mscorlib.bin",
         "tag": "core_lib"},
        {"source": "./LICENSE",
         "target": "./musync_data/LICENSE.bin",
         "tag": "license"},
    ]

    binary_info: dict[str, dict[str, Any]] = {}
    current_offset: int = FILL_SIZE
    payload_buffer = BytesIO()

    # 1. 遍历并压缩每个资产
    for file_node in file_list:
        source_path = file_node['source']
        target_path = file_node['target']
        tag = file_node['tag']

        print(f"Encoding: {source_path} -> {target_path}")
        compressed_bytes = compress_and_save(source_path, target_path)

        if compressed_bytes is None:
            continue

        byte_length = len(compressed_bytes)

        # 记录元数据映射
        binary_info[tag] = {
            "offset": current_offset,
            "length": byte_length,
            "hash": get_hash(source_path)
        }

        current_offset += byte_length
        payload_buffer.write(compressed_bytes)

    # 2. 安全地补充特异性结构数据
    if "game_lib" in binary_info:
        binary_info["game_lib"]["source_hash"] = SOURCE_DLL
    if "song_name" in binary_info:
        binary_info["song_name"]["version"] = get_song_version()

    print(json.dumps(binary_info, ensure_ascii=False, indent=4))

    # 3. 序列化并压缩头文件信息
    header_json: bytes = json.dumps(binary_info).encode("utf-8")  # 强制使用 utf-8 更安全
    header_buffer = BytesIO()
    with gzip.GzipFile(fileobj=header_buffer, mode='wb') as gz_file:
        gz_file.write(header_json)

    compressed_header: bytes = header_buffer.getvalue()
    header_size: int = len(compressed_header)

    # [致命漏洞修复] 检查压缩后的头部是否超出了预留的 508 字节！
    if header_size > (FILL_SIZE - 4):
        raise OverflowError(
            f"Header compression overflow! Size {header_size} bytes exceeds max allowed {FILL_SIZE - 4} bytes. "
            f"Please increase FILL_SIZE."
        )

    # 4. 封装并生成最终二进制包
    # 包结构: [4字节头部大小] + [动态填充头部] + [负载数据]
    with open("./musync_data/Resources.bin", 'wb') as binary_file:
        # 写入 uint32 的头部大小描述符
        binary_file.write(struct.pack('I', header_size))
        # 写入头部，剩余空间用 0x00 补齐
        binary_file.write(compressed_header.ljust(FILL_SIZE - 4, b'\x00'))
        # 写入所有被打包文件的二进制流
        binary_file.write(payload_buffer.getvalue())

    print("Success: Resources encoded and packed perfectly.")


if __name__ == '__main__':
    build_resource_pack()
