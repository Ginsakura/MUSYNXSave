# Step 0: 检查参数列表
[CmdletBinding()]
param (
    [switch]$noarchive
)

# 定义函数
# 构建图标资源
function BuildIcon{
    <#
    .SYNOPSIS
    构建C/C++图标资源
    .DESCRIPTION
    构建C/C++图标资源
    .PARAMETER None
    无参数
    .EXAMPLE
    BuildIcon
    .NOTES
    提供其他重要信息，如注意事项、限制条件、已知问题等。
    .INPUTS
    描述函数可以接收的输入类型，通常用于支持管道输入的函数。
    .OUTPUTS
    描述函数的输出类型和内容。
    #>
    $resPath = "ico.res";   # C++图标res资源
    $rcPath = "ico.rc";     # C++图标rc资源
    Set-Location -Path "musync_data/";
    if (-not (Test-Path -Path $resPath)) {
        & windres $rcPath -O coff -o $resPath;
        Write-Host "图标资源 ${path}${resPath} 创建成功！" -ForegroundColor Green;
    } else {
        Write-Host "图标资源 ${path}${resPath} 已存在。" -ForegroundColor Yellow;
    }
    Set-Location -Path ..;
}

# 目录检查
function CheckDir {
    <#
    .SYNOPSIS
    检查目录是否存在，如果不存在则创建该目录。

    .DESCRIPTION
    此函数检查指定的目录是否存在。如果目录不存在，将创建该目录，并返回成功消息。
    如果目录已存在，则返回相应的提示消息。

    .PARAMETER Dir
    指定要检查的目录路径。

    .EXAMPLE
    CheckDir -Dir "C:\tempdir"
    检查目录 "C:\tempdir" 是否存在，如果不存在则创建该目录。

    .EXAMPLE
    "C:\tempdir" | CheckDir
    通过管道输入目录路径，检查目录是否存在，如果不存在则创建该目录。

    .NOTES
    此函数适用于需要确保目录存在的场景。如果目录路径无效（例如包含非法字符），可能会导致错误。

    .INPUTS
    此函数接受字符串类型的目录路径作为输入。支持通过管道输入。

    .OUTPUTS
    此函数不返回任何输出，但会通过 Write-Host 输出状态消息。
    #>
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [string]$Dir
    )

    process {
        if (-not (Test-Path -Path $Dir)) {
            New-Item -ItemType Directory -Path $Dir -ErrorAction Stop | Out-Null
            Write-Host "目录 ${Dir} 创建成功！" -ForegroundColor Green
        } else {
            Write-Host "目录 ${Dir} 已存在。" -ForegroundColor Yellow
        }
    }
}

# 复制资源文件
function Copy-Resources {
    <#
    .SYNOPSIS
    Copies specified resources from a source directory to a target directory.

    .DESCRIPTION
    This function takes a list of resource files, copies them from the source directory to the target directory,
    and provides feedback on the success or failure of each copy operation.

    .PARAMETER SourceDirectory
    The directory containing the source files to be copied.

    .PARAMETER TargetDirectory
    The directory where the files will be copied to.

    .PARAMETER ResourceFiles
    An array of file names to be copied.

    .EXAMPLE
    Copy-Resources -SourceDirectory "musync_data" -TargetDirectory "MusyncSaveDecode/musync_data" -ResourceFiles @("Resources.bin", "songname.json", "songname.ver", "Musync.ico")
    #>
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
            Write-Host "文件 ${file} 已拷贝到 ${TargetDirectory}" -ForegroundColor Green
        } else {
            Write-Host "文件 ${file} 不存在于 ${SourceDirectory}，跳过拷贝。" -ForegroundColor Yellow
        }
    }
}

# 定义打包函数
function Create-Archive {
    <#
    .SYNOPSIS
    创建ZIP文件，将指定的文件和文件夹打包。

    .DESCRIPTION
    此函数根据提供的文件列表和目标路径，使用Compress-Archive命令创建ZIP文件。

    .PARAMETER SourceItems
    要打包的文件和文件夹路径数组。

    .PARAMETER DestinationZip
    输出的ZIP文件路径。

    .EXAMPLE
    Create-Archive -SourceItems @("logs", "musync_data", "MusyncSaveDecodeCLI.exe") -DestinationZip "MusyncSaveDecode_WithConsole_1.0.0_AllInOne.zip"
    #>
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
        Write-Host "打包成功！输出文件：${DestinationZip}" -ForegroundColor Green
    }
    catch {
        Write-Host "打包失败：$($_.Exception.Message)" -ForegroundColor Red
    }
}

# 定义变量
$isPreRelease = python -c "import Version;print(Version.isPreRelease)";
$isPreReleaseBool = [bool]::Parse($isPreRelease);
# 根据布尔值调用不同的属性并赋值给 $version
if ($isPreReleaseBool) {
    $version = py -c "import Version; print(Version.preVersion)";
} else {
    $version = py -c "import Version; print(Version.version)";
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

# Step 3: Pyinstaller编译
& pyinstaller "buildLauncher.spec" --distpath "./MusyncSaveDecode" --clean;
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
    Create-Archive -SourceItems $archive_AC -DestinationZip $destinationZip_AC;
    Create-Archive -SourceItems $archive_ANC -DestinationZip $destinationZip_ANC;
    Set-Location -Path "MusyncSaveDecodeCLI";
    Create-Archive -SourceItems $archive_C -DestinationZip $destinationZip_C;
    Set-Location -Path "../MusyncSaveDecodeNoCLI";
    Create-Archive -SourceItems $archive_NC -DestinationZip $destinationZip_NC;
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
