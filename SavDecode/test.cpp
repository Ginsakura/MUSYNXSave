//test.cpp
#include <Python.h>
#include <iostream>

static PyObject* PrintHello(PyObject *self, PyObject *args)
{
	std::cout << "Hello, I am form c++" << std::endl;
	Py_INCREF(Py_None);
	return Py_None;
}
//描述方法
static PyMethodDef Methods[] = {
	{"PrintHelloFn", (PyCFunction)(PrintHello), METH_VARARGS, "aSdasdasd"},
	{NULL, NULL}
};
static struct PyModuleDef cModPyDem =
{
    PyModuleDef_HEAD_INIT,
    "PrintHello", /* name of module */
    "",          /* module documentation, may be NULL */
    -1,          /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
    Methods
};


//函数名必须为这样的格式： PyInit_模块名 
PyMODINIT_FUNC PyInit_PrintHello();
PyObject* PyInit_PrintHello()    
{
	PyObject* m = PyModule_Create(&cModPyDem);
    return m;

}


