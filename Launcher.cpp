#include <iostream>
#include <windows.h>
#include <Python.h>

//g++ -o MusyncSaveDecode/Launcher Launcher.cpp -I"C:\Python3x\include" -L"C:\Python3x\libs" -lpython3x
int main() {
	// 加载 python3.x.dll
	HMODULE hModule = LoadLibrary("./python311.dll"); // 替换为实际的版本号
	if (!hModule) {
		fprintf(stderr, "Failed to load python3.x.dll\n");
		return 1;
	}

	// 加载模块
	Py_Initialize();
	if (!Py_IsInitialized()) {
		fprintf(stderr, "Failed to initialize Python interpreter\n");
		return 1;
	}

	PyObject* pModule = PyImport_ImportModule("Launcher");
	if (!pModule) {
		PyErr_Print();
		fprintf(stderr, "Failed to load module 'Launcher'\n");
		Py_Finalize();
		return 1;
	}

	PyObject* pFunc = PyObject_GetAttrString(pModule, "Launcher");
	if (!pFunc) {
		PyErr_Print();
		fprintf(stderr, "Failed to get function 'Launcher()'\n");
		Py_DECREF(pModule);
		Py_Finalize();
		return 1;
	}

	// 调用函数
	PyObject* pValue = PyObject_CallObject(pFunc, nullptr);
	//Py_DECREF(pArgs);

	if (pValue == NULL) {
		PyErr_Print();
		fprintf(stderr, "Call failed\n");
		Py_DECREF(pFunc);
		Py_DECREF(pModule);
		Py_Finalize();
		return 1;
	}

	// 检查返回值是否为 None
	if (pValue == Py_None) {
		printf("Result of call: None\n");
	}
	else {
		// 打印结果
		printf("Result of call: %ld\n", PyLong_AsLong(pValue));
	}
	Py_DECREF(pValue);
	Py_DECREF(pFunc);
	Py_DECREF(pModule);

	Py_Finalize();
	system("pause");
	return 0;
}