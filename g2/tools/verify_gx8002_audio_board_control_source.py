# SPDX-License-Identifier: MIT
"""Experimental admission of source-derived NationalChip diagnostics."""
import json,re,shutil
from verify_gx8002_audio_board_control import verify as compare,ROOT,sha
from verify_gx8002_logging import check_paths

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);r=compare()
    spans=[(x['package_offset'],x['bytes']) for row in r['functions'] for x in row['stock_occurrences']]
    registry=(ROOT/'tools/build_gx8002_source_candidate.py').read_text()
    for name in set(re.findall(r"'(gx8002-[^']+\.json)'",registry)):
        if name=='gx8002-audio-board-control-source-verification.json':continue
        path=ROOT/'docs/research'/name
        if not path.exists():continue
        other=json.loads(path.read_text())
        for row in other.get('functions',[other]):
            for x in row.get('stock_occurrences',row.get('exact_stock_occurrences',[])):
                off=x.get('package_offset');size=x.get('bytes')
                if off is not None and size is not None and any(off<a+n and a<off+size for a,n in spans):raise ValueError(('Overlap',name))
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-audio-board-control/candidate.elf',output/'audio-board-control.elf')
    r.update(source_admitted=True,hardware_qualified=False,evidence_sha256={n:sha((ROOT/'tools'/n).read_bytes()) for n in ('verify_gx8002_audio_board_control.py','verify_gx8002_audio_board_control_source.py','build_gx8002_audio_board_control.py','execute_gx8002_audio_board_control.py')})
    r['limits'].append('Experimental hybrid only; complete source-only firmware unfinished.')
    return r
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-board-control-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Audio board control source admission passed')
