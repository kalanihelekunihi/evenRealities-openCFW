import subprocess,sys
from pathlib import Path
p=Path(__file__).resolve().parent

for name in ["run-focused.py","run-extra.py","run-closure.py","run-affected.py"]:
 subprocess.run([sys.executable,str(p/name)],check=True)
