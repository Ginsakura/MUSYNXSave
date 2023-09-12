from distutils.core import setup, Extension
import os

os.environ["CC"] = "g++"

module1 = Extension(
	name = 'SavDecode',
	language = 'C++',
	extra_compile_args = ['-std=c++20','-fmodules-ts'],
	include_dirs = [r"D:\Program Files\Python3.11\include"],
	libraries = ['python3'],
	library_dirs = [r"D:\Program Files\Python3.11\libs"],
	sources = ['SavDecode.cpp'])

setup (name = 'FastSavDecode',
	version = '1.0',
	author = 'Ginsakura',
	description = 'This is a demo package',
	ext_modules = [module1])