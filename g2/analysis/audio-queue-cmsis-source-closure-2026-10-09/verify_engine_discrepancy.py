from pathlib import Path
import json
import unicorn
D=Path(__file__).resolve().parent
exec((D/'verify.py').read_text().split('for capacity,size in itertools.product')[0])
c=dict(kind='receive',capacity=1,size=4,prefill=1)
continuous=run(False,**c,execution_mode='continuous');stepped=run(False,**c);native=run(True,**c)
assert continuous['state_digest']!=stepped['state_digest']==native['state_digest']
assert len(continuous['extra_payload_writes'])==2 and not stepped['extra_payload_writes'] and not native['extra_payload_writes']
assert [x['pc'] for x in continuous['extra_payload_writes']]==['0x441fba','0x441fec']
(D/'engine-discrepancy.json').write_text(json.dumps({'status':'REPRODUCED_TOOLING_DISCREPANCY','unicorn_version':unicorn.__version__,'elf_sha256':receipt['elf_sha256'],'inputs':c,'original_continuous':continuous,'original_instruction_stepped':stepped,'native_instruction_stepped':native,'interpretation':'Continuous execution unexpectedly carries Thumb IT state from actual memcpy return across stock caller pop and enters queue-unlock with a receive-output pointer. Single instruction execution restores expected payload-only writes and agrees with native source. M33-compatible profile also reproduced the continuous discrepancy in a separate inspection. No hardware defect or emulator-vendor attribution claimed.','limits':'Stepping uses count1 and actual currentPC; no register/flag/byte modifications, helper substitutions, copied opcodes or fabricated returns. All primary comparisons use this mode.'},indent=2)+'\n');print('REPRODUCED continuous/stepped receive discrepancy; stepped original/native agree')
