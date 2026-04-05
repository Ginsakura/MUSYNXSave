# Step 0: 检查参数列表
[CmdletBinding()]
param (
    [switch]$noarchive
)

# ==========================================
# 函数定义区
# ==========================================

# ------------------------------------------
# 功能: 构建C/C++图标资源
# ------------------------------------------
function BuildIcon{
    $resPath = "ico.res";   # C++图标res资源
    $rcPath = "ico.rc";     # C++图标rc资源
    Set-Location -Path "musync_data/";
    if (-not (Test-Path -Path $resPath)) {
        & windres $rcPath -O coff -o $resPath;
        Write-Host ("图标资源 {0}{1} 创建成功！ " -f $path, $resPath) -ForegroundColor Green;
    } else {
        Write-Host ("图标资源 {0}{1} 已存在。 " -f $path, $resPath) -ForegroundColor Yellow;
    }
    Set-Location -Path ..;
}

# ------------------------------------------
# 功能: 检查目录是否存在，如果不存在则创建该目录。
# ------------------------------------------
function CheckDir {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [string]$Dir
    )


    process {
        if (-not (Test-Path -Path $Dir)) {
            New-Item -ItemType Directory -Path $Dir -ErrorAction Stop | Out-Null
            Write-Host ("目录 {0} 创建成功！ " -f $Dir) -ForegroundColor Green
        } else {
            Write-Host ("目录 {0} 已存在。 " -f $Dir) -ForegroundColor Yellow
        }
    }
}

# ------------------------------------------
# 功能: 复制资源文件
# ------------------------------------------
function Copy-Resources {
    param (
        [string]$SourceDirectory,
        [string]$TargetDirectory,
        [string[]]$ResourceFiles
    )

    # Copy each resource file
    foreach ($file in $ResourceFiles) {
        $sourceFile = Join-Path -Path $SourceDirectory -ChildPath $file
        $destinationFile = Join-Path -Path $TargetDirectory -ChildPath $file

        if (Test-Path -Path $sourceFile) {
            Copy-Item -Path $sourceFile -Destination $destinationFile
            Write-Host ("文件 {0} 已拷贝到 {1}。 " -f $file, $TargetDirectory) -ForegroundColor Green
        } else {
            Write-Host ("文件 {0} 不存在于 {1}，跳过拷贝。 " -f $file, $SourceDirectory) -ForegroundColor Yellow
        }
    }
}

# ------------------------------------------
# 功能: 创建ZIP文件 (已重命名以避免与系统内置压缩命令冲突导致卡死)
# ------------------------------------------
function Create-Compress-Archive {
    param (
        [Parameter(Mandatory = $true)]
        [string[]]$SourceItems,

        [Parameter(Mandatory = $true)]
        [string]$DestinationZip
    )

    # 确保目标ZIP文件的目录存在
    # $destinationDir = [System.IO.Path]::GetDirectoryName($DestinationZip)
    # CheckDir -Dir $DestinationZip;

    # 打包文件和文件夹
    try {
        Compress-Archive -Path $SourceItems -DestinationPath $DestinationZip -Force
        Write-Host ("打包成功！输出文件：{0} " -f $DestinationZip) -ForegroundColor Green
    }
    catch {
        Write-Host ("打包失败：{0} " -f $_.Exception.Message) -ForegroundColor Red
    }
}

# ==========================================
# 变量声明与业务逻辑区
# ==========================================

cd ./musync_save/;
$isPreRelease = python -c "import version;print(version.is_is_pre_release)";
$isPreReleaseBool = [bool]::Parse($isPreRelease);
# 根据布尔值调用不同的属性并赋值给 $version
if ($isPreReleaseBool) {
    $version = py -c "import version; print(version.pre_version)";
} else {
    $version = py -c "import version; print(version.version)";
}
$resourceFiles = @("Resources.bin", "songname.json", "songname.ver", "Musync.ico");  # 资源文件
$archive_AC = @("logs", "musync_data", "MusyncSaveDecodeCLI.exe");                     # CLI all in one archive files
$archive_ANC = @("logs", "musync_data", "MusyncSaveDecodeNoCLI.exe");                  # NoCLI all in one archive files
$archive_C = @("logs", "musync_data", "_internal", "MusyncSaveDecodeCLI.exe");
$archive_NC = @("logs", "musync_data", "_internal", "MusyncSaveDecodeNoCLI.exe");
$destinationZip_AC = "Archive/MusyncSaveDecode_WithConsole_${version}_AllInOne.zip"
$destinationZip_ANC = "Archive/MusyncSaveDecode_NoConsole_${version}_AllInOne.zip"
$destinationZip_C = "../Archive/MusyncSaveDecode_WithConsole_${version}.zip";
$destinationZip_NC = "../Archive/MusyncSaveDecode_NoConsole_${version}.zip";
cd ../;

Clear-Host;
Write-Host "==== 任务开始 ====";
# Step 1: 清理生成目录
Remove-Item -Path "./MusyncSaveDecode" -Force -Recurse -ErrorAction SilentlyContinue;
Write-Host "已删除目录：./MusyncSaveDecode" -ForegroundColor Yellow;

# Step 2: 检查构建目录
CheckDir -Dir "MusyncSaveDecode/";
CheckDir -Dir "MusyncSaveDecode/Archive/";
# CheckDir -Dir "MusyncSaveDecode/MusyncSaveDecodeCLI/";
# CheckDir -Dir "MusyncSaveDecode/MusyncSaveDecodeNoCLI/";

# Step 3: Pyinstaller构建
Write-Host "Pyinstaller构建开始..." -ForegroundColor Green;
& pyinstaller "buildLauncher.spec" --distpath "./MusyncSaveDecode" --clean;
if ($?) {
    Write-Host "Pyinstaller构建成功! " -ForegroundColor Green;
} else {
    Write-Host "Pyinstaller构建失败! " -ForegroundColor Red;
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

# Step 4: 检查资源目录
Set-Location -Path "MusyncSaveDecode";
CheckDir -Dir "logs/";
CheckDir -Dir "musync_data/";
CheckDir -Dir "MusyncSaveDecodeCLI/musync_data/";
CheckDir -Dir "MusyncSaveDecodeCLI/logs/";
CheckDir -Dir "MusyncSaveDecodeNoCLI/musync_data/";
CheckDir -Dir "MusyncSaveDecodeNoCLI/logs/";

# Step 5: 拷贝资源文件
Copy-Resources -SourceDirectory "../musync_data" -TargetDirectory "musync_data" -ResourceFiles $resourceFiles;
Copy-Resources -SourceDirectory "../musync_data" -TargetDirectory "MusyncSaveDecodeCLI/musync_data/" -ResourceFiles $resourceFiles;
Copy-Resources -SourceDirectory "../musync_data" -TargetDirectory "MusyncSaveDecodeNoCLI/musync_data/" -ResourceFiles $resourceFiles;

# Step 6: 打包生成文件
if ($noarchive){
    Write-Host "Skip Archive Zip File";
} else {
    Create-Compress-Archive -SourceItems $archive_AC -DestinationZip $destinationZip_AC;
    Create-Compress-Archive -SourceItems $archive_ANC -DestinationZip $destinationZip_ANC;
    Set-Location -Path "MusyncSaveDecodeCLI";
    Create-Compress-Archive -SourceItems $archive_C -DestinationZip $destinationZip_C;
    Set-Location -Path "../MusyncSaveDecodeNoCLI";
    Create-Compress-Archive -SourceItems $archive_NC -DestinationZip $destinationZip_NC;
    Set-Location -Path "..";
}
Set-Location -Path "..";

# Step 7: 清理生成文件
# Remove-Item -Path "./logs" -Force -Recurse -ErrorAction SilentlyContinue
# Write-Host "已移除目录：./logs" -ForegroundColor Yellow;
# Remove-Item -Path "./musync_data" -Force -Recurse -ErrorAction SilentlyContinue
# Write-Host "已移除目录：./musync_data" -ForegroundColor Yellow;
# Remove-Item -Path "./MusyncSaveDecodeCLI" -Force -Recurse -ErrorAction SilentlyContinue
# Write-Host "已移除目录：./MusyncSaveDecodeCLI" -ForegroundColor Yellow;
# Remove-Item -Path "./MusyncSaveDecodeNoCLI" -Force -Recurse -ErrorAction SilentlyContinue
# Write-Host "已移除目录：./MusyncSaveDecodeNoCLI" -ForegroundColor Yellow;
# Remove-Item -Path "./MusyncSaveDecodeCLI.exe" -Force -ErrorAction SilentlyContinue
# Write-Host "已删除文件：./MusyncSaveDecodeNoCLI" -ForegroundColor Yellow;
# Remove-Item -Path "./MusyncSaveDecodeNoCLI.exe" -Force -ErrorAction SilentlyContinue
# Write-Host "已删除文件：./MusyncSaveDecodeNoCLI" -ForegroundColor Yellow;

# Step 7: 编译启动器
# & g++ -o $path+"Launcher" .\Launcher.cpp $path+$resPath;
# try {
#     # 编译启动器
#     & g++ -o ./MusyncSaveDecode/Launcher Launcher.cpp -I"D:\Program Files\Python3.11\include" -L"D:\Program Files\Python3.11\libs" -lpython311;
#     # 检查编译是否成功
#     if (-not $?) {
#         throw "编译启动器失败！";
#     }
#     Write-Host "启动器编译成功！" -ForegroundColor Green;
# }
# catch {
#     Write-Host "编译启动器时发生错误：$($_.Exception.Message)" -ForegroundColor Red;
#     exit 1;
# }

Write-Host "==== 所有任务完成 ====";
# Read-Host "Input Enter Key to Exit";
