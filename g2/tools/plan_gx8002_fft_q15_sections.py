# SPDX-License-Identifier: MIT
"""Find a whole-section packing with fixed public entries and copy trampoline."""
import json
from build_gx8002_backup_cfft import ROOT,sha

def plan():
    path=ROOT/'docs/research/gx8002-fft-q15-lto-materialized.json';r=json.loads(path.read_text())
    items=[s.copy() for s in r['sections'] if s['flags']&4]
    fixed={'rfft':0x478a4,'shift_q15':0x47a00,'maxabs_q15':0x47a74,'fill_q15':0x47aec}
    reserved=[]
    for name,start in fixed.items():
        section=next(s for s in items if s['section']=='.text.open_cfw_gx8002_backup_'+name);items.remove(section)
        reserved.append({'section':section['section'],'offset':start,'size':section['size']})
    # Four bytes reserved for a source-authored branch at the copy public entry.
    ends={r['section']:r['offset']+r['size'] for r in reserved}
    def end(name):return ends['.text.open_cfw_gx8002_backup_'+name]
    ranges=[(end('rfft'),0x47a00),(end('shift_q15'),0x47a74),(end('maxabs_q15'),0x47ac0),(0x47ac4,0x47aec),(end('fill_q15'),0x4818a),(0x4cd34,0x4cf14)]
    positions=[a for a,b in ranges];bins=[[] for _ in ranges];items.sort(key=lambda s:-s['size']);failed=set()
    def search(index):
        if index==len(items):return True
        key=(index,tuple(positions))
        if key in failed:return False
        item=items[index]
        for n,(lo,hi) in enumerate(ranges):
            old=positions[n];start=(old+item['align']-1)&-item['align']
            if start+item['size']>hi:continue
            positions[n]=start+item['size'];bins[n].append({'section':item['section'],'offset':start,'size':item['size']})
            if search(index+1):return True
            bins[n].pop();positions[n]=old
        failed.add(key);return False
    fits=search(0)
    result={'materialized_report_sha256':sha(path.read_bytes()),'fits':fits,'fixed':reserved,'copy_entry_branch_reservation':[0x47ac0,4],'ranges':ranges,'placements':bins if fits else [],'source_admitted':False,'limits':['Combinatorial placement only. Branch encoding, relink, descriptor addresses, references and loader effects not yet qualified.']}
    (ROOT/'docs/research/gx8002-fft-q15-section-plan.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(plan()['fits'])
