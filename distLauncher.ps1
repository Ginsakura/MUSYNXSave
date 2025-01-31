# 定义变量
$resourceDir = "musync_data/";                          # 资源目录
$resPath = "ico.res";                                   # C++图标res资源
$rcPath = "ico.rc";                                     # C++图标rc资源
$distDir = "MusyncSaveDecode/";                         # 生成目录
$resourceTargetDir = "MusyncSaveDecode/musync_data/";   # 资源文件目标目录
$resourcePath = @("Resources.bin", "songname.json", "songname.update", "Musync.ico"); # 资源文件

Clear-Host;
Write-Host "==== 任务开始 ====";

# Step 1: 编译图标资源
Set-Location -Path $resourceDir;
if (-not (Test-Path -Path $resPath)) {
    & windres $rcPath -O coff -o $resPath;
    Write-Host "图标资源 "."$path"."$resPath"." 创建成功！" -ForegroundColor Green;
} else {
    Write-Host "图标资源 "."$path"."$resPath"." 已存在。" -ForegroundColor Yellow;
}
Set-Location -Path ..;

# Step 2: 创建输出目录
if (-not (Test-Path -Path $distDir)) {
    New-Item -ItemType Directory -Path $distDir;
    Write-Host "目录 $distDir 创建成功！" -ForegroundColor Green;
} else {
    Write-Host "目录 $distDir 已存在。" -ForegroundColor Yellow;
}
# Step 2: 创建资源目录
if (-not (Test-Path -Path $resourceTargetDir)) {
    New-Item -ItemType Directory -Path $resourceTargetDir;
    Write-Host "目录 $resourceTargetDir 创建成功！" -ForegroundColor Green;
} else {
    Write-Host "目录 $resourceTargetDir 已存在。" -ForegroundColor Yellow;
}

# Step 3: 编译Cython模块
& pyinstaller build.spec --distpath ./MusyncSaveDecode --clean;
if ($?) {
    Write-Host "Pyinstaller编译成功！" -ForegroundColor Green;
} else {
    Write-Host "Pyinstaller编译失败！" -ForegroundColor Red;
    exit 1;
}
# Write-Host "正在编译Cython模块 ..."
# & python setup.py build_ext --inplace
# if ($?) {
#     Write-Host "Cython模块编译成功！" -ForegroundColor Green;
# } else {
#     Write-Host "Cython模块编译失败！" -ForegroundColor Red;
#     exit 1;
# }

# Step 4: 拷贝资源文件
foreach ($file in $resourcePath) {
    $sourceFile = Join-Path -Path $resourceDir -ChildPath $file;
    $destinationFile = Join-Path -Path $resourceTargetDir -ChildPath $file;

    if (Test-Path -Path $sourceFile) {
        Copy-Item -Path $sourceFile -Destination $destinationFile;
        Write-Host "文件 $file 已拷贝到 $resourceTargetDir"; -ForegroundColor Green;
    } else {
        Write-Host "文件 $file 不存在于 $resourceDir，跳过拷贝。" -ForegroundColor Orange;
    }
}

# Step 5: 编译启动器
# & g++ -o $path+"Launcher" .\Launcher.cpp $path+$resPath;

try {
    # 编译启动器
    & g++ -o ./MusyncSaveDecode/Launcher Launcher.cpp -I"D:\Program Files\Python3.11\include" -L"D:\Program Files\Python3.11\libs" -lpython311;
    # 检查编译是否成功
    if (-not $?) {
        throw "编译启动器失败！";
    }
    Write-Host "启动器编译成功！" -ForegroundColor Green;
}
catch {
    Write-Host "编译启动器时发生错误：$($_.Exception.Message)" -ForegroundColor Red;
    exit 1;
}

Write-Host "==== 所有任务完成 ====";
