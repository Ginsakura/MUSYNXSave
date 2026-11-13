## 1. L0 模块风格统一

- [x] 1.1 `save_data_manager.py`：移除 `(object)` 继承、`self.logger` → `self._logger`、移除未使用的 `List` 导入、类型注解改为内置泛型
- [x] 1.2 `songname_manager.py`：`self.logger` → `self._logger`、检查并统一类型注解

## 2. 中间模块外壳翻新

- [x] 2.1 `all_hit_analyze.py`：移除 `(object)` 继承、docstring 旧类名 `HitAnalyze` → `AllHitAnalyze`、移除被注释的 `super()` 调用
- [x] 2.2 `musync_save_decode.py`：移除 `(object)` 继承、docstring 旧类名 `MUSYNCSavProcess` → `MusyncSaveDecoder`、移除被注释的反射代码、PascalCase 方法重命名为 snake_case

## 3. hit_delay 死代码清理

- [x] 3.1 移除 `_on_closing_bak` 备用方法
- [x] 3.2 移除被注释的 resize 逻辑代码块

## 4. main_window 全面重构

- [x] 4.1 移除 `(object)` 继承、修正 docstring 旧类名 `MusyncSavDecodeGUI` → `MusyncMainWindow`
- [x] 4.2 所有 PascalCase 方法重命名为 snake_case（`RefreshSave`、`DataLoad`、`SelectPath`、`DoubleClick`、`SortClick`、`StartGame`、`UpdateWindowInfo`、`UpdateEnum`、`CheckGameRunning` 等）
- [x] 4.3 同步更新所有 Tkinter 回调绑定（`command=`、`bind()`、`after()`）中的方法引用
- [x] 4.4 同步更新 `debug_launcher.py` 和 `launcher.py` 中对 main_window 方法的引用
- [x] 4.5 移除被注释的旧代码：`win32api`/`PIL` 导入、`NewStyle`/`OldStyle` 分支、`SubWindow` 调用
- [x] 4.6 移除 `if 1 :` 永真条件，内部代码块减少一级缩进
- [x] 4.7 补全 `MessageBoxEnum` 枚举，移除 TODO 注释
- [x] 4.8 清理未使用的 `Toplevel` 导入；若 `SubWindow` 类无活跃引用则一并移除

## 5. 全局验证与清理

- [x] 5.1 全文搜索确认无残留：旧类名（`MusyncSavDecodeGUI`、`MUSYNCSavProcess`、`HitAnalyze`）、PascalCase 方法定义、`(object)` 继承、`self.logger`（公有）
- [x] 5.2 删除根目录空文件 `tmp.py`
- [ ] 5.3 手动运行程序，验证主窗口、存档解码、同步率统计、击打延迟、各分析图表功能正常
