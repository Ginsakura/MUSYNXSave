# setup.py
from setuptools import setup, Extension
from Cython.Build import cythonize
import os

# 确保输出目录存在
output_dir = "./MusyncSaveDecode"
os.makedirs(output_dir, exist_ok=True)
# 遍历目录中的文件
for filename in os.listdir(output_dir):
	if filename.endswith(".pyd"):
		file_path = os.path.join(output_dir, filename)
		os.remove(file_path)
		print(f"Deleted: {file_path}")

ext_modules = [
	Extension("Launcher",
			sources=["Launcher.py"],
			include_dirs=["D:\\Program Files\\Python3.11\\include"],
			library_dirs=["D:\\Program Files\\Python3.11\\libs"],
			libraries=["python311"]
			),
	Extension("MainWindow",
			sources=["MainWindow.py"],
			include_dirs=["D:\\Program Files\\Python3.11\\include"],
			library_dirs=["D:\\Program Files\\Python3.11\\libs"],
			libraries=["python311"]
			),
	Extension("Difficulty_ScoreAnalyze",
			sources=["Difficulty_ScoreAnalyze.py"],
			include_dirs=["D:\\Program Files\\Python3.11\\include"],
			library_dirs=["D:\\Program Files\\Python3.11\\libs"],
			libraries=["python311"]
			),
	Extension("HitDelay",
			sources=["HitDelay.py"],
			include_dirs=["D:\\Program Files\\Python3.11\\include"],
			library_dirs=["D:\\Program Files\\Python3.11\\libs"],
			libraries=["python311"]
			),
	Extension("MusyncSavDecode",
			sources=["MusyncSavDecode.py"],
			include_dirs=["D:\\Program Files\\Python3.11\\include"],
			library_dirs=["D:\\Program Files\\Python3.11\\libs"],
			libraries=["python311"]
			),
	Extension("Resources",
			sources=["Resources.py"],
			include_dirs=["D:\\Program Files\\Python3.11\\include"],
			library_dirs=["D:\\Program Files\\Python3.11\\libs"],
			libraries=["python311"]
			),
	Extension("Toolkit",
			sources=["Toolkit.py"],
			include_dirs=["D:\\Program Files\\Python3.11\\include"],
			library_dirs=["D:\\Program Files\\Python3.11\\libs"],
			libraries=["python311"]
			),
]

setup(
	name='MusyncSaveDecode',
	version='2.0.0',
	description='Musync Save Decode',
	ext_modules=cythonize(ext_modules, build_dir=output_dir, language_level = "3"),
	script_args=['build_ext', '--inplace'],
)