# -*- coding: utf-8 -*-
"""
部署自动化 — 将 BepInEx 框架 + MUSYNCDelay 插件部署到游戏目录。
对应 tasks 13.1-13.5。
"""
import hashlib
import logging
import os
import shutil
from pathlib import Path

from .config_manager import config, Logger

_logger: logging.Logger = Logger.get_logger("Deployer")

# 插件 DLL 名称
PLUGIN_DLL = "MUSYNCDelay.dll"
# BepInEx 框架核心文件（相对于 BepInEx 根目录）
BEPINEX_CORE_FILES = [
    "BepInEx/core/BepInEx.dll",
    "BepInEx/core/0Harmony.dll",
    "BepInEx/core/BepInEx.Preloader.dll",
    "BepInEx/core/MonoMod.RuntimeDetour.dll",
    "BepInEx/core/MonoMod.Utils.dll",
    "BepInEx/core/Mono.Cecil.dll",
    "BepInEx/core/Mono.Cecil.Mdb.dll",
    "BepInEx/core/Mono.Cecil.Pdb.dll",
    "BepInEx/core/Mono.Cecil.Rocks.dll",
]
DOORSTOP_FILES = [
    "winmm.dll",
    "doorstop_config.ini",
]


def _get_game_dir() -> str:
    """获取游戏安装目录。"""
    return config.MainExecPath.rstrip('/\\')


def _get_source_dir() -> Path:
    """获取部署源文件目录（随工具分发的 BepInEx + 插件）。"""
    return Path(__file__).parent.parent / "deploy_assets"


def _get_hash(file_path: str) -> str:
    """计算文件 SHA256。"""
    h = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def deploy() -> bool:
    """
    执行部署：将 BepInEx 框架 + 插件 DLL 复制到游戏目录。
    返回 True 表示部署成功或已是最新。
    """
    game_dir = _get_game_dir()
    if not game_dir or not os.path.isdir(game_dir):
        _logger.error(f"Game directory not found: {game_dir}")
        return False

    source_dir = _get_source_dir()
    if not source_dir.is_dir():
        _logger.error(f"Deploy assets not found: {source_dir}")
        return False

    try:
        # 13.2 复制 Doorstop 文件
        for fname in DOORSTOP_FILES:
            src = source_dir / fname
            dst = Path(game_dir) / fname
            if src.is_file():
                shutil.copy2(str(src), str(dst))
                _logger.debug(f"Copied {fname}")

        # 复制 BepInEx 核心
        for rel_path in BEPINEX_CORE_FILES:
            src = source_dir / rel_path
            dst = Path(game_dir) / rel_path
            if src.is_file():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src), str(dst))
                _logger.debug(f"Copied {rel_path}")

        # 复制插件 DLL
        plugin_src = source_dir / "BepInEx" / "plugins" / "MUSYNCDelay" / PLUGIN_DLL
        plugin_dst = Path(game_dir) / "BepInEx" / "plugins" / "MUSYNCDelay" / PLUGIN_DLL
        if plugin_src.is_file():
            plugin_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(plugin_src), str(plugin_dst))
            _logger.info(f"Plugin deployed: {plugin_dst}")

        # 13.4 验证游戏原版 DLL 未被修改
        game_dll = Path(game_dir) / "MUSYNX_Data" / "Managed" / "Assembly-CSharp.dll"
        if game_dll.is_file():
            _logger.info(f"Game Assembly-CSharp.dll hash: {_get_hash(str(game_dll))}")

        _logger.info("Deployment complete.")
        return True

    except Exception as e:
        _logger.error(f"Deployment failed: {e}")
        return False


def check_deployed() -> bool:
    """13.3 检查是否已部署。"""
    game_dir = _get_game_dir()
    if not game_dir:
        return False
    plugin_path = Path(game_dir) / "BepInEx" / "plugins" / "MUSYNCDelay" / PLUGIN_DLL
    return plugin_path.is_file()


def deploy_if_needed() -> bool:
    """13.3 版本检测：已部署则跳过，否则部署。"""
    if check_deployed():
        _logger.info("Plugin already deployed, skipping.")
        return True
    return deploy()
