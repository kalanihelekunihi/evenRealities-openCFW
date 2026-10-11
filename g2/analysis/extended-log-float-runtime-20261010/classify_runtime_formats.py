"""Classify the 12 nonliteral stock logger format slots from disassembly."""
import json,re
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
inventory=json.loads((HERE.parent/'extended-log-caller-inventory-20261010/inventory.json').read_text())
lines=(ROOT/'g2/analysis/coverage-audit-parallel-2026-10-09/TDK-TRANSPORT-MAIN-DISASSEMBLY.txt').read_text().splitlines()
by_addr={int(m.group(1),16):i for i,line in enumerate(lines)
         if (m:=re.match(r'\s*([0-9a-f]+):',line))}
unresolved=[int(site['call'],16) for site in inventory['sites'] if site['format'] is None]
assert len(unresolved)==12
classified=[]
for addr in unresolved:
    i=by_addr[addr];window='\n'.join(lines[i-20:i])
    if 'str.w\tr8, [sp, #4]' in window:
        kind='r8 entry parameter of 0x56d478'
    elif re.search(r'add\s+r0, sp, #8|add\s+r0, sp, #8',window) and re.search(r'str\s+r0, \[sp, #4\]',window):
        kind='caller stack buffer at sp+8'
    else:raise AssertionError(hex(addr))
    classified.append({'call':hex(addr),'format_origin':kind})
assert sum('r8' in s['format_origin'] for s in classified)==4
assert sum('stack' in s['format_origin'] for s in classified)==8
wrapper_callers=[hex(int(re.match(r'\s*([0-9a-f]+):',line).group(1),16))
                 for line in lines if re.search(r'\bbl\s+0x56d478\b',line)]
assert len(wrapper_callers)==30
result={'status':'PASS','runtime_format_sites':classified,
        'r8_parameter_sites':4,'stack_hex_buffer_sites':8,
        'direct_calls_to_wrapper_0x56d478':len(wrapper_callers),
        'wrapper_callers':wrapper_callers,
        'limit':'Static syntactic origin only. Actual r8 values and every stack buffer byte/terminator require caller/producer execution; no format semantics inferred.'}
(HERE/'runtime_format_classification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','r8_sites':4,'stack_sites':8,'wrapper_callers':len(wrapper_callers)}))
