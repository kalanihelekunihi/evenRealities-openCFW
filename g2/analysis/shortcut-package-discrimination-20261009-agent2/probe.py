"""Authenticate original entry bodies and retain bounded GNU comparison evidence."""
from pathlib import Path
import hashlib, json, struct, subprocess
D = Path(__file__).resolve().parent
R = D.parents[2]
sha = lambda b: hashlib.sha256(b).hexdigest()
target = json.loads((R/'g2/workflow/target.json').read_text())
records = []
for row in target['components']:
    data = (R/row['local_payload_path']).read_bytes()
    assert len(data) == row['size'] and sha(data) == row['sha256']
    records.append({'id': row['id'], 'sha256': sha(data), 'size': len(data)})
raw = (R/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
elfpath = R/'g2/analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf'
elf = elfpath.read_bytes()
ph = struct.unpack_from('<8I', elf, 52)
assert ph[0] == 1 and ph[2] == 0x437fe0 and ph[4] == len(raw)
assert elf[ph[1]:ph[1]+len(raw)] == raw
vectors = struct.unpack_from('<16I', raw, 32)
assert vectors[1] == 0x5e4233
spans = [(0x5e4228, 0x5e4232), (0x5e4232,0x5e4242), (0x5e4254,0x5e426c), (0x5e4270, 0x5e4292), (0x5e4294, 0x5e42b2), (0x5e42b4,0x5e42d4)]
bodies = [{'start':hex(a),'end':hex(b),'size':b-a,'sha256':sha(raw[a-0x437fe0:b-0x437fe0])} for a,b in spans]
listing = subprocess.check_output(['/opt/homebrew/bin/arm-none-eabi-objdump','-D','-M','force-thumb','--start-address=0x5e4228','--stop-address=0x5e42dc',str(elfpath)],text=True)
(D/'startup-gnu.txt').write_text(listing)
source = R/'g2/analysis/shortcut-release-archaeology-20261009-agent3/apollo-selected/Device/Source/system_apollo510.c'
startup = source.with_name('startup_apollo510.c')
(D/'receipt.json').write_text(json.dumps({'authenticated_payloads':records,'vector_words':[hex(v) for v in vectors],'bodies':bodies,'system_source_sha256':sha(source.read_bytes()),'startup_source_sha256':sha(startup.read_bytes()),'canonical_edits':False},indent=2)+'\n')
