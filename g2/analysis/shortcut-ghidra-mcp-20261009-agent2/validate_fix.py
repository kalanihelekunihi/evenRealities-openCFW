"""Compile and evaluate only the private CSKY extension; preserve all receipts."""
from pathlib import Path
import hashlib
import json
import os
import subprocess

root = Path(__file__).resolve().parent
repo = root.parents[2]
installed = Path('/opt/homebrew/Cellar/ghidra/12.1.4/libexec')
private = root / 'private-install'
env = dict(os.environ, JAVA_HOME='/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home')
languages = Path('Ghidra/Processors/CSKY/data/languages')
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

records = []
commands = [
    ('fixed-sleigh.log', [str(private / 'support/sleigh'), str(private / languages / 'csky_v2.slaspec')]),
    ('fixed-evaluated-probe.log', [str(private / 'support/analyzeHeadless'), str(root),
       'PrivateCskyFixedProbeFull', '-process', 'synthetic-movih.bin', '-noanalysis',
       '-scriptPath', str(root), '-postScript', 'ProbeCskyMovih.java']),
]
for log, argv in commands:
    result = subprocess.run(argv, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (root / log).write_text(result.stdout)
    records.append({'argv': argv, 'exit_code': result.returncode, 'log': log,
                    'log_sha256': digest(root / log)})
    print(log, result.returncode)
    if result.returncode or ('probe' in log and 'PROBE_RESULT=a0a00000 EXPECTED=a0a00000' not in result.stdout):
        raise RuntimeError('Probe failed; inspect log')

original_hash = '3dde82aa3bc3bfbb70dc8950705cd0c2a59173e924ee6f92f9005ed880d5210b'
assert digest(installed / languages / '32b_data.sinc') == original_hash
assert digest(repo / 'third-party/tools/ghidra-csky/C-SKY/data/languages/32b_data.sinc') == original_hash
receipt = {
    'status': 'private_fix_verified', 'scope': 'one synthetic movih instruction, no firmware recovery',
    'independent_expected': hex((0xa0a0 * 65536) & 0xffffffff),
    'commands': records,
    'hashes': {str(p): digest(p) for p in [installed / languages / '32b_data.sinc',
        installed / languages / 'csky_v2.sla', private / languages / '32b_data.sinc',
        private / languages / 'csky_v2.sla', root / 'synthetic-movih.bin', root / 'ProbeCskyMovih.java']},
    'limits': ['No authenticated full-image probe or campaign admission',
               'All remaining CSKY instructions and ABI assumptions unvalidated'],
}
(root / 'fixed-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
