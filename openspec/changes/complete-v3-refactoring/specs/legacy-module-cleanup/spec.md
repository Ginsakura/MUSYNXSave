## ADDED Requirements

### Requirement: all_hit_analyze 外壳翻新
`all_hit_analyze.py` SHALL 移除 `(object)` 显式继承、修正 docstring 中的旧类名 `HitAnalyze` 为当前类名 `AllHitAnalyze`、移除被注释的 `super()` 调用。

#### Scenario: 旧风格被清除
- **WHEN** 检查 `all_hit_analyze.py` 的类定义和 docstring
- **THEN** 类定义为 `class AllHitAnalyze:`，docstring 使用 `AllHitAnalyze`，不存在被注释的 `super()` 调用

### Requirement: musync_save_decode 外壳翻新
`musync_save_decode.py` SHALL 移除 `(object)` 显式继承、修正 docstring 中的旧类名 `MUSYNCSavProcess` 为当前类名 `MusyncSaveDecoder`、移除被注释的反射修改字段代码。

#### Scenario: 旧风格被清除
- **WHEN** 检查 `musync_save_decode.py` 的类定义和 docstring
- **THEN** 类定义为 `class MusyncSaveDecoder:`，docstring 使用 `MusyncSaveDecoder`，不存在被注释的反射代码

### Requirement: hit_delay 死代码移除
`hit_delay.py` 中的 `_on_closing_bak` 备用方法 SHALL 被移除。被注释的 resize 逻辑 SHALL 被移除。

#### Scenario: 备用方法被清除
- **WHEN** 检查 `hit_delay.py` 中的方法定义
- **THEN** 不存在 `_on_closing_bak` 方法

#### Scenario: 注释代码被清除
- **WHEN** 检查 `hit_delay.py` 中的注释行
- **THEN** 不存在被注释的 resize 逻辑代码块

### Requirement: 未使用导入清理
`save_data_manager.py` 中未使用的 `List` 导入 SHALL 被移除。`main_window.py` 中未使用的 `Toplevel` 导入 SHALL 被移除（若 `SubWindow` 已被移除）。

#### Scenario: typing 导入清理
- **WHEN** 检查 `save_data_manager.py` 的导入语句
- **THEN** 不存在 `from typing import ... List` 导入（`Any` 保留，若仍在使用）

### Requirement: 根目录临时文件清理
项目根目录下的空文件 `tmp.py` SHALL 被删除。

#### Scenario: 临时文件被移除
- **WHEN** 检查项目根目录
- **THEN** 不存在 `tmp.py` 文件
