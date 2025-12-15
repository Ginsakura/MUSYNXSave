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

	PyObject* pModule, * pFunc, * pArgs, * pValue;

	// 获取函数对象
	pFunc = PyObject_GetAttrString(pModule, "Launcher");
	if (pFunc == NULL) {
		PyErr_Print();
		fprintf(stderr, "Failed to get function 'Launcher()'\n");
		Py_DECREF(pModule);
		Py_Finalize();
		return 1;
	}

	//// 创建参数
	//pArgs = PyTuple_Pack(2, PyLong_FromLong(5), PyLong_FromLong(3));
	//if (pArgs == NULL) {
	//	PyErr_Print();
	//	fprintf(stderr, "Failed to create arguments\n");
	//	Py_DECREF(pFunc);
	//	Py_DECREF(pModule);
	//	Py_Finalize();
	//	return 1;
	//}

	// 调用函数
	pValue = PyObject_CallObject(pFunc, nullptr/*pArgs*/);
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

	//PyObject* pModule = PyImport_ImportModule("Launcher");
	//if (!pModule) {
	//	PyErr_Print();
	//	fprintf(stderr, "Failed to load module 'Launcher'\n");
	//	Py_Finalize();
	//	return 1;
	//}

	//PyObject* pClass = PyObject_GetAttrString(pModule, "MyClass");
	//if (!pClass) {
	//	PyErr_Print();
	//	fprintf(stderr, "Failed to get class 'MyClass'\n");
	//	Py_DECREF(pModule);
	//	Py_Finalize();
	//	return 1;
	//}

	//PyObject* pArgs = PyTuple_Pack(1, PyLong_FromLong(10)); // 传递初始化参数
	//PyObject* pInstance = PyObject_CallObject(pClass, pArgs);
	//Py_DECREF(pArgs);

	//if (!pInstance) {
	//	PyErr_Print();
	//	fprintf(stderr, "Failed to create instance of 'MyClass'\n");
	//	Py_DECREF(pClass);
	//	Py_DECREF(pModule);
	//	Py_Finalize();
	//	return 1;
	//}

	//PyObject* pMethod = PyObject_GetAttrString(pInstance, "add");
	//if (!pMethod) {
	//	PyErr_Print();
	//	fprintf(stderr, "Failed to get method 'add'\n");
	//	Py_DECREF(pInstance);
	//	Py_DECREF(pClass);
	//	Py_DECREF(pModule);
	//	Py_Finalize();
	//	return 1;
	//}

	//PyObject* pMethodArgs = PyTuple_Pack(1, PyLong_FromLong(5)); // 传递方法参数
	//PyObject* pValue = PyObject_CallObject(pMethod, pMethodArgs);
	//Py_DECREF(pMethodArgs);

	//if (!pValue) {
	//	PyErr_Print();
	//	fprintf(stderr, "Call to method 'add' failed\n");
	//	Py_DECREF(pMethod);
	//	Py_DECREF(pInstance);
	//	Py_DECREF(pClass);
	//	Py_DECREF(pModule);
	//	Py_Finalize();
	//	return 1;
	//}

	//// 打印结果
	//printf("Result of call: %ld\n", PyLong_AsLong(pValue));
	//Py_DECREF(pValue);
	//Py_DECREF(pMethod);
	//Py_DECREF(pInstance);
	//Py_DECREF(pClass);
	//Py_DECREF(pModule);

	//Py_Finalize();
	//return 0;
}