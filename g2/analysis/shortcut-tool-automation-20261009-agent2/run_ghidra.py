"""Replay private bounded Ghidra export and preserve tool/input receipts."""
from pathlib import Path
import os,subprocess,json,hashlib
D=Path(__file__).resolve().parent
G=Path('/opt/homebrew/Cellar/ghidra/12.1.4/libexec')
input_args=['-process','private-main-analysis-only.elf'] if (D/'PrivateTlsf.gpr').exists() else ['-import',str(D/'private-main-analysis-only.elf')]
args=[str(G/'support/analyzeHeadless'),str(D),'PrivateTlsf']+input_args+['-noanalysis','-scriptPath',str(D),'-postScript','BoundedTlsf.java',str(D)]
env=os.environ.copy();env['JAVA_HOME']='/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home'
p=subprocess.run(args,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
(D/'ghidra.log').write_text(p.stdout)
assert p.returncode==0 and 'BOUNDED_BODY 004d0524' in p.stdout and 'BOUNDED_BODY 004cffc2' in p.stdout
paths=[D/'BoundedTlsf.java',D/'private-main-analysis-only.elf',D/'4d0524-ghidra-raw.c',D/'4cffc2-ghidra-raw.c',G/'Ghidra/Processors/ARM/data/languages/ARM8_le.sla',G/'Ghidra/Processors/ARM/data/languages/ARM.cspec',G/'Ghidra/Processors/ARM/data/languages/ARM.ldefs',G/'Ghidra/Processors/ARM/data/languages/ARMt.pspec']
hashes={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in paths}
(D/'ghidra-receipt.json').write_text(json.dumps({'argv':args,'exit_code':p.returncode,'version':'12.1.4','language':'ARM:LE:32:v8','cspec':'default','thumb_context':'TMode=1 on exact bounded ranges','hashes':hashes,'options':'noanalysis; bounded DisassembleCommand; private project only','note':'ARM v8 is chosen by the analysis ELF importer, not evidence of firmware hardware architecture.'},indent=2)+'\n')
print('PASS private Ghidra exports and hashes')
