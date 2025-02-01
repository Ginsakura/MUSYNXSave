# ���庯��
# ����ͼ����Դ
function BuildIcon{
    <#
    .SYNOPSIS
    ����C/C++ͼ����Դ
    .DESCRIPTION
    ����C/C++ͼ����Դ
    .PARAMETER None
    �޲���
    .EXAMPLE
    BuildIcon
    .NOTES
    �ṩ������Ҫ��Ϣ����ע�����������������֪����ȡ�
    .INPUTS
    �����������Խ��յ��������ͣ�ͨ������֧�ֹܵ�����ĺ�����
    .OUTPUTS
    ����������������ͺ����ݡ�
    #>
    $resPath = "ico.res";   # C++ͼ��res��Դ
    $rcPath = "ico.rc";     # C++ͼ��rc��Դ
    Set-Location -Path "musync_data/";
    if (-not (Test-Path -Path $resPath)) {
        & windres $rcPath -O coff -o $resPath;
        Write-Host "ͼ����Դ ${path}${resPath} �����ɹ���" -ForegroundColor Green;
    } else {
        Write-Host "ͼ����Դ ${path}${resPath} �Ѵ��ڡ�" -ForegroundColor Yellow;
    }
    Set-Location -Path ..;
}

# Ŀ¼���
function CheckDir {
    <#
    .SYNOPSIS
    ���Ŀ¼�Ƿ���ڣ�����������򴴽���Ŀ¼��

    .DESCRIPTION
    �˺������ָ����Ŀ¼�Ƿ���ڡ����Ŀ¼�����ڣ���������Ŀ¼�������سɹ���Ϣ��
    ���Ŀ¼�Ѵ��ڣ��򷵻���Ӧ����ʾ��Ϣ��

    .PARAMETER Dir
    ָ��Ҫ����Ŀ¼·����

    .EXAMPLE
    CheckDir -Dir "C:\tempdir"
    ���Ŀ¼ "C:\tempdir" �Ƿ���ڣ�����������򴴽���Ŀ¼��

    .EXAMPLE
    "C:\tempdir" | CheckDir
    ͨ���ܵ�����Ŀ¼·�������Ŀ¼�Ƿ���ڣ�����������򴴽���Ŀ¼��

    .NOTES
    �˺�����������Ҫȷ��Ŀ¼���ڵĳ��������Ŀ¼·����Ч����������Ƿ��ַ��������ܻᵼ�´���

    .INPUTS
    �˺��������ַ������͵�Ŀ¼·����Ϊ���롣֧��ͨ���ܵ����롣

    .OUTPUTS
    �˺����������κ����������ͨ�� Write-Host ���״̬��Ϣ��
    #>
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [string]$Dir
    )

    process {
        if (-not (Test-Path -Path $Dir)) {
            New-Item -ItemType Directory -Path $Dir -ErrorAction Stop | Out-Null
            Write-Host "Ŀ¼ ${Dir} �����ɹ���" -ForegroundColor Green
        } else {
            Write-Host "Ŀ¼ ${Dir} �Ѵ��ڡ�" -ForegroundColor Yellow
        }
    }
}

# ������Դ�ļ�
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
    Copy-Resources -SourceDirectory "musync_data" -TargetDirectory "MusyncSaveDecode/musync_data" -ResourceFiles @("Resources.bin", "songname.json", "songname.update", "Musync.ico")
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
            Write-Host "�ļ� ${file} �ѿ����� ${TargetDirectory}" -ForegroundColor Green
        } else {
            Write-Host "�ļ� ${file} �������� ${SourceDirectory}������������" -ForegroundColor Yellow
        }
    }
}

# ����������
function Create-Archive {
    <#
    .SYNOPSIS
    ����ZIP�ļ�����ָ�����ļ����ļ��д����

    .DESCRIPTION
    �˺��������ṩ���ļ��б��Ŀ��·����ʹ��Compress-Archive�����ZIP�ļ���

    .PARAMETER SourceItems
    Ҫ������ļ����ļ���·�����顣

    .PARAMETER DestinationZip
    �����ZIP�ļ�·����

    .EXAMPLE
    Create-Archive -SourceItems @("logs", "musync_data", "MusyncSaveDecodeCLI.exe") -DestinationZip "MusyncSaveDecode_WithConsole_1.0.0_AllInOne.zip"
    #>
    param (
        [Parameter(Mandatory = $true)]
        [string[]]$SourceItems,

        [Parameter(Mandatory = $true)]
        [string]$DestinationZip
    )

    # ȷ��Ŀ��ZIP�ļ���Ŀ¼����
    # $destinationDir = [System.IO.Path]::GetDirectoryName($DestinationZip)
    # CheckDir -Dir $DestinationZip;

    # ����ļ����ļ���
    try {
        Compress-Archive -Path $SourceItems -DestinationPath $DestinationZip -Force
        Write-Host "����ɹ�������ļ���$DestinationZip" -ForegroundColor Green
    }
    catch {
        Write-Host "���ʧ�ܣ�$($_.Exception.Message)" -ForegroundColor Red
    }
}

# �������
$isPreRelease = python -c "import Version;print(Version.isPreRelease)";
$isPreReleaseBool = [bool]::Parse($isPreRelease);
# ���ݲ���ֵ���ò�ͬ�����Բ���ֵ�� $version
if ($isPreReleaseBool) {
    $version = py -c "import Version; print(Version.preVersion)";
} else {
    $version = py -c "import Version; print(Version.version)";
}
$resourceFiles = @("Resources.bin", "songname.json", "songname.update", "Musync.ico");  # ��Դ�ļ�
$archive_AC = @("logs", "musync_data", "MusyncSaveDecodeCLI.exe");                     # CLI all in one archive files
$archive_ANC = @("logs", "musync_data", "MusyncSaveDecodeNoCLI.exe");                  # NoCLI all in one archive files
$archive_C = @("logs", "musync_data", "_internal", "MusyncSaveDecodeCLI.exe");
$archive_NC = @("logs", "musync_data", "_internal", "MusyncSaveDecodeNoCLI.exe");
$destinationZip_AC = "Archive/MusyncSaveDecode_WithConsole_${version}_AllInOne.zip"
$destinationZip_ANC = "Archive/MusyncSaveDecode_NoConsole_${version}_AllInOne.zip"
$destinationZip_C = "../Archive/MusyncSaveDecode_WithConsole_${version}.zip";
$destinationZip_NC = "../Archive/MusyncSaveDecode_NoConsole_${version}.zip";

Clear-Host;
Write-Host "==== ����ʼ ====";

# Step 0: ��������Ŀ¼
# Remove-Item -Path "./MusyncSaveDecode" -Force -Recurse -ErrorAction SilentlyContinue;
# Write-Host "��ɾ��Ŀ¼��./MusyncSaveDecode" -ForegroundColor Yellow;

# Step 1: ����ͼ����Դ
BuildIcon;

# Step 2: ��鹹��Ŀ¼
# CheckDir -Dir "MusyncSaveDecode/";
CheckDir -Dir "MusyncSaveDecode/Archive/";
# CheckDir -Dir "MusyncSaveDecode/MusyncSaveDecodeCLI/";
# CheckDir -Dir "MusyncSaveDecode/MusyncSaveDecodeNoCLI/";

# Step 3: Pyinstaller����
& pyinstaller "buildLauncher.spec" --distpath "./MusyncSaveDecode" --clean;
if ($?) {
    Write-Host "Pyinstaller����ɹ���" -ForegroundColor Green;
} else {
    Write-Host "Pyinstaller����ʧ�ܣ�" -ForegroundColor Red;
    exit 1;
}
# Write-Host "���ڱ���Cythonģ�� ..."
# & python setup.py build_ext --inplace
# if ($?) {
#     Write-Host "Cythonģ�����ɹ���" -ForegroundColor Green;
# } else {
#     Write-Host "Cythonģ�����ʧ�ܣ�" -ForegroundColor Red;
#     exit 1;
# }

# Step 4: �����ԴĿ¼
Set-Location -Path "MusyncSaveDecode";
CheckDir -Dir "logs/";
CheckDir -Dir "musync_data/";
CheckDir -Dir "MusyncSaveDecodeCLI/musync_data/";
CheckDir -Dir "MusyncSaveDecodeCLI/logs/";
CheckDir -Dir "MusyncSaveDecodeNoCLI/musync_data/";
CheckDir -Dir "MusyncSaveDecodeNoCLI/logs/";

# Step 5: ������Դ�ļ�
Copy-Resources -SourceDirectory "../musync_data" -TargetDirectory "musync_data" -ResourceFiles $resourceFiles;
Copy-Resources -SourceDirectory "../musync_data" -TargetDirectory "MusyncSaveDecodeCLI/musync_data/" -ResourceFiles $resourceFiles;
Copy-Resources -SourceDirectory "../musync_data" -TargetDirectory "MusyncSaveDecodeNoCLI/musync_data/" -ResourceFiles $resourceFiles;

# Step 6: ��������ļ�
Create-Archive -SourceItems $archive_AC -DestinationZip $destinationZip_AC;
Create-Archive -SourceItems $archive_ANC -DestinationZip $destinationZip_ANC;
Set-Location -Path "MusyncSaveDecodeCLI";
Create-Archive -SourceItems $archive_C -DestinationZip $destinationZip_C;
Set-Location -Path "../MusyncSaveDecodeNoCLI";
Create-Archive -SourceItems $archive_NC -DestinationZip $destinationZip_NC;
Set-Location -Path "..";

# Step 7: ���������ļ�
Remove-Item -Path "./logs" -Force -Recurse -ErrorAction SilentlyContinue
Write-Host "���Ƴ�Ŀ¼��./logs" -ForegroundColor Yellow;
Remove-Item -Path "./musync_data" -Force -Recurse -ErrorAction SilentlyContinue
Write-Host "���Ƴ�Ŀ¼��./musync_data" -ForegroundColor Yellow;
Remove-Item -Path "./MusyncSaveDecodeCLI" -Force -Recurse -ErrorAction SilentlyContinue
Write-Host "���Ƴ�Ŀ¼��./MusyncSaveDecodeCLI" -ForegroundColor Yellow;
Remove-Item -Path "./MusyncSaveDecodeNoCLI" -Force -Recurse -ErrorAction SilentlyContinue
Write-Host "���Ƴ�Ŀ¼��./MusyncSaveDecodeNoCLI" -ForegroundColor Yellow;
Remove-Item -Path "./MusyncSaveDecodeCLI.exe" -Force -ErrorAction SilentlyContinue
Write-Host "��ɾ���ļ���./MusyncSaveDecodeNoCLI" -ForegroundColor Yellow;
Remove-Item -Path "./MusyncSaveDecodeNoCLI.exe" -Force -ErrorAction SilentlyContinue
Write-Host "��ɾ���ļ���./MusyncSaveDecodeNoCLI" -ForegroundColor Yellow;

# Step 7: ����������
# & g++ -o $path+"Launcher" .\Launcher.cpp $path+$resPath;
# try {
#     # ����������
#     & g++ -o ./MusyncSaveDecode/Launcher Launcher.cpp -I"D:\Program Files\Python3.11\include" -L"D:\Program Files\Python3.11\libs" -lpython311;
#     # �������Ƿ�ɹ�
#     if (-not $?) {
#         throw "����������ʧ�ܣ�";
#     }
#     Write-Host "����������ɹ���" -ForegroundColor Green;
# }
# catch {
#     Write-Host "����������ʱ��������$($_.Exception.Message)" -ForegroundColor Red;
#     exit 1;
# }

Write-Host "==== ����������� ====";
