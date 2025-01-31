# �������
$resourceDir = "musync_data/";                          # ��ԴĿ¼
$resPath = "ico.res";                                   # C++ͼ��res��Դ
$rcPath = "ico.rc";                                     # C++ͼ��rc��Դ
$distDir = "MusyncSaveDecode/";                         # ����Ŀ¼
$resourceTargetDir = "MusyncSaveDecode/musync_data/";   # ��Դ�ļ�Ŀ��Ŀ¼
$resourcePath = @("Resources.bin", "songname.json", "songname.update", "Musync.ico"); # ��Դ�ļ�

Clear-Host;
Write-Host "==== ����ʼ ====";

# Step 1: ����ͼ����Դ
Set-Location -Path $resourceDir;
if (-not (Test-Path -Path $resPath)) {
    & windres $rcPath -O coff -o $resPath;
    Write-Host "ͼ����Դ "."$path"."$resPath"." �����ɹ���" -ForegroundColor Green;
} else {
    Write-Host "ͼ����Դ "."$path"."$resPath"." �Ѵ��ڡ�" -ForegroundColor Yellow;
}
Set-Location -Path ..;

# Step 2: �������Ŀ¼
if (-not (Test-Path -Path $distDir)) {
    New-Item -ItemType Directory -Path $distDir;
    Write-Host "Ŀ¼ $distDir �����ɹ���" -ForegroundColor Green;
} else {
    Write-Host "Ŀ¼ $distDir �Ѵ��ڡ�" -ForegroundColor Yellow;
}
# Step 2: ������ԴĿ¼
if (-not (Test-Path -Path $resourceTargetDir)) {
    New-Item -ItemType Directory -Path $resourceTargetDir;
    Write-Host "Ŀ¼ $resourceTargetDir �����ɹ���" -ForegroundColor Green;
} else {
    Write-Host "Ŀ¼ $resourceTargetDir �Ѵ��ڡ�" -ForegroundColor Yellow;
}

# Step 3: ����Cythonģ��
& pyinstaller build.spec --distpath ./MusyncSaveDecode --clean;
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

# Step 4: ������Դ�ļ�
foreach ($file in $resourcePath) {
    $sourceFile = Join-Path -Path $resourceDir -ChildPath $file;
    $destinationFile = Join-Path -Path $resourceTargetDir -ChildPath $file;

    if (Test-Path -Path $sourceFile) {
        Copy-Item -Path $sourceFile -Destination $destinationFile;
        Write-Host "�ļ� $file �ѿ����� $resourceTargetDir"; -ForegroundColor Green;
    } else {
        Write-Host "�ļ� $file �������� $resourceDir������������" -ForegroundColor Orange;
    }
}

# Step 5: ����������
# & g++ -o $path+"Launcher" .\Launcher.cpp $path+$resPath;

try {
    # ����������
    & g++ -o ./MusyncSaveDecode/Launcher Launcher.cpp -I"D:\Program Files\Python3.11\include" -L"D:\Program Files\Python3.11\libs" -lpython311;
    # �������Ƿ�ɹ�
    if (-not $?) {
        throw "����������ʧ�ܣ�";
    }
    Write-Host "����������ɹ���" -ForegroundColor Green;
}
catch {
    Write-Host "����������ʱ��������$($_.Exception.Message)" -ForegroundColor Red;
    exit 1;
}

Write-Host "==== ����������� ====";
