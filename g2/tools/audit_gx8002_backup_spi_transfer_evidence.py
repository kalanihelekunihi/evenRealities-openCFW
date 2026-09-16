# SPDX-License-Identifier: MIT
"""Check finite backup-transfer reports all refer to the current C candidate."""
import json
from build_gx8002_backup_dw_spi_transfer import ROOT,sha,Elf32

def audit():
    candidate=json.loads((ROOT/'docs/research/gx8002-backup-dw-spi-transfer-candidate.json').read_text())
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_dw_spi_transfer.c'
    assert sha(source.read_bytes())==candidate['source_sha256'] and candidate['fits']
    elf=Elf32((ROOT/'build/gx8002-backup-dw-spi-transfer/dw-spi-quick-transfer-candidate.elf').read_bytes(),'transfer')
    body=elf.contents(next(s for s in elf.sections if s['name']=='.text'))
    assert sha(body)==candidate['compiled_sha256']
    counts={}
    for name,expected in [('lifecycle',4),('alignment',280),('tx',160),('rx',160),('message',270)]:
        path=ROOT/f'docs/research/gx8002-backup-spi-transfer-{name}.json'
        report=json.loads(path.read_text())
        assert report['candidate']==candidate and report['decoded_cases']==expected
        counts[name]={'cases':expected,'report_sha256':sha(path.read_bytes())}
    result={'candidate':candidate,'reports':counts,'total_cases':sum(r['cases'] for r in counts.values()),'source_admitted':False,'limits':['This audit verifies evidence consistency, not new executions. Finite buffer/list/FIFO models remain bounded.','No malformed/concurrent metadata, unsupported widths, physical timing or whole-firmware qualification.']}
    (ROOT/'docs/research/gx8002-backup-spi-transfer-evidence.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(audit()['total_cases'])
