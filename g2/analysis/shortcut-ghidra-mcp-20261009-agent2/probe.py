"""Private synthetic processor probe; never reads or changes firmware."""
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parent
binary = root / 'synthetic-movih.bin'
binary.write_bytes(bytes.fromhex('23eaa0a0'))
fixed = '--fixed' in sys.argv
launcher = root / 'private-install/support/analyzeHeadless' if fixed else Path('/opt/homebrew/Cellar/ghidra/12.1.4/libexec/support/analyzeHeadless')
argv = [
    str(launcher),
    str(root), 'PrivateCskyFixedProbeFull' if fixed else 'PrivateCskyProbe', '-import', str(binary), '-loader', 'BinaryLoader',
    '-processor', 'CSKY_V2:LE:32:default', '-noanalysis', '-scriptPath', str(root),
    '-postScript', 'ProbeCskyMovih.java',
]
result = subprocess.run(argv, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
(root / ('fixed-probe.log' if fixed else 'probe.log')).write_text(result.stdout)
print('exit_code=' + str(result.returncode))
print('\n'.join(line for line in result.stdout.splitlines() if 'PROBE_' in line or 'ERROR' in line))
