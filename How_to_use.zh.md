# How to use (v1.2.6 rc2)

## 菜单
[steamlink]: https://store.steampowered.com/app/952040/_/
本程序为Steam游戏[`同步音律喵赛克`][steamlink]的非官方插件，用于对游戏本体进行功能扩展。
1. [存档解析](#启动页)
2. [谱面筛选](#)
3. [谱面成绩筛选](#)
4. [一键启动游戏(Steam接口)](#)
5. [成绩-难度分布图](#)
6. [谱面游玩详情](#)
	- 所有点击在-150~+250ms中的`分布柱状图`
	- 对`分布柱状图`的正态曲线拟合
	- 所有点击在-150~+250ms中的`饼状图`
	- 一键获取控制台中的点击记录
	- 历史记录展示
	- 修改历史记录名称
7. 更多...

## 要求
1. 系统：仅限于Windows端使用
2. 客户端：针对Steam平台开发，Epic平台未测试

## 获取本程序
[release]: https://github.com/Ginsakura/MUSYNCSave/releases
[requirements]: https://github.com/Ginsakura/MUSYNCSave/blob/main/requirements.txt
1. 从[release页面][release]下载

    [latest_prerelease_svg]: https://img.shields.io/github/v/release/ginsakura/MUSYNCSave?display_name=release&label=Latest%20PreRelease&include_prereleases
    [all_tags]: https://github.com/Ginsakura/MUSYNCSave/tags
    [![Latest tag][latest_prerelease_svg]][all_tags]

    [latest_release_svg]: https://img.shields.io/github/v/release/ginsakura/MUSYNCSave?display_name=release&label=Latest%20Release
    [release]: https://github.com/Ginsakura/MUSYNCSave/releases
    [![latest release][latest_release_svg]][release]

2. 从源码编译：

	编译环境：Python 3.11.5, [requirements.txt][requirements]

	- 无命令行的散包：
	```cmd
	pyinstaller --distpath ./NoCLI/ -D -i ./musync_data/Musync.ico ./Launcher.py -w
	```
	- 无命令行的单exe文件：
	```cmd
	pyinstaller --distpath ./ -F -i ./musync_data/Musync.ico ./Launcher.py -w
	```
	- 带命令行的散包：
	```cmd
	pyinstaller --distpath ./WithCLI/ -D -i ./musync_data/Musync.ico ./Launcher.py
	```
	- 带命令行的单exe文件：
	```cmd
	pyinstaller --distpath ./ -F -i ./musync_data/Musync.ico ./Launcher.py
	```

## 功能介绍
### 启动页
#### 头部

![maintitle](./ReadmeResources/how_to_use_maintitle.png "maintitle")

① 本程序标题

② 存档中解析出的上次游玩

③ 刷新与解码存档文件，绑定`F5`按键 ($\color{Red}{实际上两个按钮功能相似}$)

④ 存档地址文本与从文件管理器中选取按钮

⑤ 对下方筛选出的谱面进行计数，无筛选时即为所有谱面

⑥ 对谱面进行筛选，`筛选控件`为激活按钮，只有`激活`与`不激活`两种状态，

`额外筛选`为切换按钮，从↖到↘分别有三种、三种、四种状态进行`循环切换`

⑦ 通过下方筛选过的谱面计算综合同步率

⑧ 游戏启动监测，游戏启动时会自动变成绿色，红色时点击可通过steam接口(`steam://rungameid/952040`)启动游戏

⑨ 成绩分布窗口，使用matlablib绘制，通过读取存档内所有谱面的成绩生成散点图，通过散点计算平均值折线图

⑩ 通过修改客户端DLL文件实现更高级、更深层次的功能添加，修改的代码放置于`CSharp Code`文件夹

#### 窗体

①②③④⑤⑥⑦⑧⑨⑩

## 