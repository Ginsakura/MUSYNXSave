#include <iostream>
#include <filesystem>
#include <cstdlib>
#ifdef WIN32
#include <windows.h>  // Windows: GetModuleFileNameW
#include <direct.h>  // Windows: _chdir
#else
#include <unistd.h>  // Linux/macOS: chdir
#endif

namespace fs = std::filesystem;
#define MAX_PATH 260

fs::path getExecutablePath() {
#ifdef WIN32
    wchar_t buffer[MAX_PATH];
    GetModuleFileNameW(nullptr, buffer, MAX_PATH);
    return fs::path(buffer);
#else
    // Linux: /proc/self/exe, macOS: _NSGetExecutablePath
    char buffer[MAX_PATH];
    ssize_t len = readlink("/proc/self/exe", buffer, sizeof(buffer) - 1);
    if (len != -1) {
        buffer[len] = '\0';
        return fs::path(buffer);
    }
    return fs::path();
#endif
}

// 跨平台切换工作目录
void changeToExecutableDir() {
    fs::path exeDir = getExecutablePath().parent_path();
    fs::current_path(exeDir);
    std::cout << "工作目录已切换至: " << fs::current_path() << std::endl;
}

// 跨平台执行Python启动器
int launchPython() {
#ifdef WIN32
    // Windows: 使用 .venv\Scripts\python.exe
    return std::system(".venv/Scripts/python.exe Launcher.py");
#else
    // Linux/macOS: 使用 .venv/bin/python
    return std::system(".venv/bin/python Launcher.py");
#endif
}

// 跨平台暂停
void pauseConsole() {
#ifdef WIN32
    std::system("pause");
#else
    std::cout << "按 Enter 键继续...";
    std::cin.get();
#endif
}

int main(int argc, const char *argv[]) {
    int result = 1;
    try {
        // 切换到程序所在目录
        changeToExecutableDir();
        
        // 启动Python程序
        int result = launchPython();
        if (result != 0) {
            std::cerr << "Python程序执行失败, 返回码: " << result << std::endl;
        }
    } catch (const std::exception& e) {
        std::cerr << "错误: " << e.what() << std::endl;
    }
    // 暂停
    pauseConsole();
    return result;
}